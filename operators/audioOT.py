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
from bpy.types import Operator

classes = []

# Operators to add/remove data points to FrequencyResponseChartNode
class NODE_OT_add_frd_point(Operator):
    bl_idname = "node.add_frd_point"
    bl_label = "Add FRD Point"
    bl_description = "Add a new frequency response point"

    def execute(self, context):
        node = context.node
        node.frd_points.add()
        node.frd_points_index = len(node.frd_points) - 1
        return {'FINISHED'}
classes.append(NODE_OT_add_frd_point)

class NODE_OT_remove_frd_point(Operator):
    bl_idname = "node.remove_frd_point"
    bl_label = "Remove FRD Point"
    bl_description = "Remove selected frequency response point"

    def execute(self, context):
        node = context.node
        index = node.frd_points_index
        if index >= 0 and index < len(node.frd_points):
            node.frd_points.remove(index)
            node.frd_points_index = min(max(0, index - 1), len(node.frd_points) - 1)
        return {'FINISHED'}
classes.append(NODE_OT_remove_frd_point)
