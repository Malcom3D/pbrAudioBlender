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
from bpy.app.handlers import persistent
from bpy.utils import register_class, unregister_class

from ..utils import environment_json

classes = []

#from . import playback 

#for mod in (playback, ):
#    classes += mod.classes

# Global to store the the pbraudio handlers reference
pbraudio_handler = []

# handler to set shader in 3D View to SOLID
@persistent
def material_shader_only_handler(scene):
    if scene.render.engine == 'PBRAUDIO':
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'

#pbraudio_handler.append(bpy.app.handlers.depsgraph_update_post.append(material_shader_only_handler))

@persistent
def select_nodetree_handler(scene):
    if scene.render.engine == 'PBRAUDIO':
        if not bpy.context.active_object == None and hasattr(bpy.context, 'active_object'):
            object = bpy.context.active_object
            treeType = 'AcousticNodeTree'
            nodeTreeName = None

            if hasattr(object, 'pbraudio') and not object.pbraudio.environment:
                if object.pbraudio.source or object.pbraudio.output or object.type == 'CAMERA':
                    scene.acoustic_node_editor_props.acoustic_shader_type = 'SOUND'
                    if hasattr(object.pbraudio.nodetree, 'name'):
                        nodeTreeName = object.pbraudio.nodetree.name

                for world in bpy.data.worlds:
                    if hasattr(world.pbraudio, 'acoustic_domain'):
                        AcousticDomain = world.pbraudio.acoustic_domain

                if object == AcousticDomain:
                    scene.acoustic_node_editor_props.acoustic_shader_type = 'WORLD'
                    if hasattr(world.pbraudio.nodetree, 'name'):
                        nodeTreeName = world.pbraudio.nodetree.name

                elif object.type in ['MESH', 'CURVE', 'SURFACE']:
                    scene.acoustic_node_editor_props.acoustic_shader_type = 'OBJECT'
                    if hasattr(object.pbraudio.nodetree, 'name'):
                        nodeTreeName = object.pbraudio.nodetree.name

                for area in bpy.context.screen.areas:
                    if area.type == "NODE_EDITOR":
                        for space in area.spaces:
                            if space.type == "NODE_EDITOR" and not space.pin:
                                space.tree_type = treeType
                                if nodeTreeName is not None:
                                    space.node_tree = bpy.data.node_groups[nodeTreeName]

#pbraudio_handler.append(bpy.app.handlers.depsgraph_update_post.append(select_nodetree_handler))

@persistent
def update_world_environment_boundaries(scene):
    """Update boundary empties when world environment moves"""
    for obj in bpy.data.objects:
        if hasattr(obj, 'pbraudio') and obj.pbraudio.environment:
            # Check if we have boundary empties stored
            if "pbraudio_boundary_empties" in obj:
                boundary_names = obj["pbraudio_boundary_empties"]
                boundary_empties = []
                
                # Get actual boundary objects
                for name in boundary_names:
                    boundary_obj = bpy.data.objects.get(name)
                    if boundary_obj:
                        boundary_empties.append(boundary_obj)
                
                if boundary_empties:
                    # Update boundary positions
                    from ..operators.soundOT import PBRAUDIO_OT_add_world_environment
                    op = PBRAUDIO_OT_add_world_environment
                    
                    # Get current radius from object property
                    radius = obj.pbraudio.environment_size
                    
                    # Update positions
                    op.update_boundary_positions(obj, boundary_empties, radius)
            
            # Save environment data to JSON
            if hasattr(scene, 'pbraudio') and scene.pbraudio.cache_path:
                cache_path = scene.pbraudio.cache_path
                if cache_path.startswith('//'):
                    cache_path = bpy.path.abspath(cache_path)
                environment_json.save_environment_json(obj, cache_path)

@persistent
def save_environment_on_property_update(scene):
    """Save environment JSON when environment properties change"""
    for obj in bpy.data.objects:
        if hasattr(obj, 'pbraudio') and obj.pbraudio.environment:
            # Check if properties have changed
            if "pbraudio_last_environment_data" not in obj:
                obj["pbraudio_last_environment_data"] = {}
            
            current_data = {
                "file": obj.pbraudio.environment_file,
                "channels": obj.pbraudio.environment_chanels,
                "radius": obj.pbraudio.environment_size,
                "location": tuple(obj.location),
                "boundary_count": len(obj["pbraudio_boundary_empties"]) if "pbraudio_boundary_empties" in obj else 0
            }
            
            last_data = obj["pbraudio_last_environment_data"]
            
            # Check if any property has changed
            if current_data != last_data:
                # Save JSON
                if hasattr(scene, 'pbraudio') and scene.pbraudio.cache_path:
                    cache_path = scene.pbraudio.cache_path
                    if cache_path.startswith('//'):
                        cache_path = bpy.path.abspath(cache_path)
                    environment_json.save_environment_json(obj, cache_path)
                
                # Update last data
                obj["pbraudio_last__environment_data"] = current_data

def register():
    global pbraudio_handler
    for cls in classes:
        register_class(cls)

    # Register handlers
    bpy.app.handlers.depsgraph_update_post.append(material_shader_only_handler)
    bpy.app.handlers.depsgraph_update_post.append(select_nodetree_handler)
    bpy.app.handlers.depsgraph_update_post.append(update_world_environment_boundaries)
    bpy.app.handlers.frame_change_post.append(update_world_environment_boundaries)
    bpy.app.handlers.depsgraph_update_post.append(save_environment_on_property_update)

def unregister():
    global pbraudio_handler
    # Remove handlers
    if material_shader_only_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(material_shader_only_handler)
    if select_nodetree_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(select_nodetree_handler)
    if update_world_environment_boundaries in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_world_environment_boundaries)
    if update_world_environment_boundaries in bpy.app.handlers.frame_change_post:
        bpy.app.handlerslers.frame_change_post.remove(update_world_environment_boundaries)
    if save_environment_on_property_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(save_environment_on_property_update)

    for cls in reversed(classes):
        unregister_class(cls)
