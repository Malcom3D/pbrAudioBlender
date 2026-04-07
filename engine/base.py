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
from bpy.types import RenderEngine
from ..exporter import render_exporter

classes =  []

class PBRAudioRenderEngine(RenderEngine):
    """pbrAudio render engine implementation"""
    bl_idname = 'PBRAUDIO'
    bl_label = "pbrAudio"
    bl_use_preview = True
    bl_use_eevee_viewport = False
    bl_use_shading_nodes_custom = False

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    # Note the generic arguments signature, and the call to the parent class
    # `__init__` methods, which are required for Blender to create the underlying
    # `RenderEngine` data.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
#        self.scene_data = None
#        self.draw_data = None
#        self.id_render = id(self)
        if self.is_animation:
            self.report({'INFO'}, f"pbrAudio: animation rendering in progress...")
        else:
            self.report({'INFO'}, f"pbrAudio: rendering in progress...")

    # When the render engine instance is destroy, this is called. Clean up any
    # render engine data here, for example stopping running render threads.
#    def __del__(self):
        # Own delete code...
#        super().__del__()

    # Render methods
    def update(self, data, depsgraph):
        """Update render data"""
        scene = depsgraph.scene
        if self.is_animation:
            self.report({'INFO'}, f"pbrAudio: animation rendering in progress...")
        else:
            self.report({'INFO'}, f"pbrAudio: rendering in progress...")

        self.report({'INFO'}, f" pbrAudio rendering updated...")

    def render(self, depsgraph):
        """Main render method"""
#        progress_step = 0.5 / len(scene.pbraudio.collision_collection.objects.values())
#        update_progress(progress_step)
        scene = depsgraph.scene
        decimals = 18
        exporter = render_exporter.RenderExporter(scene=scene, decimals=decimals)
        start_frame = scene.frame_start
        end_frame = scene.frame_end
        frame_number = scene.frame_current
        if self.is_animation:
            self.report({'INFO'}, f"pbrAudio: animation rendering in progress...")
            print('start_frame: ', start_frame, 'end_frame: ', end_frame) 
            exporter.export_animation(start_frame, end_frame)
        else:
            self.report({'INFO'}, f"pbrAudio: rendering in progress...")
            print('frame_number: ', frame_number)
            exporter.export_frame(frame_number)

#        scene = depsgraph.scene
#        pbraudio_init = pbrAudioConfigInit()
#
#        # check cache tree
#        if not pbraudio_init.scene.pbraudio.cache_status:
#            pbraudio_init.create_cache()
#
#        pbraudio_init.domain_config()
#        pbraudio_init.source_config()
#        pbraudio_init.output_config()
#        #pbraudio.init.object_config()
#        pbraudio_init.create_config()
#
#        if not pbraudio_init.scene.pbraudio.cache_status:
#            pbraudio_init.initZarr()
#            pbraudio_init.scene.pbraudio.cache_status = True
#
        update_progress(progress)

        self.report({'INFO'}, "pbrAudio rendering end...")

        # For viewport renders, this method gets called once at the start and
        # whenever the scene or 3D viewport changes. This method is where data
        # should be read from Blender in the same thread. Typically a render
        # thread will be started to do the work while keeping Blender responsive.
        def view_update(self, context, depsgraph):
            """Update viewport"""
            pass

        # For viewport renders, this method is called whenever Blender redraws
        # the 3D viewport. The renderer is expected to quickly draw the render
        # with OpenGL, and not perform other expensive work.
        # Blender will draw overlays for selection and editing on top of the
        # rendered image automatically.
        def view_draw(self, context, depsgraph):
            """Draw viewport"""
            pass

classes.append(PBRAudioRenderEngine)
