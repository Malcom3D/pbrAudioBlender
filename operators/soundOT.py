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
from bpy.props import FloatProperty, IntProperty, StringProperty
from bpy_extras.object_utils import AddObjectHelper

from ..utils import environment_json

classes = []

#class PBRAUDIO_OT_switch_source_type(Operator):
#    """Switch sound source type"""
#    bl_idname = "object.pbraudio_switch_source_type"
#    bl_label = "Switch Source Type"
#    bl_description = "Switch sound source type"
#    bl_options = {'REGISTER', 'UNDO'}
#
#    def execute(self, context):
#        pass
#        empty.empty_display_type = 'SPHERE'
#        empty.pbraudio.source_type = 'SPHERE'
#
#classes.append(PBRAUDIO_OT_switch_source_type)

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

class PBRAUDIO_OT_resize_source(Operator, AddObjectHelper):
    """Resize a sound source"""
    bl_idname = "object.pbraudio_resize_source"
    bl_label = "Resize Source"
    bl_description = "Resize a sound source"
    bl_options = {'REGISTER', 'UNDO'}

    size: FloatProperty(
        name="Width",
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
        # Create empty object
        empty = bpy.data.objects.new("SoundOutput", None)
        empty.empty_display_type = 'SPHERE'
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
        input_node = nodetree.nodes.new('SoundInputNode')
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

    @staticmethod
    def get_acoustic_domain_bounds():
#    def get_acoustic_domain_bounds(self):
        """Get the bounding box of the acoustic domain"""
        for world in bpy.data.worlds:
            if hasattr(world, 'pbraudio') and hasattr(world.pbraudio, 'acoustic_domain'):
                domain = world.pbraudio.acoustic_domain
                if domain:
                    # Get world matrix
                    matrix = domain.matrix_world
                    
                    # Get bounding box corners in world space
                    corners = [matrix @ mathutils.Vector(corner) for corner in domain.bound_box]
                    
                    # Calculate min and max
                    min_co = mathutils.Vector((
                        min(c.x for c in corners),
                        min(c.y for c in corners),
                        min(c.z for c in corners)
                    ))
                    max_co = mathutils.Vector((
                        max(c.x for c in corners),
                        max(c.y for c in corners),
                        max(c.z for c in corners)
                    ))
                    
                    return min_co, max_co
        
        return None, None

    @staticmethod
    def is_point_inside_domain(point):
#    def is_point_inside_domain(self, point):
        """Check if a point is inside the acoustic domain"""
        min_co, max_co = PBRAUDIO_OT_add_world_environment.get_acoustic_domain_bounds()
        if min_co is None or max_co is None:
            return True  # No domain defined, allow placement anywhere
        
        return (min_co.x <= point.x <= max_co.x and
                min_co.y <= point.y <= max_co.y and
                min_co.z <= point.z <= max_co.z)

    def create_boundary_empties(self, center_obj, num_channels, radius):
        """Create boundary empties around the center object"""
        boundary_empties = []
        
        for i in range(num_channels):
            # Calculate spherical coordinates using Fibonacci spiral
            golden_angle = math.pi * (3 - math.sqrt(5))
            y = 1 - (i / (num_channels - 1)) * 2 if num_channels > 1 else 0
            r = math.sqrt(1 - y * y)
            theta = golden_angle * i
            
            x = math.cos(theta) * r
            z = math.sin(theta) * r
            
            # Calculate position relative to center
            position = center_obj.location + mathutils.Vector((x, y, z)) * radius
            
            # Create boundary empty
            boundary_empty = bpy.data.objects.new(f"WorldEnvironment_{i:02d}", None)
            boundary_empty.empty_display_type = 'PLAIN_AXES'
            boundary_empty.empty_display_size = 0.05
            boundary_empty.location = position
            
            # Make non-selectable
            boundary_empty.hide_select = True
            
            # Link to collection
            bpy.context.collection.objects.link(boundary_empty)
            
            # Parent to center empty
            boundary_empty.parent = center_obj
            
            # Store reference
            boundary_empties.append(boundary_empty)
        
        return boundary_empties

    @staticmethod
    def update_boundary_count(center_obj, new_channel_count):
        """Update the number of boundary empties based on channel count"""
        # Get current boundaries
        current_boundaries = []
        if "pbraudio_boundary_empties" in center_obj:
            boundary_names = center_obj["pbraudio_boundary_empties"]
            for name in boundary_names:
                boundary_obj = bpy.data.objects.get(name)
                if boundary_obj:
                    current_boundaries.append(boundary_obj)
        
        current_count = len(current_boundaries)
        
        if new_channel_count == current_count:
            return  # No change needed
        
        # Remove excess boundaries
        if new_channel_count < current_count:
            for i in range(new_channel_count, current_count):
                if i < len(current_boundaries):
                    bpy.data.objects.remove(current_boundaries[i], do_unlink=True)
        
        # Add new boundaries if needed
        elif new_channel_count > current_count:
            radius = center_obj.pbraudio.environment_size
            for i in range(current_count, new_channel_count):
                # Calculate position for new boundary
                golden_angle = math.pi * (3 - math.sqrt(5))
                y = 1 - (i / (new_channel_count - 1)) * 2 if new_channel_count > 1 else 0
                r = math.sqrt(1 - y * y)
                theta = golden_angle * i
                
                x = math.cos(theta) * r
                z = math.sin(theta) * r
                
                # Calculate position relative to center
                position = center_obj.location + mathutils.Vector((x, y, z)) * radius
                
                # Create new boundary empty
                boundary_empty = bpy.data.objects.new(f"WorldEnvironment_{i:02d}", None)
                boundary_empty.empty_display_type = 'PLAIN_AXES'
                boundary_empty.empty_display_size = 0.05
                boundary_empty.location = position
                boundary_empty.hide_select = True
                boundary_empty.parent = center_obj
                
                # Link to collection
                bpy.context.collection.objects.link(boundary_empty)
                
                current_boundaries.append(boundary_empty)
        
        # Update the stored boundary names
        center_obj["pbraudio_boundary_empties"] = [obj.name for obj in current_boundaries[:new_channel_count]]
        
        # Update Update positions for all boundaries
        PBRAUDIO_OT_add_world_environment.update_boundary_positions(center_obj, current_boundaries[:new_channel_count], radius)

#    def update_boundary_positions(self, center_obj, boundary_empties, radius):
    @staticmethod
    def update_boundary_positions(center_obj, boundary_empties, radius):
        """Update boundary positions based on center object location and domain constraints"""
        min_co, max_co = PBRAUDIO_OT_add_world_environment.get_acoustic_domain_bounds()
        
        for i, boundary in enumerate(boundary_empties):
            # Calculate original relative position
            golden_angle = math.pi * (3 - math.sqrt(5))
            y = 1 - (i / (len(boundary_empties) - 1)) * 2 if len(boundary_empties) > 1 else 0
            r = math.sqrt(1 - y * y)
            theta = golden_angle * i
            
            x = math.cos(theta) * r
            z = math.sin(theta) * r
            
#            # Calculate desired position
#            desired_position = center_obj.location + mathutils.Vector((x, y, z)) * radius
            # Calculate LOCAL position (relative to parent)
            local_position = mathutils.Vector((x, y, z)) * radius

            # Update boundary's local position
            boundary.location = local_position
            
#            # Constrain to domain if domain exists
            # If we need to constrain to domain, we should update the world position
            # and then convert back to local
            if min_co is not None and max_co is not None:
                # Calculate world position
                world_position = center_obj.matrix_world @ local_position
#                # Clamp position to domain bounds
#                clamped_position = mathutils.Vector((
#                    max(min_co.x, min(max_co.x, desired_position.x)),
#                    max(min_co.y, min(max_co.y, desired_position.y)),
#                    max(min_co.z, min(max_co.z, desired_position.z))
#                ))
#                
#                # If clamped, adjust radius to keep spherical distribution
#                if clamped_position != desired_position:
                # Check if inside domain
                if not PBRAUDIO_OT_add_world_environment.is_point_inside_domain(world_position):
                    # Find intersection with domain along the radial direction
#                    direction = (desired_position - center_obj.location).normalized()
                    direction = (world_position - center_obj.location).normalized()
                    
                    # Test multiple distances to find maximum allowed
                    max_allowed_radius = radius
                    for test_radius in range(int(radius * 100), 0, -1):
                        test_position = center_obj.location + direction * (test_radius / 100.0)
                        if PBRAUDIO_OT_add_world_environment.is_point_inside_domain(test_position):
                            max_allowed_radius = test_radius / 100.0
                            break
                    
#                    # Use the maximum allowed radius
#                    desired_position = center_obj.location + direction * max_allowed_radius
                    # Calculate new local position
                    new_local_position = direction * max_allowed_radius
                    boundary.location = new_local_position
            
#            # Update boundary position
#            boundary.location = desired_position

    def execute(self, context):
        # Check if point is inside acoustic domain
        if not self.is_point_inside_domain(self.location):
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
        boundary_empties = self.create_boundary_empties(
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
        if not self.is_point_inside_domain(self.location):
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

