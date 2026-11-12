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
Play/stop button for the currently-browsed pbrAudioStorage signal.

Delegates playback to pbraudio.playback_toggle, which uses python `aud`
with spatial position taken from the active selected object.
"""

import blf
import gpu
from gpu_extras.batch import batch_for_shader

from .widget_base import ViewportWidget

BG_IDLE   = (0.15, 0.15, 0.15, 0.85)
BG_HOVER  = (0.25, 0.35, 0.55, 0.95)
BG_ACTIVE = (0.55, 0.15, 0.15, 0.95)
FG_TEXT   = (1.0, 1.0, 1.0, 1.0)

BASE_FONT_SIZE = 14

class PlaybackWidget(ViewportWidget):
    name = "playback"

    def __init__(self, spec_provider):
        """
        spec_provider : callable() -> tuple(collection, engine, obj_idx, track, signal) | None
            Called at click time; returns what to play.
        """
        super().__init__()
        self._provider = spec_provider
        self._hits: dict[int, dict] = {}

    def _state_key(self):
        return "playing"

    def _is_playing(self) -> bool:
        import bpy
        scene = getattr(bpy.context, "scene", None)
        if scene is None or not hasattr(scene, "pbraudio"):
            return False
        return bool(getattr(scene.pbraudio, "preview_playing", False))

    def draw(self, ctx, region, rv3d, x, y, w, h):
        font_id = 0
        blf.size(font_id, BASE_FONT_SIZE)

        st = self.state(region)
        hover = st.get("hover", False)
        playing = self._is_playing()

        if playing:
            bg = BG_ACTIVE
        elif hover:
            bg = BG_HOVER
        else:
            bg = BG_IDLE

        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        shader.uniform_float("color", bg)
        _rect_fill(shader, x, y, w, h)
        gpu.state.blend_set('NONE')

        text = "■  Stop" if playing else "▶  Play"
        tw, th = blf.dimensions(font_id, text)
        blf.color(font_id, *FG_TEXT)
        blf.position(font_id, x + (w - tw) / 2, y + (h - th) / 2, 0)
        blf.draw(font_id, text)

        self._hits[region.as_pointer()] = {
            "x": x, "y": y, "w": w, "h": h, "hover": hover,
        }

    def hit(self, region, mx, my) -> bool:
        r = self._hits.get(region.as_pointer())
        return bool(r and r["x"] <= mx <= r["x"] + r["w"] and
                    r["y"] <= my <= r["y"] + r["h"])

    def on_event(self, ctx, region, event) -> bool:
        r = self._hits.get(region.as_pointer())
        if r is None:
            return False
        if event.type not in {"MOUSEMOVE", "LEFTMOUSE"}:
            return False

        mx, my = event.mouse_region_x, event.mouse_region_y
        on = (r["x"] <= mx <= r["x"] + r["w"] and
              r["y"] <= my <= r["y"] + r["h"])

        if r.get("hover") != on:
            r["hover"] = on
            region.tag_redraw()

        if on and event.type == "LEFTMOUSE" and event.value == "PRESS":
            self._invoke_playback(ctx)
            return True
        return False

    def _invoke_playback(self, ctx):
        import bpy
        spec = self._provider()
        if spec is None:
            self._report(ctx, "pbrAudio: no signal selected in browser", "WARNING")
            return
        col, eng, oidx, track, sig = spec
        obj = bpy.context.active_object
        if obj is None:
            self._report(ctx, "pbrAudio: select an object to place the sound", "WARNING")
            return
        try:
            bpy.ops.pbraudio.playback_toggle(
                'INVOKE_DEFAULT',
                collection=col, engine=eng, obj_idx=oidx,
                track_name=track, signal_name=sig or "",
                anchor_object=obj.name,
            )
        except Exception as e:
            self._report(ctx, f"pbrAudio playback: {e}", "ERROR")

    @staticmethod
    def _report(ctx, msg, level="INFO"):
        print(f"[pbrAudio playback widget] {msg}")

def _rect_fill(shader, x, y, w, h):
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {"pos": [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]},
    )
    batch.draw(shader)
