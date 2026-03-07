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
import time
import multiprocessing
from functools import wraps
from bpy.types import Operator

from ..exporter.collision_export import MeshToNumpyExporter

def run_async(func):
    """Decorator to run function in background process"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create process
        process = multiprocessing.Process(
            target=func,
            args=args,
            kwargs=kwargs
        )
        process.start()
        
        # Return process object for monitoring
        return process
    
    return wrapper

@run_async
def pbrAudio_prebake(config_file: str):
    from rigidBody import rigidBody
    rbs = rigidBody(config_file)
    rbs.prebake()
    return {"processed": True}

@run_async
def pbrAudio_bake(config_file: str):
    from rigidBody import rigidBody
    rbs = rigidBody(config_file)
    rbs.bake()
    return {"processed": True}

@run_async
def pbrAudio_prerender(config_file: str):
    from rigidBody import rigidBody
    rbs = rigidBody(config_file)
    rbs.prerender()
    return {"processed": True}

@run_async
def pbrAudio_render(config_file: str):
    from rigidBody import rigidBody
    rbs = rigidBody(config_file)
    rbs.render()
    return {"processed": True}

classes = []

class PBRAUDIO_OT_Render(Operator):
    bl_idname = "scene.pbraudio_render"
    bl_label = "Render"
    bl_description = "Render preRendered sound from dynamics and animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'render'):
            if scene.pbraudio.prerender and not scene.pbraudio.render:
                # Start async processing
                config_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
                process = pbrAudio_render(config_file)
                # Monitor completion
                bpy.app.timers.register(lambda: self.check_process(scene, process), first_interval=1.0)
                self.report({'INFO'}, "Started async render processing")
        return {'FINISHED'}
    
    def check_process(self, scene, process):
        if not process.is_alive():
            print("Async processing completed")
            # Update UI here
            scene.pbraudio.cache_status = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_Render)

class PBRAUDIO_OT_preRender(Operator):
    bl_idname = "scene.pbraudio_prerender"
    bl_label = "preRender"
    bl_description = "PreRender baked sound from dynamics and animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene 
        if hasattr(scene.pbraudio, 'prerender'):
            if scene.pbraudio.bake and not scene.pbraudio.prerender:
                # Start async processing
                config_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
                process = pbrAudio_prerender(config_file)
                # Monitor completion
                bpy.app.timers.register(lambda: self.check_process(scene, process), first_interval=1.0)
                self.report({'INFO'}, "Started async prerender processing")
        return {'FINISHED'}

    def check_process(self, scene, process):
        if not process.is_alive():
            print("Async processing completed")
            # Update UI here
            scene.pbraudio.prerender = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_preRender)

class PBRAUDIO_OT_bake(Operator):
    bl_idname = "scene.pbraudio_bake"
    bl_label = "Bake"
    bl_description = "Bake prebaked sound from dynamics and animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'bake'):
            if scene.pbraudio.prebake and not scene.pbraudio.bake:
                # Start async processing
                config_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
                process = pbrAudio_bake(config_file)
                # Monitor completion
                bpy.app.timers.register(lambda: self.check_process(scene, process), first_interval=1.0)
                self.report({'INFO'}, "Started async bake processing")
        return {'FINISHED'}

    def check_process(self, scene, process):
        if not process.is_alive():
            print("Async processing completed")
            # Update UI here
            scene.pbraudio.bake = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_bake)

class PBRAUDIO_OT_prebake(Operator):
    bl_idname = "scene.pbraudio_prebake"
    bl_label = "preBake"
    bl_description = "Prebake sound"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'prebake'):
            if not scene.pbraudio.prebake and not scene.pbraudio.cache_status:
                decimals = 18
                fps = scene.render.fps
                fps_base = scene.render.fps_base
                start_frame = scene.frame_start
                end_frame = scene.frame_end

                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                bpy.ops.object.select_all(action='DESELECT')

                # Create exporter
                exporter = MeshToNumpyExporter(scene=scene, decimals=decimals)
                for obj in scene.pbraudio.collision_collection.objects.values():
                    # Export animation
                    exporter.export_animation(obj, start_frame, end_frame)
                    obj.select_set(False)

                # Save config
                exporter.save_config()

                # Start async processing
                config_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
                process = pbrAudio_prebake(config_file)

                # Monitor completion
                bpy.app.timers.register(lambda: self.check_process(scene, process), first_interval=1.0)
                self.report({'INFO'}, "Started async prebake processing")
        return {'FINISHED'}

    def check_process(self, scene, process):
        if not process.is_alive():
            print("Async processing completed")
            # Update UI here
            scene.pbraudio.prebake = True
            scene.pbraudio.cache_status = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_prebake)

class PBRAUDIO_OT_clear_cache(Operator):
    bl_idname = "scene.pbraudio_clear_cache"
    bl_label = "Clear Cache"
    bl_description = "Clear Collision Cache"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'cache_status'):
            if scene.pbraudio.cache_status:
                scene.pbraudio.render = False
                scene.pbraudio.prerender = False
                scene.pbraudio.bake = False
                scene.pbraudio.prebake = False
                scene.pbraudio.cache_status = False
                self.report({'INFO'}, f"Collision cache for {scene.pbraudio.collision_collection.name_full} cleared")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_clear_cache)
