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

classes = []

def get_acoustic_domain_bounds():
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

def is_point_inside_domain(point):
    """Check if a point is inside the acoustic domain"""
    min_co, max_co = get_acoustic_domain_bounds()
    if min_co is None or max_co is None:
        return True  # No domain defined, allow placement anywhere

    return (min_co.x <= point.x <= max_co.x and
            min_co.y <= point.y <= max_co.y and
            min_co.z <= point.z <= max_co.z)

def create_boundary_empties(center_obj, num_channels, radius):
    """Create boundary empties around the center object"""
    bpy.ops.object.select_all(action='DESELECT')
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

        # Add pbraudio properties
        scene = bpy.context.scene
        if hasattr(scene, 'pbraudio') and scene.pbraudio.cache_path:
            cache_path = scene.pbraudio.cache_path
            if cache_path.startswith('//'):
                cache_path = bpy.path.abspath(cache_path)
            boundary_empty.pbraudio.source = True
            boundary_empty.pbraudio.source_type = 'SPHERE'
            boundary_empty.pbraudio.environment_boundary = True
            boundary_empty.pbraudio.source_file = f"{cache_path}/Environments/{center_obj.name}/{boundary_empty.name}.raw"

        # Make non-selectable
        boundary_empty.hide_select = True

        # Link to collection
        bpy.context.collection.objects.link(boundary_empty)

        # Parent to center empty
        boundary_empty.parent = center_obj

        # Store reference
        boundary_empties.append(boundary_empty)

    return boundary_empties

def update_boundary_count(center_obj, new_channel_count):
    """Update the number of boundary empties based on channel count"""
    radius = center_obj.pbraudio.environment_size
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
            boundary_empty.parent = center_obj
            boundary_empty.hide_select = True

            # Link to collection
            bpy.context.collection.objects.link(boundary_empty)

            current_boundaries.append(boundary_empty)

    # Update the stored boundary names
    center_obj["pbraudio_boundary_empties"] = [obj.name for obj in current_boundaries[:new_channel_count]]

    # Update positions for all boundaries
    update_boundary_positions(center_obj, current_boundaries[:new_channel_count], radius)

def update_boundary_positions(center_obj, boundary_empties, radius):
    """Update boundary positions based on center object location and domain constraints"""
    min_co, max_co = get_acoustic_domain_bounds()

    for i, boundary in enumerate(boundary_empties):
        # Calculate original relative position
        golden_angle = math.pi * (3 - math.sqrt(5))
        y = 1 - (i / (len(boundary_empties) - 1)) * 2 if len(boundary_empties) > 1 else 0
        r = math.sqrt(1 - y * y)
        theta = golden_angle * i

        x = math.cos(theta) * r
        z = math.sin(theta) * r

        # Calculate LOCAL position (relative to parent)
        local_position = mathutils.Vector((x, y, z)) * radius

        # If we need to constrain to domain, we should update the world position
        # and then convert back to local
        if min_co is not None and max_co is not None:
            # Calculate world position
            world_position = center_obj.matrix_world @ local_position

            # Check if inside domain
            if not is_point_inside_domain(world_position):
                # Find intersection with domain along the radial direction

                direction = (world_position - center_obj.location).normalized()

                # Test multiple distances to find maximum allowed
                max_allowed_radius = radius
                for test_radius in range(int(radius * 100), 0, -1):
                    test_position = center_obj.location + direction * (test_radius / 100.0)
                    if is_point_inside_domain(test_position):
                        max_allowed_radius = test_radius / 100.0
                        break

                # Calculate new local position
                new_local_position = direction * max_allowed_radius
                boundary.location = new_local_position
