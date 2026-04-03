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
from bpy.props import StringProperty, PointerProperty

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

class NODE_OT_export_frd_response(Operator):
    bl_idname = "node.export_frd_response"
    bl_label = "Export FRD Response"
    bl_description = "Export the manually entered frequency response data to a FRD file"

    filepath: StringProperty(
        name="filename",
        description="Path of frd file to save",
        subtype='FILE_PATH', 
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default=''
    )

    node: PointerProperty(
        name="node",
        type=bpy.types.Node
    )

    def invoke(self, context, event):
        if self.filepath == '':
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    def execute(self, context):
        node = self.node
        # Gather data points
        frequencies = []
        magnitudes = []
        phases = []

        for point in node.frd_points:
            frequencies.append(point.frequency)
            magnitudes.append(point.magnitude)
            if node.has_phase:
                phases.append(point.phase)

        # Convert to numpy arrays
        import numpy as np
        freq_array = np.array(frequencies)
        mag_array = np.array(magnitudes)
        phase_array = np.array(phases) if node.has_phase else None

        # Call your frd_io utility
        filename = bpy.path.abspath(self.filepath)
        try:
            frd_io.write_frd_file(filename, freq_array, mag_array, phase_array)
#            if node.has_phase:
#                frd_io.write_frd_file(filename, freq_array, mag_array, phase_array)
#            else:
#                frd_io.write_frd_file(filename, freq_array, mag_array)
            self.report({'INFO'}, f"FRD file exported: {filename}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'}

classes.append(NODE_OT_export_frd_response)
