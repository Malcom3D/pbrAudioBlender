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
from mathutils import Matrix, Vector

from ..utils import frd_io, environment_json
from ..utils.ambisonic_decoder import AmbisonicDecoder
from ..exporter.render_exporter import RenderExporter

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
        render_path = scene.pbraudio.cache_path
        if render_path.startswith('//'):
            render_path = f"{bpy.path.abspath(render_path)}"
        os.makedirs(render_path, exist_ok=True)
        self.render_path = f"{render_path}/AcousticDomain"
        os.makedirs(self.render_path, exist_ok=True)
        decimals = 18
        exporter = RenderExporter(scene=scene, decimals=decimals)
        if self.is_animation:
            self.report({'INFO'}, f"pbrAudio: animation rendering in progress...")
            start_frame = scene.frame_start
            end_frame = scene.frame_end
        else:
            self.report({'INFO'}, f"pbrAudio: rendering in progress...")
            start_frame = self.scene.frame_current
            end_frame = start_frame

        # Find Domain Vector
        for world in bpy.data.worlds.values():
            acoustic_domain = world.pbraudio.acoustic_domain
            world_matrix = acoustic_domain.matrix_world
        domain_vertices = exporter.config["acoustic_domain"].get('geometry', [])
        domain_vectors = [world_matrix @ Vector(v) for v in domain_vertices]

        objects = exporter.find_objs_in_domain(domain_vertices=domain_vectors)
        for object in objects: 
            self.export_animation_obj(object, start_frame, end_frame)

        sources = exporter.find_empty_in_domain(domain_vertices=domain_vectors, empty_type='source')
        for source in sources:
            if source.pbraudio.source:
                self.export_animation_empty(source, start_frame, end_frame)

        outputs = exporter.find_empty_in_domain(domain_vertices=domain_vectors, empty_type='output')
        for output in outputs:
            if output.pbraudio.output:
                exporter.export_animation_empty(output, start_frame, end_frame)

        environments = exporter.find_empty_in_domain(domain_vertices=domain_vectors, empty_type='environment')
        if not len(environments) == 0:
            for environment in environments:
                if not environment.pbraudio.environment_file == "":
                    # Save environment data as json
                    json_config_path = environment_json.save_environment_json(environment, self.render_path)
                    # Decode boundary empty audio channel from saved json
                    ambisonic_decoder = AmbisonicDecoder(json_config_path=json_config_path)
                    ambisonic_decoder.save_decoded_files()

        self.report({'INFO'}, "pbrAudio rendering end...")

        # For viewport renders, this method gets called once at the start and
        # whenever the scene or 3D viewport changes. This method is where data
        # should be read from Blender in the same thread. Typically a render
        # thread will be started to do the work while keeping Blender responsive.
#        def view_update(self, context, depsgraph):
#            """Update viewport"""
#            pass

        # For viewport renders, this method is called whenever Blender redraws
        # the 3D viewport. The renderer is expected to quickly draw the render
        # with OpenGL, and not perform other expensive work.
        # Blender will draw overlays for selection and editing on top of the
        # rendered image automatically.
#        def view_draw(self, context, depsgraph):
#            """Draw viewport"""
#            pass

classes.append(PBRAudioRenderEngine)
