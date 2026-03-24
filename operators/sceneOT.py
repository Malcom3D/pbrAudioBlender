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

import io
import os, sys
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
def pbrAudio_physics(config_file: str):
    from physicsSolver import EntityManager
    from physicsSolver import physicsEngine
    em = EntityManager(config_file)
    phys = physicsEngine(em)
    phys.bake()
    return {"processed": True}

@run_async
def pbrAudio_prebake(config_file: str):
    from physicsSolver import EntityManager
    from rigidBody import rigidBodyEngine
    em = EntityManager(config_file)
    rbs = rigidBodyEngine(em)
    rbs.prebake()
    return {"processed": True}

@run_async
def pbrAudio_bake(config_file: str):
    from physicsSolver import EntityManager
    from rigidBody import rigidBodyEngine
    em = EntityManager(config_file)
    rbs = rigidBodyEngine(em)
    rbs.bake()
    return {"processed": True}

@run_async
def pbrAudio_fracture(config_file: str):
    from physicsSolver import EntityManager
    from fractureSound import fractureEngine
    em = EntityManager(config_file)
    fract = fractureEngine(em)
    fract.bake()
    return {"processed": True}

classes = []

class PBRAUDIO_OT_fracture(Operator):
    bl_idname = "scene.pbraudio_fracture"
    bl_label = "BakeFracture"
    bl_description = "Bake of fracture data for sound synthesis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'fracture') and not scene.pbraudio.fracture:
            if not scene.pbraudio.bake:
                bpy.ops.scene.pbraudio_bake()
            # Start async processing
            config_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
            status_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/status/fractureEngine/bake"
            process = pbrAudio_fracture(config_file)
            # Monitor completion
            bpy.app.timers.register(lambda: self.check_process(scene, process, status_file), first_interval=1.0)
            self.report({'INFO'}, "Bake of fracture data for sound synthesis started")
        return {'FINISHED'}

    def check_process(self, scene, process, status_file):
        if process.is_alive():
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    self.report({'INFO'}, "Process progress: {f.read()}%")
        else:
            print("Baking of fracture data for sound synthesis completed")
            # Update UI here
            scene.pbraudio.fracture = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_fracture)

class PBRAUDIO_OT_bake(Operator):
    bl_idname = "scene.pbraudio_bake"
    bl_label = "Bake"
    bl_description = "Bake of prebaked data for sound synthesis"
    bl_options = {'REGISTER', 'UNDO'}
                
    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'bake') and not scene.pbraudio.bake:
            if not scene.pbraudio.prebake:
                bpy.ops.scene.pbraudio_prebake()
            # Start async processing
            config_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
            status_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/status/rigidBodyEngine/bake"
            process = pbrAudio_bake(config_file)
            # Monitor completion
            bpy.app.timers.register(lambda: self.check_process(scene, process, status_file), first_interval=1.0)
            self.report({'INFO'}, "Bake of prebaked data for sound synthesis started")
        return {'FINISHED'}

    def check_process(self, scene, process, status_file):
        if process.is_alive():
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    self.report({'INFO'}, "Process progress: {f.read()}%")
        else:
            print("Baking of prebaked data for sound synthesis completed")
            # Update UI here
            scene.pbraudio.bake = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_bake)

class PBRAUDIO_OT_prebake(Operator):
    bl_idname = "scene.pbraudio_prebake"
    bl_label = "PreBake"
    bl_description = "PreBake baked physics dynamics for sound synthesis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'prebake') and not scene.pbraudio.prebake:
            if not scene.pbraudio.physics:
                bpy.ops.scene.pbraudio_physics()
            # Start async processing
            config_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
            status_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/status/rigidBodyEngine/prebake"
            process = pbrAudio_prebake(config_file)
            # Monitor completion
            bpy.app.timers.register(lambda: self.check_process(scene, process, status_file), first_interval=1.0)
            self.report({'INFO'}, "Prebaking of baked physics dynamics for sound synthesis started")
        return {'FINISHED'}

    def check_process(self, scene, process, status_file):
        if process.is_alive():
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    self.report({'INFO'}, "Process progress: {f.read()}%")
        else:
            print("Prebaking of baked physics dynamics for sound synthesis completed")
            # Update UI here
            scene.pbraudio.prebake = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_prebake)

class PBRAUDIO_OT_physics(Operator):
    bl_idname = "scene.pbraudio_physics"
    bl_label = "BakePhysics"
    bl_description = "Bake physics"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'physics'):
            if not scene.pbraudio.physics:
                decimals = 18
                fps = scene.render.fps
                fps_base = scene.render.fps_base
                start_frame = scene.frame_start
                end_frame = scene.frame_end

                bpy.ops.object.select_all(action='SELECT')
#                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                bpy.ops.object.select_all(action='DESELECT')

                self.report({'INFO'}, "Physics dynamics bake processing started")
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
                status_file = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}/status/physicsEngine/bake"
                process = pbrAudio_physics(config_file)

                # Monitor completion
                bpy.app.timers.register(lambda: self.check_process(scene, process, status_file), first_interval=1.0)
        return {'FINISHED'}

    def check_process(self, scene, process, status_file):
        if process.is_alive():
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    progress_status = f.read()
                    print(f"Process progress: {progress_status}%")
        else:
            self.report({'INFO'}, "Physics dynamics bake processing completed")
            # Update UI here
            scene.pbraudio.physics = True
            scene.pbraudio.cache_status = True
            return None
        return 1.0

classes.append(PBRAUDIO_OT_physics)

class PBRAUDIO_OT_clear_cache(Operator):
    bl_idname = "scene.pbraudio_clear_cache"
    bl_label = "Clear Cache"
    bl_description = "Clear Collision Cache"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'cache_status'):
            if scene.pbraudio.cache_status:
                scene.pbraudio.bake = False
                scene.pbraudio.prebake = False
                scene.pbraudio.physics = False
                scene.pbraudio.cache_status = False
                self.report({'INFO'}, f"Collision cache for {scene.pbraudio.collision_collection.name_full} cleared")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_clear_cache)
