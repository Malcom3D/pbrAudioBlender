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
from bpy.types import Node
from bpy.props import StringProperty, EnumProperty, FloatProperty, IntProperty
from bpy_extras.io_utils import ImportHelper

from .baseND import AcousticMaterialNode

classes = []

class NODE_OT_load_frd_file(bpy.types.Operator, ImportHelper):
    """Load FRD frequency response file"""
    bl_idname = "node.load_frd_file"
    bl_label = "Load FRD File"
    
    filter_glob: StringProperty(
        default="*.frd;*.txt;*.csv",
        options={'HIDDEN'}
    )

    node: PointerProperty(
        type=FrequencyResponseNode
    )
    
    def execute(self, context):
#        node = context.node
        if self.node:
            self.node.frd_filepath = self.filepath
            # Extract filename without extension
            filename = os.path.basename(self.filepath)
            node.frd_filename = os.path.splitext(filename)[0]
        return {'FINISHED'}

class FrequencyResponseNode(AcousticMaterialNode):
    """Node for loading and managing frequency response data from FRD files"""
    bl_idname = 'FrequencyResponseNode'
    bl_label = "Frequency Response"
    bl_icon = 'GRAPH'
    
    # File properties
    frd_filepath: StringProperty(
        name="FRD File",
        description="Path to FRD frequency response file",
        subtype='FILE_PATH',
        default=""
    )
    
    frd_filename: StringProperty(
        name="Filename",
        description="Name of the FRD file",
        default=""
    )
    
    # Frequency range properties
    frequency_min: FloatProperty(
        name="Min Frequency",
        description="Minimum frequency in Hz",
        default=20.0,
        min=0.0,
        soft_max=20000.0
    )
    
    frequency_max: FloatProperty(
        name="Max Frequency",
        description="Maximum frequency in Hz",
        default=20000.0,
        min=0.0,
        soft_max=96000.0
    )
    
    # Magnitude properties
    magnitude_min: FloatProperty(
        name="Min Magnitude",
        description="Minimum magnitude in dB",
        default=-60.0,
        soft_min=-120.0,
        soft_max=0.0
    )
    
    magnitude_max: FloatProperty(
        name="Max Magnitude",
        description="Maximum magnitude in dB",
        default=0.0,
        soft_min=-120.0,
        soft_max=20.0
    )
    
    # Display properties
    show_frequency_range: bpy.props.BoolProperty(
        name="Show Frequency Range",
        description="Display frequency range controls",
        default=False
    )
    
    show_magnitude_range: bpy.props.BoolProperty(
        name="Show Magnitude Range",
        description="Display magnitude range controls",
        default=False
    )
    
    # Curve visualization properties
    curve_resolution: IntProperty(
        name="Curve Resolution",
        description="Number of points for curve visualization",
        default=100,
        min=10,
        max=1000
    )
    
    def init(self, context):
        """Initialize the node"""
        self.outputs.new('AcousticMaterialNodeSocket', "FrequencyResponse")
        
    def draw_buttons(self, context, layout):
        """Draw node buttons"""
        # File selection
        row = layout.row()
        row.prop(self, "frd_filename", text="")
        op = row.operator("node.load_frd_file", text="", icon='FILE_FOLDER')
        op.node = self
        
        if self.frd_filepath:
            # Show file info
            box = layout.box()
            box.label(text="File Info:", icon='INFO')
            
            # Try to parse and display file info
            try:
                if os.path.exists(self.frd_filepath):
                    file_size = os.path.getsize(self.frd_filepath)
                    box.label(text=f"Size: {file_size / 1024:.1f} KB")
                    
                    # Try to read first few lines for preview
                    with open(self.frd_filepath, 'r') as f:
                        lines = f.readlines()[:5]
                        if lines:
                            box.label(text="Preview:")
                            for i, line in enumerate(lines[:3]):
                                if line.strip():
                                    box.label(text=f"  {line.strip()[:50]}...")
            except:
                box.label(text="Could not read file", icon='ERROR')
        
        # Frequency range
        row = layout.row(align=True)
        row.prop(self, "show_frequency_range", 
                icon='TRIA_DOWN' if self.show_frequency_range else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Frequency Range")
        
        if self.show_frequency_range:
            col = layout.column(align=True)
            col.prop(self, "frequency_min", slider=True)
            col.prop(self, "frequency_max", slider=True)
        
        # Magnitude range
        row = layout.row(align=True)
        row.prop(self, "show_magnitude_range", icon='TRIA_DOWN' if self.show_magnitude_range else 'TRIA_RIGHT', icon_only=True, emboss=False)
        row.label(text="Magnitude Range")
        
        if self.show_magnitude_range:
            col = layout.column(align=True)
            col.prop(self, "magnitude_min", slider=True)
            col.prop(self, "magnitude_max", slider=True)
        
        # Curve settings
        layout.prop(self, "curve_resolution")
        
        # Preview button
        if self.frd_filepath and os.path.exists(self.frd_filepath):
            layout.operator("node.preview_frequency_response", text="Preview Response", icon='SHADING_RENDERED')
    
    def draw_buttons_ext(self, context, layout):
        """Draw additional buttons in sidebar"""
        layout.prop(self, "frd_filepath")
        
        # Advanced settings
        box = layout.box()
        box.label(text="Advanced Settings:", icon='SETTINGS')
        box.prop(self, "curve_resolution")
        
        # Import/Export options
        row = box.row()
        row.operator("node.export_frequency_response", text="Export")
        row.operator("node.import_frequencyrequency_response", text="Import")
    
    def update(self):
        """Update node output when properties change"""
        # Here you would parse the FRD file and update the output
        if self.frd_filepath and os.path.exists(self.frd_filepath):
            # Parse FRD file and set output values
            # This is where you'd integrate with your FRD parsing logic
            pass
    
    def copy(self, node):
        """Copy node data"""
        self.frd_filepath = node.frd_filepath
        self.frd_filename = node.frd_filename
    
    def free(self):
        """Clean up when node is removed"""
        pass

class NODE_OT_preview_frequency_response(bpy.types.Operator):
    """Preview frequency response curve"""
    bl_idname = "node.preview_frequency_response"
    bl_label = "Preview Frequency Response"
    
    def execute(self, context):
        node = context.node
        if node and node.frd_filepath and os.path.exists(node.frd_filepath):
            # Here you would implement the preview logic
            # This could open a new window or draw in the node editor
            self.report({'INFO'}, f"Previewing {node.frd_filename}")
        return {'FINISHED'}

classes.extend([
    NODE_OT_load_frd_file,
    FrequencyResponseNode,
    NODE_OT_preview_frequency_response
])
