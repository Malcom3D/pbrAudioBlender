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
import os
from bpy.types import Operator
from ..utils import frd_io

classes = []

class BigPreview(Operator):
    bl_idname = "node.big_preview"
    bl_label = "Big Preview"
    def execute(self, context):
        print("Running big preview")
        return {'FINISHED'}
    def check(self, context):
        return False
    def invoke(self, context, event):
        wm = context.window_manager
        self.texture = bpy.data.textures.new(name="previewTexture", type="IMAGE")
        self.texture.image = context.window_manager.image
        self.texture.extension = 'CHECKER'  # EXTEND # CLIP # CLIP_CUBE # REPEAT # CHECKER
        print("Invoke big preview")
        return wm.invoke_props_dialog(self, width=600)
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        #col.scale_y = 2
        col.template_preview(self.texture, show_buttons=False)
        
classes.append(BigPreview)

class PBRAUDIO_OT_export_frd_response(Operator):
    bl_idname = "node.export_frd_response"
    bl_label = "Export FRD Response"
    bl_description = "Export the manually entered frequency response data to a FRD file"

    def execute(self, context):
        node = context.node
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
        filename = bpy.path.abspath(node.filename)
        try:
            if node.has_phase:
                frd_io.write_frd_file(filename, freq_array, mag_array, phase_array)
            else:
                frd_io.write_frd_file(filename, freq_array, mag_array)
            self.report({'INFO'}, f"FRD file exported: {filename}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'}

classes.append(NODE_OT_export_frd_response)
