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
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        space.node_tree = nodetree
                        break

        self.report({'INFO'}, f"Created pbrAudio node tree: {nodetree.name}")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_material_add)

class PBRAUDIO_OT_point_add(Operator):
    bl_idname = "acoustic.point_add"
    bl_label = "Add Frequency Point"
    bl_description = "Add a new frequency–magnitude point"

    def execute(self, context):
        node = context.node
        if node and hasattr(node, "points"):
            node.points.add()
            node.point_index = len(node.points) - 1
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_point_add)

class PBRAUDIO_OT_point_remove(Operator):
    bl_idname = "acoustic.point_remove"
    bl_label = "Remove Frequency Point"
    bl_description = "Remove the selected point"

    def execute(self, context):
        node = context.node
        if node and hasattr(node, "points") and node.points:
            if node.point_index < len(node.points):
                node.points.remove(node.point_index)
                node.point_index = min(node.point_index, len(node.points) - 1)
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_point_remove)

class PBRAUDIO_OT_generate_curve(Operator):
    bl_idname = "acoustic.generate_curve"
    bl_label = "Generate Curve from Frequency Response"
    bl_description = "Create or update a 2D curve representing the frequency response"

    def execute(self, context):
        node = context.node
        if not node or not hasattr(node, "points"):
            self.report({'ERROR'}, "No frequency response node selected")
            return {'CANCELLED'}

        # Gather points, sort by frequency
        pts = [(p.frequency, p.magnitude) for p in node.points]
        if not pts:
            self.report({'WARNING'}, "No frequency points defined")
            return {'CANCELLED'}

        pts.sort(key=lambda x: x[0])   # ascending frequency

        # Compute 3D coordinates: X = x_offset + x_scale * log10(freq)
        # (skip zero or negative frequencies)
        coords = []
        for freq, mag in pts:
            if freq <= 0:
                continue
            x = node.x_offset + node.x_scale * math.log10(freq)
            y = node.y_scale * mag
            coords.append(Vector((x, y, 0.0)))

        if len(coords) < 2:
            self.report({'WARNING'}, "Need at least two valid points to draw a curve")
            return {'CANCELLED'}

        # -------------------------------------------------------------------
        # Create or update the curve object
        # -------------------------------------------------------------------
        scene = context.scene
        curve_name = "FrequencyResponse"
        # Remove existing object with the same name if present (optional)
        if curve_name in bpy.data.objects:
            old_obj = bpy.data.objects[curve_name]
            bpy.data.objects.remove(old_obj, do_unlink=True)

        # Create new curve data
        curve_data = bpy.data.curves.new(name=curve_name, type='CURVE')
        curve_data.dimensions = '3D'

        # Add a spline and set its points
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(coords) - 1)
        for i, v in enumerate(coords):
            # Curve points use 4D coordinates (x, y, z, weight)
            spline.points[i].co = (v.x, v.y, v.z, 1.0)

        # Create object and link to collection
        curve_obj = bpy.data.objects.new(curve_name, curve_data)
        context.collection.objects.link(curve_obj)

        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        curve_obj.select_set(True)
        context.view_layer.objects.active = curve_obj

        self.report({'INFO'}, f"Curve '{curve_name}' created/updated")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_generate_curve)
