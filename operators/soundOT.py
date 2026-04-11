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
import mathutils
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, StringProperty, EnumProperty
from bpy_extras.object_utils import AddObjectHelper

from ..utils import environment_json
from ..utils.common import update_boundary_positions, get_acoustic_domain_bounds, is_point_inside_domain, create_boundary_empties

classes = []

class PBRAUDIO_OT_add_spherical_source(Operator, AddObjectHelper):
    """Add a spherical sound source"""
    bl_idname = "object.pbraudio_add_spherical_source"
    bl_label = "Spherical Source"
    bl_description = "Add a spherical sound source"
    bl_options = {'REGISTER', 'UNDO'}

    radius: FloatProperty(
        name="Radius",
        description="Radius of the spherical source",
        default=0.25,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    def execute(self, context):
        # Deselect All
        bpy.ops.object.select_all(action='DESELECT')
        # Create empty object
        empty = bpy.data.objects.new("SphericalSource", None)
        empty.empty_display_type = 'SPHERE'
        empty.empty_display_size = self.radius
        empty.location = self.location

        # Link to collection
        context.collection.objects.link(empty)

        # Set as active object
        context.view_layer.objects.active = empty
        empty.select_set(True)

        # Add pbrAudio properties
        if not hasattr(empty, 'pbraudio'):
            bpy.ops.object.pbraudio_add_properties()

        # Configure as source
        empty.pbraudio.source = True
        empty.pbraudio.source_type = 'SPHERE'
        empty.show_axis = True

        # Create new pbrAudio node tree
        nodetree = bpy.data.node_groups.new(self.name, 'AcousticNodeTree')
        nodetree.pbraudio_type = 'SOUND'

        # Set up default nodes
        output_node = nodetree.nodes.new('SoundOutputNode')
        output_node.location = (300, 0)

#        shader_node = nodetree.nodes.new('AcousticShaderNode')
#        shader_node.location = (0, 0)

#        # Connect nodes
#        nodetree.links.new(shader_node.outputs[0], output_node.inputs[0])

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
        self.report({'INFO'}, f"Added spherical source with radius {self.radius}")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.location = context.scene.cursor.location
        return self.execute(context)

classes.append(PBRAUDIO_OT_add_spherical_source)

class PBRAUDIO_OT_add_planar_source(Operator, AddObjectHelper):
    """Add a planar sound source"""
    bl_idname = "object.pbraudio_add_planar_source"
    bl_label = "Planar Source"
    bl_description = "Add a planar sound source"
    bl_options = {'REGISTER', 'UNDO'}

    width: FloatProperty(
        name="Width",
        description="Width of the planar source",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    height: FloatProperty(
        name="Height",
        description="Height of the planar source",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    def execute(self, context):
        # Deselect All
        bpy.ops.object.select_all(action='DESELECT')
        # Create empty object
        empty = bpy.data.objects.new("PlanarSource", None)
        empty.empty_display_type = 'CUBE'
        empty.empty_display_size = max(self.width, self.height) / 2
        empty.location = self.location

        # Scale to match width and height (cube is 2x2x2 units)
        empty.scale = (self.width / 2, self.height / 2, 0.01)

        # Link to collection
        context.collection.objects.link(empty)

        # Set as active object
        context.view_layer.objects.active = empty
        empty.select_set(True)

        # Add pbrAudio properties
        if not hasattr(empty, 'pbraudio'):
            bpy.ops.object.pbraudio_add_properties()

        # Configure as source
        empty.pbraudio.source = True
        empty.pbraudio.source_type = 'PLANE'
        empty.show_axis = True

        # Create new pbrAudio node tree
        nodetree = bpy.data.node_groups.new(self.name, 'AcousticNodeTree')
        nodetree.pbraudio_type = 'SOUND'

        # Set up default nodes
        output_node = nodetree.nodes.new('SoundOutputNode')
        output_node.location = (300, 0)

#        shader_node = nodetree.nodes.new('AcousticShaderNode')
#        shader_node.location = (0, 0)

#        # Connect nodes
#        nodetree.links.new(shader_node.outputs[0], output_node.inputs[0])

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
        self.report({'INFO'}, f"Added planar source with size {self.width}x{self.height}")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.location = context.scene.cursor.location
        return self.execute(context)

classes.append(PBRAUDIO_OT_add_planar_source)

class PBRAUDIO_OT_resize_output(Operator, AddObjectHelper):
    """Resize a sound output"""
    bl_idname = "object.pbraudio_resize_output"
    bl_label = "Resize Output"
    bl_description = "Resize a sound output"
    bl_options = {'REGISTER', 'UNDO'}

    size: FloatProperty(
        name="Size",
        description="Size of spherical output",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    def execute(self, context):
        empty = context.object
        empty.empty_display_size = self.size

        return {'FINISHED'}
classes.append(PBRAUDIO_OT_resize_output)

class PBRAUDIO_OT_resize_source(Operator, AddObjectHelper):
    """Resize a sound source"""
    bl_idname = "object.pbraudio_resize_source"
    bl_label = "Resize Source"
    bl_description = "Resize a sound source"
    bl_options = {'REGISTER', 'UNDO'}

    size: FloatProperty(
        name="Size",
        description="Size of spherical source",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    width: FloatProperty(
        name="Width",
        description="Width of the planar source",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    height: FloatProperty(
        name="Height",
        description="Height of the planar source",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    def execute(self, context):
        empty = context.object
        if empty.pbraudio.source_type == 'SPHERE':
            empty.empty_display_size = self.size
        elif empty.pbraudio.source_type == 'PLANE':
            empty.empty_display_size = max(self.width, self.height) / 2
            # Scale to match width and height (cube is 2x2x2 units)
            empty.scale = (self.width / 2, self.height / 2, 0.01)

        return {'FINISHED'}

classes.append(PBRAUDIO_OT_resize_source)

class PBRAUDIO_OT_add_camera_nodetree(Operator, AddObjectHelper):
    """Add a sound output (microphone/listener)"""
    bl_idname = "object.pbraudio_add_camera_nodetree"
    bl_label = "Add Camera Output NodeTree"
    bl_description = "Add a sound output nodetree for camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create new pbrAudio node tree
        nodetree = bpy.data.node_groups.new("CameraSoundOutput", 'AcousticNodeTree')
        nodetree.pbraudio_type = 'SOUND'

        # Set up default nodes
        input_node = nodetree.nodes.new('SoundOutputNode')
        input_node.location = (300, 0)

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
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_add_camera_nodetree)

class PBRAUDIO_OT_add_sound_output(Operator, AddObjectHelper):
    """Add a sound output (microphone/listener)"""
    bl_idname = "object.pbraudio_add_sound_output"
    bl_label = "Sound Output"
    bl_description = "Add a sound output (microphone/listener)"
    bl_options = {'REGISTER', 'UNDO'}

    output_type: EnumProperty(
        name="Type",
        items=[
            ('MONO', "Mono", "Mono sound output"),
            ('AMBI', "Ambisonic", "Ambisonic sound output"),
        ],
        default='MONO'
    )

    ambisonic_order: EnumProperty(
        name="Order",
        description="Ambisonic order (only for ambisonic type)",
        items=[
            ('0', "Zero", "Zero order"),
            ('1', "First", "First order"),
            ('2', "Second", "Second order"),
            ('3', "Third", "Third order"),
        ],
        default='1'
    )

    mono_mic_type: EnumProperty(
        name="Microphone Type",
        description="Microphone type (only for mono type)",
        items=[
            ('OMNIDIRECTIONAL', "Omnidirectional", "Omnidirectional Microphone"),
            ('CARDIOID', "Cardioid", "Cardioid Microphone"),
            ('HYPERCARDIOID', "Hypercardioid", "Hypercardioid Microphone"),
            ('FIGURE_8', "Figure 8", "Figure 8 Microphone"),
        ],
        default='OMNIDIRECTIONAL'
    )

    size: FloatProperty(
        name="Size",
        description="Display size of the output",
        default=0.25,
        min=0.01,
        max=10.0,
        unit='LENGTH'
    )

    def execute(self, context):
        # Deselect All
        bpy.ops.object.select_all(action='DESELECT')
        # Create empty object
        empty = bpy.data.objects.new("SoundOutput", None)
        empty.empty_display_type = 'CONE'
        empty.empty_display_size = self.size
        empty.location = self.location

        # Link to collection
        context.collection.objects.link(empty)

        # Set as active object
        context.view_layer.objects.active = empty
        empty.select_set(True)

        # Add pbrAudio properties
        if not hasattr(empty, 'pbraudio'):
            bpy.ops.object.pbraudio_add_properties()

        # Configure as output
        empty.pbraudio.output = True
        empty.pbraudio.output_type = self.output_type

        # Set specific properties based on type
        if self.output_type == 'AMBI':
            empty.pbraudio.ambisonic_order = self.ambisonic_order
        else:  # MONO
            empty.pbraudio.mono_mic_type = self.mono_mic_type

        empty.show_axis = True

        # Create new pbrAudio node tree
        nodetree = bpy.data.node_groups.new("SoundOutput", 'AcousticNodeTree')
        nodetree.pbraudio_type = 'SOUND'

        # Set up default nodes
        input_node = nodetree.nodes.new('SoundOutputNode')
        input_node.location = (300, 0)

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

        self.report({'INFO'}, f"Added sound output ({self.output_type})")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.location = context.scene.cursor.location
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "output_type")

        if self.output_type == 'AMBI':
            layout.prop(self, "ambisonic_order")
        else:  # MONO
            layout.prop(self, "mono_mic_type")

        layout.prop(self, "size")

classes.append(PBRAUDIO_OT_add_sound_output)

class PBRAUDIO_OT_add_world_environment(Operator, AddObjectHelper):
    """Add a world environment sphere with boundary empties"""
    bl_idname = "object.pbraudio_add_world_environment"
    bl_label = "World Environment"
    bl_description = "Add a world environment sphere with boundary empties"
    bl_options = {'REGISTER', 'UNDO'}

    sphere_radius: FloatProperty(
        name="Sphere Radius",
        description="Radius of the environment sphere",
        default=1.0,
        min=0.1,
        max=100.0,
        unit='LENGTH'
    )

    number_channels: IntProperty(
        name="Number of Channels",
        description="Number of boundary empties (channels)",
        default=8,
        min=1,
        max=64
    )

    def execute(self, context):
        # Check if point is inside acoustic domain
        if not is_point_inside_domain(self.location):
            self.report({'ERROR'}, "World Environment must be placed inside the Acoustic Domain")
            return {'CANCELLED'}

        # Create central empty
        center_empty = bpy.data.objects.new("WorldEnvironment", None)
        center_empty.empty_display_type = 'SPHERE'
        center_empty.empty_display_size = 0.1
        center_empty.location = self.location
        center_empty.show_axis = True

        # Link to collection
        context.collection.objects.link(center_empty)

        # Add pbrAudio properties
        if not hasattr(center_empty, 'pbraudio'):
            bpy.ops.object.pbraudio_add_properties()

        # Configure as environment
        center_empty.pbraudio.environment = True
        center_empty.pbraudio.environment_size = self.sphere_radius
        center_empty.pbraudio.environment_chanels = self.number_channels

        # Create boundary empties
        boundary_empties = create_boundary_empties(
            center_empty,
            self.number_channels,
            self.sphere_radius
        )

        # Store boundary references in a custom property
        center_empty["pbraudio_boundary_empties"] = [obj.name for obj in boundary_empties]

        # Add handler for location updates
        center_empty.pbraudio.environment_size = self.sphere_radius

        # Save environment data to JSON
        if hasattr(context.scene, 'pbraudio') and context.scene.pbraudio.cache_path:
            cache_path = context.scene.pbraudio.cache_path
            if cache_path.startswith('//'):
                cache_path = bpy.path.abspath(cache_path)
            json_path = environment_json.save_environment_json(center_empty, cache_path)
            if json_path:
                self.report({'INFO'}, f"Environment JSON saved: {json_path}")

        # Set center empty as active
        context.view_layer.objects.active = center_empty
        center_empty.select_set(True)

        self.report({'INFO'}, f"Added world environment with {self.number_channels} boundary empties")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.location = context.scene.cursor.location
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sphere_radius")
        layout.prop(self, "number_channels")

        # Show warning if outside domain
        if not is_point_inside_domain(self.location):
            layout.label(text="Warning: Outside Acoustic Domain", icon='ERROR')

classes.append(PBRAUDIO_OT_add_world_environment)

class PBRAUDIO_OT_remove_world_environment(Operator):
    """Remove a world environment and its boundary empties"""
    bl_idname = "object.pbraudio_remove_world_environment"
    bl_label = "Remove World Environment"
    bl_description = "Remove world environment and its boundary empties"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                hasattr(context.active_object, 'pbraudio') and
                context.active_object.pbraudio.environment)

    def execute(self, context):
        obj = context.active_object

        # Clean up boundary empties
        if "pbraudio_boundary_empties" in obj:
            boundary_names = obj["pbraudio_boundary_empties"]

            for name in boundary_names:
                boundary_obj = bpy.data.objects.get(name)
                if boundary_obj:
                    bpy.data.objects.remove(boundary_obj, do_unlink=True)

            # Remove the custom property
            del obj["pbraudio_boundary_empties"]

        # Remove the environment object
        bpy.data.objects.remove(obj, do_unlink=True)

        self.report({'INFO'}, "Removed world environment and its boundaries")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_remove_world_environment)

class PBRAUDIO_OT_add_properties(Operator):
    """Add pbrAudio properties to selected object"""
    bl_idname = "object.pbraudio_add_properties"
    bl_label = "Add pbrAudio Properties"
    bl_description = "Add pbrAudio properties to selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj:
            # Ensure pbrAudio properties exist
            if not hasattr(obj, 'pbraudio'):
                # This will be handled by the property registration
                # We just need to ensure the property group is initialized
                pass

            self.report({'INFO'}, f"Added pbrAudio properties to {obj.name}")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_add_properties)
