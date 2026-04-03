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

# Operators to add/clear data points to FrequencyResponseChartNode
class NODE_OT_add_freq_response_data(Operator):
    bl_idname = "node.add_freq_response_data"
    bl_label = "Add Frequency Response Data Point"

    def execute(self, context):
        node = context.active_node
        if hasattr(node, "response_data"):
            new_item = node.response_data.add()
            new_item.frequency = 1000.0
            new_item.magnitude = 0.0
            new_item.phase = 0.0
        return {'FINISHED'}
classes.append(NODE_OT_add_freq_response_data)

class NODE_OT_clear_freq_response_data(Operator):
    bl_idname = "node.clear_freq_response_data"
    bl_label = "Clear Frequency Response Data"

    def execute(self, context):
        node = context.active_node
        if hasattr(node, "response_data"):
            node.response_data.clear()
        return {'FINISHED'}
classes.append(NODE_OT_clear_freq_response_data)
