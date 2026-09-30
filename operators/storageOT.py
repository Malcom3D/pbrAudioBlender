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

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

classes = []

class PBRAUDIO_OT_blosc2_filter_add(Operator):
    """Add a new blosc2 filter to the list"""
    bl_idname = "pbraudio.blosc2_filter_add"
    bl_label = "Add Blosc2 Filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        storage_props = context.scene.pbraudiostorage
        storage_props.blosc2_filters.add()
        storage_props.blosc2_filters_index = len(storage_props.blosc2_filters) - 1
        return {'FINISHED'}
classes.append(PBRAUDIO_OT_blosc2_filter_add)

class PBRAUDIO_OT_blosc2_filter_remove(Operator):
    """Remove the selected blosc2 filter from the list"""
    bl_idname = "pbraudio.blosc2_filter_remove"
    bl_label = "Remove Blosc2 Filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        storage_props = context.scene.pbraudiostorage
        index = storage_props.blosc2_filters_index
        if 0 <= index < len(storage_props.blosc2_filters):
            storage_props.blosc2_filters.remove(index)
            storage_props.blosc2_filters_index = min(max(0, index - 1), len(storage_props.blosc2_filters) - 1)
        return {'FINISHED'}
classes.append(PBRAUDIO_OT_blosc2_filter_remove)
