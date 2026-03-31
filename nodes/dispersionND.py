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
import math
from bpy.types import Node
from bpy.props import IntProperty, FloatProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup

from .baseND import ThreeDfrequencyNode
from .frequencyND import FrequencyResponseNode

classes = []

class DispersionPoint(PropertyGroup):
    """Property group for a single dispersion point"""
    azimuth: IntProperty(
        name="Azimuth",
        description="Azimuth angle in degrees (0-360)",
        default=0,
        min=0,
        max=360,
        subtype='ANGLE'
    )
    
    elevation: IntProperty(
        name="Elevation",
        description="Elevation angle in degrees (-90 to 90)",
        default=0,
        min=-90,
        max=90,
        subtype='ANGLE'
    )
    
    # Reference to frequency response node
    frequency_response: PointerProperty(
        name="Frequency Response",
        type=frequencyND.FrequencyResponseNode,
        description="Frequency response for this azimuth/elevation"
    )

class DispersionPatternNode(ThreeDfrequencyNode):
    """3D Dispersion Pattern node with dynamic inputs for azimuth/elevation pairs"""
    bl_idname = 'DispersionPatternNode'
    bl_label = "3D Dispersion Pattern"
    bl_icon = 'MATSPHERE'
    
    # Collection of dispersion points
    dispersion_points: CollectionProperty(
        type=DispersionPoint
    )
    
    # Active point index
    active_point_index: IntProperty(
        name="Active Point Index",
        default=0,
        min=0
    )
    
    # Grid properties
    azimuth_resolution: IntProperty(
        name="Azimuth Resolution",
        description="Number of azimuth steps (0-360)",
        default=12,
        min=1,
        max=72
    )
    
    elevation_resolution: IntProperty(
        name="Elevation Resolution",
        description="Number of elevation steps (-90 to 90)",
        default=7,
        min=1,
        max=19
    )
    
    # Display properties
    show_grid: bpy.props.BoolProperty(
        name="Show Grid",
        description="Display grid controls",
        default=True
    )
    
    show_points: bpy.props.BoolProperty(
        name="Show Points",
        description="Display point list",
        default=True
    )
    
    # Symmetry properties
    symmetry_type: bpy.props.EnumProperty(
        name="Symmetry",
        items=[
            ('NONE', "None", "No symmetry"),
            ('AXIAL', "Axial", "Axial symmetry"),
            ('SPHERICAL', "Spherical", "Spherical symmetry"),
            ('CUSTOM', "Custom", "Custom symmetry pattern")
        ],
        default='NONE'
    )
    
    def init(self, context):
        """Initialize the node"""
        self.outputs.new('AcousticMaterialNodeSocket', "DispersionPattern")
        
        # Create default grid
        self.create_default_grid()
    
    def create_default_grid(self):
        """Create a default grid of points"""
        self.dispersion_points.clear()
        
        # Create points for a basic grid
        for elev in range(-90, 91, 30):  # -90, -60, -30, 0, 30, 60, 90
            for azi in range(0, 360, 45):  # 0, 45, 90, 135, 180, 225, 270, 315
                point = self.dispersion_points.add()
                point.azimuth = azi
                point.elevation = elev
    
    def update_grid(self):
        """Update grid based on resolution settings"""
        self.dispersion_points.clear()
        
        # Calculate step sizes
        azi_step = 360 / self.azimuth_resolution
        elev_step = 180 / (self.elevation_resolution - 11)
        
        # Create grid points
        for elev_idx in range(self.elevation_resolution):
            elevation = -90 + (elev_idx * elev_step)
            for azi_idx in range(self.azimuth_resolution):
                azimuth = azi_idx * azi_step
                
                point = self.dispersion_points.add()
                point.azimuth = int(azimuth)
                point.elevation = int(elevation)
        
        # Update sockets
        self.update_sockets()
    
    def update_sockets(self):
        """Update input sockets based on dispersion points"""
        # Remove all existing input sockets
        for socket in list(self.inputs):
            self.inputs.remove(socket)
        
        # Add sockets for each point
        for i, point in enumerate(self.d.dispersion_points):
            socket_name = f"FR_{point.azimuth:03d}_{point.elevation:+03d}"
            socket = self.inputs.new('AcousticMaterialNodeSocket', socket_name)
            socket.text = f"Az: {point.azimuth}°, El: {point.elevation}°"
    
    def draw_buttons(self, context, layout):
        """Draw node buttons"""
        # Grid controls
        row = layout.row(align=True)
        row.prop(self, "show_grid",
                icon='TRIA_DOWN' if self.show_grid else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Grid Settings")
        
        if self.show_grid:
            box = layout.box()
            
            # Resolution controls
            col = box.column(align=True)
            col.prop(self, "azimuth_resolution")
            col.prop(self, "elevation_resolution")
            
            # Update button
            row = box.row()
            row.operator("node.update_dispersion_grid", text="Update Grid")
            
            # Symmetry
            box.prop(self, "symmetry_type")
            
            # Auto-fill button
            if self.symmetry_type != 'NONE':
                box.operator("node.apply_symmetry", text="Apply Symmetry")
        
        # Points list
        row = layout.row(align=True)
        row.prop(self, "show_points",
                icon='TRIA_DOWN' if self.show_points else 'TRIA_RIGHT',
                icon_only=True, emboss=False)
        row.label(text="Dispersion Points")
        
        if self.show_points:
            box = layout.box()
            
            # List of points
            for i, point in enumerate(self.dispersion_points):
                row = box.row(align=True)
                
                # Point info
                col = row.column(align=True)
                col.label(text=f"Point {i+1}:")
                col = row.column(align=True)
                col.label(text=f"Az: {point.azimuth}°")
                col.label(text=f"El: {point.elevation}°")
                
                # Connect button
                if not point.frequency_response:
                    op = row.operator("node.connect_frequency_response", 
                                    text="Connect", icon='LINKED')
                    op.point_index = i
                else:
                    row.label(text=point.frequency_response.name, icon='LINKED')
            
            # Add/remove points
            row = box.row(align=True)
            row.operator("node.add_dispersion_point", text="Add Point", icon='ADD')
            row.operator("node.remove_dispersion_point", text="Remove", icon='REMOVE')
        
        # Visualization
        layout.operator("node.visualize_dispersion", 
                      text="Visualize Pattern", icon='SHADING_RENDERED')
    
    def draw_buttons_ext(self, context, layout):
        """Draw additional buttons in sidebar"""
        # Import/Export
        box = layout.box()
        box.label(text="Import/Export:", icon='FILE')
        
        row = box.row()
        row.operator("node.export_dispersion_pattern", text="Export")
        row.operator("node.import_dispersion_pattern", text="Import")
        
        # Advanced settings
        box = layout.box()
        box.label(text="Advanced:", icon='SETTINGS')
        
        # Interpolation settings
        box.prop(self, "symmetry_type")
        
        # Clear all button
        box.operator("node.clear_dispersion_points", text="Clear All Points")
    
    def update(self):
        """Update node when properties change"""
        # Update grid if resolution changed
        if hasattr(self, '_last_azi_res') and hasattr(self, '_last_elev_res'):
            if (self._last_azi_res != self.azimuth_resolution or 
                self._last_elev_res != self.elevation_resolution):
                self.update_grid()
        
        self._last_azi_res = self.azimuth_resolution
        self._last_elev_res = self.elevation_resolution
    
    def copy(self, node):
        """Copy node data"""
        # Copy dispersion points
        self.dispersion_points.clear()
        for point in node.dispersion_points:
            new_point = self.dispersion_points.add()
            new_point.azimuth = point.azimuth
            new_point.elevation = point.elevation
            # # Note: frequency_response pointer might need special handling
    
    def free(self):
        """Clean up when node is removed"""
        pass

# Operator classes
class NODE_OT_update_dispersion_grid(bpy.types.Operator):
    """Update dispersion grid"""
    bl_idname = "node.update_dispersion_grid"
    bl_label = "Update Grid"
    
    def execute(self, context):
        node = context.node
        if node:
            node.update_grid()
        return {'FINISHED'}

class NODE_OT_add_dispersion_point(bpy.types.Operator):
    """Add a new dispersion point"""
    bl_idname = "node.add_dispersion_point"
    bl_label = "Add Point"
    
    def execute(self, context):
        node = context.node
        if node:
            point = node.dispersion_points.add()
            point.azimuth = 0
            point.elevation = 0
            node.active_point_index = len(node.dispersion_points) - 1
            node.update_sockets()
        return {'FINISHED'}

class NODE_OT_remove_dispersion_point(bpy.types.Operator):
    """Remove active dispersion point"""
    bl_idname = "node.remove_dispersion_point"
    bl_label = "Remove Point"
    
    def execute(self, context):
        node = context.node
        if node and node.dispersion_points:
            if node.active_point_index < len(node.dispersion_points):
                node.dispersion_points.remove(node.active_point_index)
                node.active_point_index = min(node.active_point_index, 
                                            len(node.dispersion_points) - 1)
                node.update_sockets()
        return {'FINISHED'}

class NODE_OT_connect_frequency_response(bpy.types.Operator):
    """Connect frequency response to dispersion point"""
    bl_idname = "node.connect_frequency_response"
    bl_label = "Connect Frequency Response"
    
    point_index: IntProperty()
    
    def execute(self, context):
        node = context.node
        if node and self.point_index < len(node.dispersion_points):
            # This would typically open a node picker or link nodes
            # For now, just report
            self.report({'INFO'}, f"Connect to point {self.point_index}")
        return {'FINISHED'}

class NODE_OT_apply_symmetry(bpy.types.Operator):
    """Apply symmetry to dispersion pattern"""
    bl_idname = "node.apply_symmetry"
    bl_label = "Apply Symmetry"
    
    def execute(self, context):
        node = context.node
        if node:
            # Implement symmetry logic based on symmetry_type
            self.report({'INFO'}, f"Applied {node.symmetry_type} symmetry")
        return {'FINISHED'}

class NODE_OT_visualize_dispersion(bpy.types.Operator):
    """Visualize 3D dispersion pattern"""
    bl_idname = "node.visualize_dispersion"
    bl_label = "Visualize"
    
    def execute(self, context):
        node = context.node
        if node:
            # Create 3D visualization of dispersion pattern
            # This could create a mesh or use viewport drawing
            self.report({'INFO'}, "Creating 3D visualization")
        return {'FINISHED'}

class NODE_OT_clear_dispersion_points(bpy.types.Operator):
    """Clear all dispersion points"""
    bl_idname = "node.clear_dispersion_points"
    bl_label = "Clear All"
    
    def execute(self, context):
        node = context.node
        if node:
            node.dispersion_points.clear()
            node.update_sockets()
        return {'FINISHED'}

# Register all classes
classes.extend([
    DispersionPoint,
    DispersionPatternNode,
    NODE_OT_update_dispersion_grid,
    NODE_OT_add_dispersion_point,
    NODE_OT_remove_dispersion_point,
    NODE_OT_connect_frequency_response,
    NODE_OT_apply_symmetry,
    NODE_OT_visualize_dispersion,
    NODE_OT_clear_dispersion_points
])
