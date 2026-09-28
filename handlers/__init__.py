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

classes = []

@persistent
def select_nodetree_handler(scene):
    if scene.render.engine == 'PBRAUDIO':
        if not bpy.context.screen == None and hasattr(bpy.context.screen, 'areas'):
            for area in bpy.context.screen.areas:
                if area.type == "NODE_EDITOR":
                    for space in area.spaces:
                        if space.type == "NODE_EDITOR" and not space.pin:
                            space.node_tree = None

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

@persistent
def companion_render_handler(scene):
    """
    This handler is called by Blender after a render is complete.
    It checks if a companion render is pending and, if so, starts it.
    """
    if not hasattr(scene, 'pbraudio') or not scene.pbraudio.is_companion_render_pending:
        return

    # Reset the flag immediately to prevent re-triggering
    scene.pbraudio.is_companion_render_pending = False

    print("Companion render handler triggered. Starting companion render...")
    
    companion_engine = scene.pbraudio.companion_render_engine
    
    # Switch to the companion engine
    scene.render.engine = companion_engine
    
    # Render the animation
    try:
        bpy.ops.render.render(animation=True)
    except Exception as e:
        print(f"Companion render failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Switch back to the pbrAudio engine
        scene.render.engine = 'PBRAUDIO'
        
        # Invalidate the UI to reflect the engine change
        for area in bpy.context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()

def register():
    for cls in classes:
        register_class(cls)

    # Register handlers
    bpy.app.handlers.depsgraph_update_post.append(select_nodetree_handler)
    bpy.app.handlers.render_complete.append(companion_render_handler)

def unregister():
    if select_nodetree_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(select_nodetree_handler)
    if companion_render_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(companion_render_handler)

    for cls in reversed(classes):
        unregister_class(cls)
