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
Operators:
    pbraudio.playback_toggle  — toggles the spatial aud player
    pbraudio.storage_cd       — cd the browser (for external keymaps)
"""

import bpy
import numpy as np
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty

from ...gui.core.spatial_player import SpatialPlayer

classes = []

class PBRAUDIO_OT_storage_cd(Operator):
    """Change the pbrAudio storage browser working directory"""
    bl_idname = "pbraudio.storage_cd"
    bl_label = "pbrAudio Browser cd"
    bl_options = {'REGISTER', 'UNDO'}

    path: StringProperty(name="Path", default="/")

    def execute(self, context):
        bs = context.scene.get("_pbraudio_browser")
        # Not exposed through scene; the widget owns it. Kept for keymaps.
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_storage_cd)

class PBRAUDIO_OT_playback_toggle(Operator):
    """Play or stop the selected pbrAudioStorage signal spatially"""
    bl_idname = "pbraudio.playback_toggle"
    bl_label = "Toggle pbrAudio Playback"
    bl_options = {'REGISTER', 'UNDO'}

    collection:   StringProperty(default="")
    engine:       StringProperty(default="")
    obj_idx:      IntProperty(default=-1)
    track_name:   StringProperty(default="")
    signal_name:  StringProperty(default="")
    anchor_object: StringProperty(default="")

    def execute(self, context):
        player = SpatialPlayer.get()

        # Toggle off if already playing
        if player.playing:
            player.stop()
            self.report({'INFO'}, "pbrAudio: playback stopped")
            return {'FINISHED'}

        if not self.collection or not self.engine or self.obj_idx < 0:
            # fallback to the DAW TUI selection
            spec = _spec_from_browser_selection(context)
            if spec is None:
                self.report({'WARNING'}, "pbrAudio: no signal selected")
                return {'CANCELLED'}
            self.collection, self.engine, self.obj_idx, self.track_name, self.signal_name = spec

        audio, sr = _read_signal(context, self.collection, self.engine, self.obj_idx, self.track_name, self.signal_name)
        if audio is None:
            self.report({'ERROR'}, "pbrAudio: could not read audio")
            return {'CANCELLED'}

        anchor = self.anchor_object or (context.active_object.name if context.active_object else None)
        player.play(audio, sr, anchor)

        # Free-vector update so viewports refresh
        _tag_redraw(context)
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_playback_toggle)

# ----------------------------------------------------------------------
# plumbing
# ----------------------------------------------------------------------
def _get_storage_engine(context):
    """Return the shared StorageEngine instance, creating it on first use."""
    try:
        from pbrAudioStorage import StorageEngine
        from pbrAudioCommon import EntityManager
    except ImportError:
        return None

    cache = context.scene.get("_pbraudio_storage_engine")
    if cache is not None:
        return cache

    cache_path = context.scene.pbraudio.cache_path
    if cache_path.startswith("//"):
        cache_path = bpy.path.abspath(cache_path)
    config_file = f"{cache_path}/AcousticDomain/config.json"

    try:
        em = EntityManager(config_file)
        engine = StorageEngine(entity_manager=em)
    except Exception as e:
        print(f"[pbrAudio] storage engine init failed: {e}")
        return None

    context.scene["_pbraudio_storage_engine"] = engine
    return engine


def _get_browser_state(context):
    """Return the shared BrowserState instance used by the widget."""
    cache = context.scene.get("_pbraudio_browser")
    if cache is not None:
        return cache
    return None


def _spec_from_browser_selection(context):
    bs = _get_browser_state(context)
    if bs is None:
        return None
    try:
        spec = bs.parse_signal_path("/" + "/".join(bs.cwd))
    except Exception:
        return None
    # storage.parse_signal_path may return signal=None for a track
    col, eng, oidx, track, sig = spec
    return col, eng, oidx, track, sig or ""


def _read_signal(context, collection, engine, obj_idx, track_name, signal_name):
    storage = _get_storage_engine(context)
    if storage is None:
        return None, 0
    try:
        data = storage.read(collection=collection, engine=engine, obj_idx=obj_idx, track_name=track_name, signal_name=signal_name or None)
    except Exception as e:
        print(f"[pbrAudio] storage.read failed: {e}")
        return None, 0

    if data is None:
        return None, 0

    data = np.ascontiguousarray(data, dtype=np.float32)
    sr = int(context.scene.pbraudio.sample_rate)
    return data, sr

def _tag_redraw(context):
    for area in context.screen.areas if context.screen else ():
        if area.type == 'VIEW_3D':
            area.tag_redraw()
