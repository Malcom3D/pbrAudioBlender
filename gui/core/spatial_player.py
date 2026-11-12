# Copyright (C) 2025 Malcom3D <malcom3d.gpl@gmail.com>
#
# This file is part of pbrAudio.
#
# pbrAudio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pbrAudio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pbrAudio.  If not, see <https://www.gnu.org/licenses/>.
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Thin wrapper: pbrAudioStorage → numpy → aud with a live (animated) position.

Why live position: the object we anchor to can be animated. `aud` only
lets us set position once, so we spin a small timer that re-issues
`handle.location = ...` at ~60 Hz while playing — same trick Blender's
own sequencer overlay uses.
"""

import time
import bpy
import numpy as np
import aud

class SpatialPlayer:
    _instance = None

    def __init__(self):
        self._device = None
        self._handle = None
        self._timer_key = None
        self._anchor_name = None

        self._playing = False

    @classmethod
    def get(cls) -> "SpatialPlayer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -- public ------------------------------------------------------
    @property
    def playing(self) -> bool:
        return self._playing

    def play(self, audio: np.ndarray, sample_rate: int, anchor_object_name: str | None):
        self.stop()
        audio = np.ascontiguousarray(audio, dtype=np.float32)
        # aud wants shape (samples, channels)
        if audio.ndim == 1:
            audio = audio.reshape(-1, 1)
        else:
            audio = audio.T

        self._device = aud.Device()
        self._device.distance_model = aud.DISTANCE_MODEL_INVERSE_CLAMPED

        sound = aud.Sound.buffer(audio, sample_rate)
        self._handle = self._device.play(sound)
        self._handle.volume = 1.0

        self._anchor_name = anchor_object_name
        self._apply_position(anchor_object_name)

        # ticker: refresh position while the handle is alive
        self._playing = True
        self._timer_key = bpy.app.timers.register(self._tick, first_interval=1.0 / 60.0, persistent=True)

        # signal the button to redraw
        _notify_preview_state(True)

    def stop(self):
        if self._timer_key is not None:
            try:
                bpy.app.timers.unregister(self._timer_key)
            except Exception:
                pass
            self._timer_key = None

        if self._handle is not None:
            try:
                self._handle.stop()
            except Exception:
                pass
            self._handle = None

        if self._device is not None:
            try:
                self._device.stopAll()
                self._device = None
            except Exception:
                pass

        was = self._playing
        self._playing = False
        if was:
            _notify_preview_state(False)

    # -- internals ---------------------------------------------------
    def _tick(self):
        if self._handle is None:
            self._playing = False
            return None  # unregister

        # If the sound finished on its own (aud handle.status -> True)
        if getattr(self._handle, "status", False):
            self.stop()
            return None

        self._apply_position(self._anchor_name)
        return 1.0 / 60.0  # reschedule

    def _apply_position(self, name):
        if not name:
            return
        obj = bpy.data.objects.get(name)
        if obj is None:
            return
        loc = obj.matrix_world.translation
        try:
            self._handle.location = (loc.x, loc.y, loc.z)
        except Exception:
            # older aud builds require a tuple; already is
            pass

def _notify_preview_state(playing: bool):
    """Push the state into the scene + redraw any 3D viewports."""
    scene = bpy.context.scene
    if hasattr(scene, "pbraudio"):
        scene.pbraudio.preview_playing = playing
    screen = bpy.context.screen
    if screen:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
