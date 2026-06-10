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
from mathutils import Vector
from bpy.props import StringProperty, FloatProperty, PointerProperty
from bpy.types import Operator

classes = []

class PBRAUDIO_OT_material_add(Operator):
    bl_idname = "material.pbraudio_add"
    bl_label = "New pbrAudio material"
    bl_description = "Create a new acoustic material node tree"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(
        name="Name",
        description="Name of the pbrAudio node tree",
        default="AcousticMaterial"
    )

    def execute(self, context):
        # Create new pbrAudio node tree
        nodetree = bpy.data.node_groups.new(self.name, 'AcousticNodeTree')
        nodetree.pbraudio_type = 'OBJECT'

        # Set up default nodes
        output_node = nodetree.nodes.new('AcousticMaterialOutputNode')
        output_node.location = (300, 0)

        shader_node = nodetree.nodes.new('AcousticShaderNode')
        shader_node.location = (0, 0)
    
        # Connect nodes
        nodetree.links.new(shader_node.outputs[0], output_node.inputs[0])
        
        # Link to active object if available
        if context.active_object and context.active_object.pbraudio:
            context.active_object.pbraudio.nodetree = nodetree
        
        # Set the node tree as active in the node editor
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        space.node_tree = nodetree
                        break

        self.report({'INFO'}, f"Created pbrAudio node tree: {nodetree.name}")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_material_add)

class PBRAUDIO_OT_copy_material_to_selected(Operator):
    """Copy acoustic material node tree to selected objects"""
    bl_idname = "material.pbraudio_copy_to_selected"
    bl_label = "Copy Acoustic Material to Selected"
    bl_description = "Copy the acoustic node tree from the active object to all selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                hasattr(context.active_object, 'pbraudio') and
                context.active_object.pbraudio.nodetree is not None)

    def execute(self, context):
        active_obj = context.active_object
        
        # Get the source node tree
        source_nodetree = active_obj.pbraudio.nodetree
        if not source_nodetree:
            self.report({'ERROR'}, "Active object has no acoustic node tree")
            return {'CANCELLED'}
        
        # Count objects that will receive the copy
        copied_count = 0
        skipped_count = 0
        
        # Iterate through all selected objects
        for obj in context.selected_objects:
            # Skip the active object itself
            if obj == active_obj:
                continue
            
            # Skip objects that don't have pbraudio properties
            if not hasattr(obj, 'pbraudio'):
                continue
            
            # Skip objects that are not mesh type (materials only apply to mesh objects)
            if obj.type != 'MESH':
                continue
            
            # Create a copy of the node tree
            new_nodetree = source_nodetree.copy()
            
            # Rename the copy to reflect the target object
            new_nodetree.name = f"{source_nodetree.name}_{obj.name}"
            
            # Assign the copied node tree to the target object
            obj.pbraudio.nodetree = new_nodetree
            
            copied_count += 1
        
        if copied_count > 0:
            self.report({'INFO'}, f"Copied acoustic material to {copied_count} object(s)")
        else:
            self.report({'WARNING'}, "No suitable objects found to copy to")
        
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_copy_material_to_selected)
