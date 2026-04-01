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
import numpy as np
from bpy.types import Node
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty
from mathutils import Vector

from .baseND import AcousticMaterialNode

classes = []

class FrequencyResponseCurveNode(AcousticMaterialNode):
    """Node for plotting frequency response curves"""
    bl_idname = 'FrequencyResponseCurveNode'
    bl_label = "Frequency Response Curve"
    bl_icon = 'GRAPH'
    
    # Display properties
    show_magnitude: BoolProperty(
        name="Show Magnitude",
        description="Display magnitude curve",
        default=True
    )
    
    show_phase: BoolProperty(
        name="Show Phase",
        description="Display phase curve",
        default=False
    )
    
    show_group_delay: BoolProperty(
        name="Show Group Delay",
        description="Display group delay curve",
        default=False
    )
    
    # Curve style properties
    curve_thickness: FloatProperty(
        name="Curve Thickness",
        description="Thickness of the curve lines",
        default=2.0,
        min=1.0,
        max=10.0
    )
    
    magnitude_color: bpy.props.FloatVectorProperty(
        name="Magnitude Color",
        description="Color for magnitude curve",
        subtype='COLOR',
        default=(0.8, 0.2, 0.2, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )
    
    phase_color: bpy.props.FloatVectorProperty(
        name="Phase Color",
        description="Color for phase curve",
        subtype='COLOR',
        default=(0.2, 0.6, 0.8, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )
    
    group_delay_color: bpy.props.FloatVectorProperty(
        name="Group Delay Color",
        description="Color for group delay curve",
        subtype='COLOR',
        default=(0.2, 0.8, 0.3, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )
    
    # Grid properties
    show_grid: BoolProperty(
        name="Show Grid",
        description="Display grid lines",
        default=True
    )
    
    grid_color: bpy.props.FloatVectorProperty(
        name="Grid Color",
        description="Color for grid lines",
        subtype='COLOR',
        default=(0.3, 0.3, 0.3, 0.3),
        size=4,
        min=0.0,
        max=1.0
    )
    
    # Axis properties
    x_axis_log: BoolProperty(
        name="Log Frequency",
        description="Use logarithmic scale for frequency axis",
        default=True
    )
    
    y_axis_magnitude_range: bpy.props.FloatVectorProperty(
        name="Magnitude Range",
        description="Y-axis range for magnitude",
        size=2,
        default=(-60.0, 0.0),
        min=-200.0,
        max=200.0
    )
    
    y_axis_phase_range: bpy.props.FloatVectorProperty(
        name="Phase Range",
        description="Y-axis range for phase",
        size=2,
        default=(-180.0, 180.0),
        min=-360.0,
        max=360.0
    )
    
    y_axis_group_delay_range: bpy.props.FloatVectorProperty(
        name="Group Delay Range",
        description="Y-axis range for group delay",
        size=2,
        default=(0.0, 0.01),
        min=0.0,
        max=1.0
    )
    
    # Plot dimensions
    plot_width: FloatProperty(
        name="Plot Width",
        description="Width of the plot area",
        default=400.0,
        min=100.0,
        max=1000.0
    )
    
    plot_height: FloatProperty(
        name="Plot Height",
        description="Height of the plot area",
        default=300.0,
        min=100.0,
        max=1000.0
    )
    
    # Data source
    source_node: bpy.props.StringProperty(
        name="Source Node",
        description="Name of the frequency response node to plot",
        default=""
    )
    
    def init(self, context):
        """Initialize the node"""
        self.inputs.new('AcousticMaterialNodeSocket', "FrequencyResponse")
        self.outputs.new('AcousticMaterialNodeSocket', "CurveData")
    
    def draw_buttons(self, context, layout):
        """Draw node buttons"""
        # Source selection
        box = layout.box()
        box.label(text="Data Source:", icon='LINKED')
        
        # Find connected frequency response nodes
        connected_nodes = []
        if self.inputs[0].is_linked:
            for link in self.inputs[0].links:
                if link.from_node.bl_idname == 'FrequencyResponseNode':
                    connected_nodes.append(link.from_node)
        
        if connected_nodes:
            row = box.row()
            row.label(text="Connected:")
            row = box.row()
            for node in connected_nodes:
                row.label(text=node.name, icon='NODE')
        else:
            box.label(text="No frequency response connected", icon='ERROR')
        
        # Display options
        box = layout.box()
        box.label(text="Display Options:", icon='SHADING_RENDERED')
        
        row = box.row()
        row.prop(self, "show_magnitude")
        if self.show_magnitude:
            row.prop(self, "magnitude_color", text="")
        
        row = box.row()
        row.prop(self, "show_phase")
        if self.show_phase:
            row.prop(self, "phase_color", text="")
        
        row = box.row()
        row.prop(self, "show_group_delay")
        if self.show_group_delay:
            row.prop(self, "group_delay_color", text="")
        
        # Axis options
        box = layout.box()
        box.label(text="Axis Options:", icon='AXIS_TOP')
        
        box.prop(self, "x_axis_log")
        
        if self.show_magnitude:
            col = box.column(align=True)
            col.label(text="Magnitude Range (dB):")
            col.prop(self, "y_axis_magnitude_range", index=0, text="Min")
            col.prop(self, "y_axis_magnitude_range", index=1, text="Max")
        
        if self.show_phase:
            col = box.column(align=True)
            col.label(text="Phase Range (deg):")
            col.prop(self, "y_axis_phase_range", index=0, text="Min")
            col.prop(self, "y_axis_phase_range", index=1, text="Max")
        
        if self.show_group_delay:
            col = box.column(align=True)
            col.label(text="Group Delay Range (s):")
            col.prop(self, "y_axis_group_delay_range", index=0, text="Min")
            col.prop(self, "y_axis_group_delay_range", index=1, text="Max")
        
        # Style options
        box = layout.box()
        box.label(text="Style Options:", icon='PREFERENCES')
        
        box.prop(self, "curve_thickness")
        box.prop(self, "show_grid")
        if self.show_grid:
            box.prop(self, "grid_color", text="Grid Color")
        
        # Plot dimensions
        box = layout.box()
        box.label(text="Plot Dimensions:", icon='FULLSCREEN_ENTER')
        
        col = box.column(align=True)
        col.prop(self, "plot_width")
        col.prop(self, "plot_height")
        
        # Update button
        box = layout.box()
        box.operator("node.update_frequency_curve", text="Update Plot", icon='FILE_REFRESH')
    
    def draw_buttons_ext(self, context, layout):
        """Draw additional buttons in sidebar"""
        # Export options
        box = layout.box()
        box.label(text="Export:", icon='EXPORT')
        
        row = box.row()
        row.operator("node.export_curve_image", text="Export as Image")
        row.operator("node.export_curve_data", text="Export Data")
        
        # Statistics
        box = layout.box()
        box.label(text="Statistics:", icon='INFO')
        
        # Get data from connected node
        data = self.get_frequency_data()
        if data:
            frequencies, magnitudes, phases = data
            
            if len(frequencies) > 0:
                box.label(text=f"Points: {len(frequencies)}")
                box.label(text=f"Freq Range: {frequencies[0]:.1f} - {frequencies[-1]:.1f} Hz")
                
                if len(magnitudes) > 0:
                    box.label(text=f"Mag Range: {np.min(magnitudes):.1f} - {np.max(magnitudes):.1f} dB")
                
                if len(phases) > 0:
                    box.label(text=f"Phase Range: {np.min(phases):.1f} - {np.max(phases):.1f}°")
    
    def get_frequency_data(self):
        """Get frequency data from connected node"""
        if not self.inputs[0].is_linked:
            return None
        
        # Get connected frequency response node
        for link in self.inputs[0].links:
            if link.from_node.bl_idname == 'FrequencyResponseNode':
                node = link.from_node
                if node.data_valid:
                    return node.get_frequency_response_data()
        
        return None
    
    def get_group_delay_data(self):
        """Calculate group delay from phase data"""
        data = self.get_frequency_data()
        if not data:
            return None
        
        frequencies, magnitudes, phases = data
        
        if len(frequencies) < 2 or len(phases) < 2:
            return None
        
        # Calculate group delay
        from ..utils.frd_parser import calculate_group_delay
        group_delay = calculate_group_delay(frequencies, phases)
        
        return frequencies, group_delay
    
    def draw_curve(self, context):
        """Draw the curve in the node"""
        # This method would be called by a custom draw handler
        # For now, we'll create a separate operator to draw the curve
        pass

class NODE_OT_update_frequency_curve(bpy.types.Operator):
    """Update frequency response curve plot"""
    bl_idname = "node.update_frequency_curve"
    bl_label = "Update Plot"
    
    def execute(self, context):
        node = context.node
        if node:
            # Force redraw of the node
            node.update()
            # Update any viewport drawing
            context.area.tag_redraw()
        return {'FINISHED'}

class NODE_OT_export_curve_image(bpy.types.Operator):
    """Export frequency response curve as image"""
    bl_idname = "node.export_curve_image"
    bl_label = "Export as Image"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save the image",
        subtype='FILE_PATH'
    )
    
    image_format: bpy.props.EnumProperty(
        name="Format",
        items=[
            ('PNG', "PNG", "PNG format"),
            ('JPEG', "JPEG", "JPEG format"),
            ('TIFF', "TIFF", "TIFF format"),
            ('BMP', "BMP", "BMP format"),
        ],
        default='PNG'
    )
    
    image_width: bpy.props.IntProperty(
        name="Width",
        description="Image width in pixels",
        default=800,
        min=100,
        max=4096
       )
    
    image_height: bpy.props.IntProperty(
        name="Height",
        description="Image height in pixels",
        default=600,
        min=100,
        max=4096
    )
    
    def invoke(self, context, event):
        # Set default filepath
        self.filepath = bpy.path.abspath("//frequency_response.png")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        node = context.node
        if node:
            # Here you would implement image export
            # This would require creating an off-screen render of the curve
            self.report({'INFO'}, f"Exporting curve to {self.filepath}")
        return {'FINISHED'}

class NODE_OT_export_curve_data(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export frequency response curve data"""
    bl_idname = "node.export_curve_data"
    bl_label = "Export Data"
    
    filename_ext = ".csv"
    
    filter_glob: bpy.props.StringProperty(
        default="*.csv;*.txt",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        node = context.node
        if node:
            data = node.get_frequency_data()
            if data:
                frequencies, magnitudes, phases = data
                
                # Write to CSV
                with open(self.filepath, 'w') as f:
                    f.write("Frequency (Hz),Magnitude (dB),Phase (deg)\n")
                    for i in range(len(frequencies)):
                        f.write(f"{frequencies[i]},{magnitudes[i]},{phases[i]}\n")
                
                self.report({'INFO'}, f"Exported {len(frequencies)} points to {self.filepath}")
            else:
                self.report({'WARNING'}, "No data to export")
        
        return {'FINISHED'}

classes.extend([
    FrequencyResponseCurveNode,
    NODE_OT_update_frequency_curve,
    NODE_OT_export_curve_image,
    NODE_OT_export_curve_data
])
