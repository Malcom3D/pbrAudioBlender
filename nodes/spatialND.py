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
from bpy.types import Node
from bpy.props import IntProperty, FloatProperty, StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList

from .baseND import AcousticBaseNode
from ..utils import frd_io

classes = []

class SpatialResponsePoint(PropertyGroup):
    """Property group for a spatial response point (azimuth, elevation, response node)"""
    azimuth: FloatProperty(
        name="Azimuth (degrees)",
        description="Azimuth angle in degrees (0-360)",
        default=0.0,
        min=0.0,
        max=360.0,
        subtype='ANGLE'
    )
    
    elevation: FloatProperty(
        name="Elevation (degrees)",
        description="Elevation angle in degrees (-90 to 90)",
        default=0.0,
        min=-90.0,
        max=90.0,
        subtype='ANGLE'
    )
    
    # We'll store the node name that provides the frequency response
    response_node_name: StringProperty(
        name="Response Node",
        description="Name of the node providing frequency response data",
        default=""
    )
    
    # We'll store the node tree name for reference
    node_tree_name: StringProperty(
        name="Node Tree",
        description="Name of the node tree containing the response node",
        default=""
    )

    link_idx: IntProperty(
        name="Input link idx",
        default=0
    )
classes.append(SpatialResponsePoint)

class SPATIALRESPONSE_UL_Points(UIList):
    """UIList for displaying spatial response points points"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "azimuth", text="Az")
        row.prop(item, "elevation", text="El")
        
        # Show response node name if available
        if item.response_node_name:
            row.label(text=item.response_node_name)
        else:
            row.label(text="No response", icon='ERROR')
classes.append(SPATIALRESPONSE_UL_Points)

class SpatialFrequencyResponseNode(AcousticBaseNode):
    """Node to combine multiple frequency responses into a spatial response"""
    bl_idname = 'SpatialFrequencyResponseNode'
    bl_label = 'Spatial Frequency Response'
    bl_icon = 'ORIENTATION_GIMBAL'
    
    pbraudio_type: StringProperty(default='SpatialFrequencyResponse')
    
    # Collection of spatial response points
    spatial_points: CollectionProperty(type=SpatialResponsePoint)
    spatial_points_index: IntProperty(
        name='Index',
        default=0
    )
    
    # Interpolation method
    interpolation_method: EnumProperty(
        name="Interpolation",
        description="Method for interpolating between spatial points",
        items=[
            ('NEAREST', "Nearest", "Use nearest point"),
            ('BILINEAR', "Bilinear", "Bilinear interpolation between points"),
            ('SPHERICAL', "Spherical", "Spherical interpolation (great circle)"),
        ],
        default='BILINEAR'
    )
    
    # Whether to normalize responses
    normalize_responses: BoolProperty(
        name="Normalize Responses",
        description="Normalize all frequency responses to have the same average magnitude",
        default=True
    )
    
    # Reference to the node tree for dynamic inputs
    dynamic_inputs_initialized: BoolProperty(default=False)
    
    def init(self, context):
        self.outputs.new('AcousticValueNodeSocket', "Spatial Frequency Response")
    
    def add_inputs(self):
        i, point in enumerate(self.spatial_points)[-1]
        input_name = f"Response {i+1:02d} ({point.azimuth:.0f}°, {point.elevation:.0f}°)"
        socket = self.inputs.new('AcousticValueNodeSocket', input_name)
        socket.identifier = f"response_{i}"
        
        # Store point index in socket for reference
        socket.point_index = i
    
    def update_dynamic_inputs(self):
        """Create dynamic inputs based on spatial points"""
        # Update point references in connected nodes
        for i, point in enumerate(self.spatial_points):
            input_idx = self.get_input_index_for_point(i)
            if input_idx >= 0 and self.inputs[input_idx].is_linked:
                # Get the connected node
                link = self.inputs[input_idx].links[0]
                from_node = link.from_node

                # Update the point with node reference
                point.response_node_name = from_node.name
                point.node_tree_name = from_node.id_data.name
                point.link_idx = input_idx

        # Remove existing dynamic inputs
        for i in range(len(self.inputs) - 1, -1, -1):
            if self.inputs[i].name.startswith("Response "):
                self.inputs.remove(self.inputs[i])
        
        # Add new inputs for each spatial point
        for i, point in enumerate(self.spatial_points):
            input_name = f"Response {i+1:02d} ({point.azimuth:.0f}°, {point.elevation:.0f}°)"
            socket = self.inputs.new('AcousticValueNodeSocket', input_name)
            socket.identifier = f"response_{i}"
            
            # Store point index in socket for reference
            socket.point_index = i
    
        # Connect nodes
        for i, point in enumerate(self.spatial_points):
            nodetree = bpy.data.node_groups[point.node_tree_name]
            response_node = nodetree.nodes[point.response_node_name]
            nodetree.links.new(response_node.outputs[0], self.inputs[point.link_idx])

    def draw_buttons(self, context, layout):
        """Draw the node UI"""
        # Spatial points list
        row = layout.row()
        row.template_list("SPATIALRESPONSE_UL_Points", "", 
                         self, "spatial_points", 
                         self, "spatial_points_index", 
                         rows=4)
        
        col = row.column(align=True)
        op = col.operator("node.add_spatial_point", text="", icon='ADD')
        op.node_name = self.name
        op.node_tree = self.id_data.name
        
        op = col.operator("node.remove_spatial_point", text="", icon='REMOVE')
        op.node_name = self.name
        op.node_tree = self.id_data.name
        
        col.separator()
        op = col.operator("node.update_spatial_inputs", text="", icon='FILE_REFRESH')
        op.node_name = self.name
        op.node_tree = self.id_data.name
        
        # Interpolation settings
        layout.separator()
        layout.prop(self, "interpolation_method")
        layout.prop(self, "normalize_responses")
        
        # Info about connected responses
        layout.separator()
        box = layout.box()
        box.label(text="Connected Responses:", icon='INFO')
        
        connected_count = 0
        for i, point in enumerate(self.spatial_points):
            # Check if the corresponding input is connected
            input_idx = self.get_input_index_for_point(i)
            if input_idx >= 0 and self.inputs[input_idx].is_linked:
                connected_count += 1
                row = box.row()
                row.label(text=f"Point {i+1}: ", icon='CHECKMARK')
                row.label(text=f"Az={point.azimuth:.0f}°, El={point.elevation:.0f}°")
        
        if connected_count == 0:
            box.label(text="No responses connected", icon='ERROR')
        else:
            box.label(text=f"{connected_count}/{len(self.spatial_points)} responses connected")
    
    def get_input_index_for_point(self, point_index):
        """Get the input socket index for a given point index"""
        for i, socket in enumerate(self.inputs):
            if hasattr(socket, 'point_index') and socket.point_index == point_index:
                return i
        return -1
    
    def update(self):
        """Update the node when connections change"""
        # Update dynamic inputs if needed
        if not self.dynamic_inputs_initialized or len(self.inputs) != len(self.spatial_points):
            self.update_dynamic_inputs()
            self.dynamic_inputs_initialized = True
        
    def free(self):
        """Clean up when node is deleted"""
        self.dynamic_inputs_initialized = False

classes.append(SpatialFrequencyResponseNode)
