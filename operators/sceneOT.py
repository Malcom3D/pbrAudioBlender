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
import os
import sys
import bpy
import time
import multiprocessing
from functools import wraps
from bpy.types import Operator

from ..exporter.collision_exporter import CollisionExporter

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
def pbrAudio_physics(config_file: str, status_file: str):
    from physicsSolver import EntityManager
    from physicsSolver import physicsEngine
    em = EntityManager(config_file)
    phys = physicsEngine(em)
    phys.bake()

    # Write completion status
    with open(status_file, 'w') as f:
        f.write("100")

    return {"processed": True}

@run_async
def pbrAudio_prebake(config_file: str, status_file: str):
    from physicsSolver import EntityManager
    from rigidBody import rigidBodyEngine
    em = EntityManager(config_file)
    rbs = rigidBodyEngine(em)
    rbs.prebake()

    # Write completion status
    with open(status_file, 'w') as f:
        f.write("100")

    return {"processed": True}

@run_async
def pbrAudio_bake(config_file: str, status_file: str):
    from physicsSolver import EntityManager
    from rigidBody import rigidBodyEngine
    em = EntityManager(config_file)
    rbs = rigidBodyEngine(em)
    rbs.bake()

    # Write completion status
    with open(status_file, 'w') as f:
        f.write("100")

    return {"processed": True}

@run_async
def pbrAudio_fracture(config_file: str, status_file: str):
    from physicsSolver import EntityManager
    from fractureSound import fractureEngine
    em = EntityManager(config_file)
    fract = fractureEngine(em)
    fract.bake()

    # Write completion status
    with open(status_file, 'w') as f:
        f.write("100")

    return {"processed": True}

classes = []

class PBRAUDIO_OT_fracture(Operator):
    bl_idname = "scene.pbraudio_fracture"
    bl_label = "BakeFracture"
    bl_description = "Bake of fracture data for sound synthesis"
    bl_options = {'REGISTER', 'UNDO'}

    def update_progress(self, scene, status_file):
        """Update progress from status file"""
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    progress = f.read().strip()
                    if progress:
                        scene.pbraudio.status_progress = float(progress) / 100
                return True
            except:
                pass
        return False

    def check_completion(self, scene, process, status_file):
        """Update UI"""
        for area in bpy.context.screen.areas:
            area.tag_redraw()
        """Check if the process has completed"""
        if not process.is_alive():
            # Process finished
            scene.pbraudio.shader_processing = False
            scene.pbraudio.fracture = True
            scene.pbraudio.status_progress = 1.0
            self.report({'INFO'}, "Baking of fracture data for sound synthesis completed")
            return None
        else:
            # Update progress
            self.update_progress(scene, status_file)
            # Continue timer
            return 1.0

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'fracture') and not scene.pbraudio.fracture:
            if not scene.pbraudio.bake:
                bpy.ops.scene.pbraudio_bake('EXEC_DEFAULT')
            # Start async processing
            scene.pbraudio.shader_processing = True
            scene.pbraudio.status_progress = 0.0
            export_path = f"{scene.pbraudio.cache_path}"
            if scene.pbraudio.cache_path.startswith('//'):
                export_path = f"{bpy.path.abspath(scene.pbraudio.cache_path)}"
            config_file = f"{export_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
            status_file = f"{export_path}/{scene.pbraudio.collision_collection.name_full}/status/fractureEngine/bake"
            process = pbrAudio_fracture(config_file, status_file)

            # Monitor completion
            bpy.app.timers.register(lambda: self.check_completion(scene, process, status_file), first_interval=1.0)
            self.report({'INFO'}, "Bake of fracture data for sound synthesis started")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_fracture)

class PBRAUDIO_OT_bake(Operator):
    bl_idname = "scene.pbraudio_bake"
    bl_label = "Bake"
    bl_description = "Bake of prebaked data for sound synthesis"
    bl_options = {'REGISTER', 'UNDO'}
                
classes.append(PBRAUDIO_OT_bake)

