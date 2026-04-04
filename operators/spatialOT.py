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
from bpy.props import StringProperty, FloatProperty

classes = []

class NODE_OT_add_spatial_point(Operator):
    """Add a new spatial response point"""
    bl_idname = "node.add_spatial_point"
    bl_label = "Add Spatial Point"
    bl_description = "Add a new spatial response point"
    
    node_tree: StringProperty(name="Node Tree", default="")
    node_name: StringProperty(name="Node Name", default="")
    
    azimuth: FloatProperty(
        name="Azimuth",
        description="Azimuth angle in degrees",
        default=0.0,
        min=0.0,
        max=360.0
    )
    
    elevation: FloatProperty(
        name="Elevation",
        description="Elevation angle in degrees",
        default=0.0,
        min=-90.0,
        max=90.0
    )
    
    def invoke(self, context, event):
        # Open a dialog to set azimuth and elevation
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "azimuth")
        layout.prop(self, "elevation")
    
    def execute(self, context):
        if not self.node_name == "":
            node = bpy.data.node_groups[self.node_tree].nodes[self.node_name]
            
            # Add new point
            point = node.spatial_points.add()
            point.azimuth = self.azimuth
            point.elevation = self.elevation
            node.spatial_points_index = len(node.spatial_points) - 1
            
            # Update dynamic inputs
            node.update_dynamic_inputs()
            
            # Update the node
            node.update()
            
            return {'FINISHED'}
        return {'CANCELLED'}

classes.append(NODE_OT_add_spatial_point)

class NODE_OT_remove_spatial_point(Operator):
    """Remove selected spatial point"""
    bl_idname = "node.remove_spatial_point"
    bl_label = "Remove Spatial Point"
    bl_description = "Remove selected spatial point"
    
    node_tree: StringProperty(name="Node Tree", default="")
    node_name: StringProperty(name="Node Name", default="")
    
    def execute(self, context):
        if not self.node_name == "":
            node = bpy.data.node_groups[self.node_tree].nodes[self.node_name]
            index = node.spatial_points_index
            
            if index >= 0 and index < len(node.spatial_points):
                # Remove the point
                node.spatial_points.remove(index)
                
                # Adjust index
                node.spatial_points_index = min(max(0, index - 1), len(node.spatial_points) - 1)
                
                # Update dynamic inputs
                node.update_dynamic_inputs()
                
                # Update the node
                node node.update()
            
            return {'FINISHED'}
        return {'CANCELLED'}

classes.append(NODE_OT_remove_spatial_point)

class NODE_OT_update_spatial_inputs(Operator):
    """Update spatial inputs to match points"""
    bl_idname = "node.update_spatial_inputs"
    bl_label = "Update Spatial Inputs"
    bl_description = "Update dynamic inputs to match spatial points"
    
    node_tree: StringProperty(name="Node Tree", default="")
    node_name: StringProperty(name="Node Name", default="")
    
    def execute(self, context):
        if not self.node_name == "":
            node = bpy.data.node_groups[self.node_tree].nodes[self.node_name]
            node.update_dynamic_inputs()
            node.update()
            return {'FINISHED'}
        return {'CANCELLED'}

classes.append(NODE_OT_update_spatial_inputs)

class NODE_OT_generate_spherical_grid(Operator):
    """Generate a spherical grid of spatial points"""
    bl_idname = "node.generate_spherical_grid"
    bl_label = "Generate Spherical Grid"
    bl_description = "GenerateGenerate a spherical grid of spatial points"
    
    node_tree: StringProperty(name="Node Tree", default="")
    node_name: StringProperty(name="Node Name", default="")
    
    azimuth_steps: IntProperty(
        name="Azimuth Steps",
        description="Number of azimuth steps (0-360°)",
        default=8,
        min=1,
        max=36
    )
    
    elevation_steps: IntProperty(
        name="Elevation Steps",
        description="Number of elevation steps (-90° to 90°)",
        default=5,
        min=1,
        max=18
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "azimuth_steps")
        layout.prop(self, "elevation_steps")
    
    def execute(self, context):
        if not self.node_name == "":
            node = bpy.data.node_groups[self.node_tree].nodes[self.node_name]
            
            # Clear existing points
            node.spatial_points.clear()
            
            # Generate spherical grid
            for elev_idx in range(self.elevation_steps):
                # Calculate elevation (-90 to 90 degrees)
                if self.elevation_steps == 1:
                    elevation = 0.0
                else:
                    elevation = -90.0 + (180.0 * elev_idx / (self.elevation_steps - 1))
                
                for azim_idx in range(self.azimuth_steps):
                    # Calculate azimuth (0 to 360 degrees)
                    azimuth = 360.0 * azim_idx / self.azimuth_steps
                    
                    # Add point
                    point = node.spatial_points.add()
                    point.azimuth = azimuth
                    point.elevation = elevation
            
            # Update index
            node.spatial_points_index = 0
            
            # Update dynamic inputs
            node.update_dynamic_inputs()
            
            # Update the node
            node.update()
            
            self.report({'INFO'}, f"Generated {len(node.spatial_points)} spatial points")
            return {'FINISHED'}
        return {'CANCELLED'}

classes.append(NODE_OT_generate_spherical_grid)
