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
        nodetree = bpy.data.node_groups.new(self.name, 'AcousticMaterialNodeTree')

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
        for area in bpy.context.screen.areas:
            if area.type == 'NODE_EDITOR':
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        space.node_tree = nodetree
                        break

        self.report({'INFO'}, f"Created pbrAudio node tree: {nodetree.name}")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_material_add)