class PBRAUDIO_OT_prebake(Operator):
    bl_idname = "scene.pbraudio_prebake"
    bl_label = "PreBake"
    bl_description = "PreBake baked physics dynamics for sound synthesis"
    bl_options = {'REGISTER', 'UNDO'}

    def update_progress(self, scene, status_file):
        """Update progress from status file"""
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    progress = f.read().strip()
                    if progress:
                        scene.pbraudio.status_progress = float(progress) / 100
                return True
            except:
                pass
        return False

    def check_completion(self, scene, process, status_file):
        """Update UI"""
        for area in bpy.context.screen.areas:
            area.tag_redraw()
        """Check if the process has completed"""
        if not process.is_alive():
            # Process finished
            scene.pbraudio.shader_processing = False
            scene.pbraudio.prebake = True
            scene.pbraudio.status_progress = 1.0
            self.report({'INFO'}, "Baking of prebaked data for sound synthesis completed")
            return None
        else:
            # Update progress
            self.update_progress(scene, status_file)
            # Continue timer
            return 1.0

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'prebake') and not scene.pbraudio.prebake:
            if not scene.pbraudio.physics:
                bpy.ops.scene.pbraudio_physics('EXEC_DEFAULT')
            # Start async processing
            scene.pbraudio.shader_processing = True
            scene.pbraudio.status_progress = 0.0
            export_path = f"{scene.pbraudio.cache_path}"
            if scene.pbraudio.cache_path.startswith('//'):
                export_path = f"{bpy.path.abspath(scene.pbraudio.cache_path)}"
            config_file = f"{export_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
            status_file = f"{export_path}/{scene.pbraudio.collision_collection.name_full}/status/rigidBodyEngine/prebake"
            process = pbrAudio_prebake(config_file, status_file)
            # Monitor completion
            bpy.app.timers.register(lambda: self.check_completion(scene, process, status_file), first_interval=1.0)
            self.report({'INFO'}, "Prebaking of baked physics dynamics for sound synthesis started")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_prebake)

class PBRAUDIO_OT_physics(Operator):
    bl_idname = "scene.pbraudio_physics"
    bl_label = "BakePhysics"
    bl_description = "Bake physics"
    bl_options = {'REGISTER', 'UNDO'}

    def update_progress(self, scene, status_file):
        """Update progress from status file"""
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    progress = f.read().strip()
                    if progress:
                        scene.pbraudio.status_progress = 0.5 + (float(progress) / 100)
                return True
            except:
                pass
        return False

    def check_completion(self, scene, process, status_file):
        """Update UI"""
        for area in bpy.context.screen.areas:
            area.tag_redraw()
        """Check if the process has completed"""
        if not process.is_alive():
            # Process finished
            scene.pbraudio.shader_processing = False
            scene.pbraudio.physics = True
            scene.pbraudio.cache_status = True
            scene.pbraudio.status_progress = 1.0
            self.report({'INFO'}, "Physics dynamics bake processing completed")
            return None
        else:
            # Update progress
            self.update_progress(scene, status_file)
            # Continue timer
            return 1.0

    def execute(self, context):
        scene = context.scene
        if hasattr(scene.pbraudio, 'physics'):
            if not scene.pbraudio.physics:
                decimals = 18
                fps = scene.render.fps
                fps_base = scene.render.fps_base
                start_frame = scene.frame_start
                end_frame = scene.frame_end

#                bpy.ops.object.select_all(action='SELECT')
#                bpy.ops.object.select_all(action='DESELECT')

                self.report({'INFO'}, "Physics dynamics bake processing started")
                # Create exporter
                scene.pbraudio.shader_processing = True
                scene.pbraudio.status_progress = 0.0
                exporter = CollisionExporter(scene=scene, decimals=decimals)
                progress_step = 0.5 / len(scene.pbraudio.collision_collection.objects.values())
                for obj in scene.pbraudio.collision_collection.objects.values():
                    # Export animation
                    scene.pbraudio.status_progress += progress_step
                    exporter.export_animation(obj, start_frame, end_frame)
                    obj.select_set(False)

                # Save config
                exporter.save_config()

                # Start async processing
                export_path = f"{scene.pbraudio.cache_path}"
                if scene.pbraudio.cache_path.startswith('//'):
                    export_path = f"{bpy.path.abspath(scene.pbraudio.cache_path)}"
                config_file = f"{export_path}/{scene.pbraudio.collision_collection.name_full}/config.json"
                status_file = f"{export_path}/{scene.pbraudio.collision_collection.name_full}/status/physicsEngine/bake"
                process = pbrAudio_physics(config_file, status_file)

                # Monitor completion
                bpy.app.timers.register(lambda: self.check_completion(scene, process, status_file), first_interval=1.0)
        return {'FINISHED'}

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
                scene.pbraudio.status_progress = 1
                scene.pbraudio.shader_processing = False
                self.report({'INFO'}, f"Collision cache for {scene.pbraudio.collision_collection.name_full} cleared")
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_clear_cache)
