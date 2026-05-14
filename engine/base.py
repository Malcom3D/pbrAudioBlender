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
import os
import time
import threading
from bpy.types import RenderEngine
from mathutils import Matrix, Vector

from ..utils import frd_io, environment_json
from ..utils.ambisonic_decoder import AmbisonicDecoder
from ..exporter.render_exporter import RenderExporter
from pbrAudioRay.core.entity_manager import EntityManager
from pbrAudioRay.core.acoustic_engine import AcousticEngine

classes = []

class PBRAudioRenderEngine(RenderEngine):
    """pbrAudio render engine implementation"""
    bl_idname = 'PBRAUDIO'
    bl_label = "pbrAudio"
    bl_use_preview = False
    bl_use_material = False
    bl_use_eevee_viewport = False
    bl_use_shading_nodes_custom = False
    
    # Render status flags
    _is_rendering = False
    _render_thread = None
    _cancel_render = False
    
    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_data = None
        self.draw_data = None
        self.exporter = None
        self.render_process = None
        self.report({'INFO'}, f"pbrAudio: RenderEngine initialized")
    
    # When the render engine instance is destroy, this is called. Clean up any
    # render engine data here, for example stopping running render threads.
    def __del__(self):
        self.cancel_render()
    
    def cancel_render(self):
        """Cancel any ongoing render"""
        self._cancel_render = True
        if self._render_thread and self._render_thread.is_alive():
            self._render_thread.join(timeout=2.0)
        self._is_rendering = False
    
    def _run_external_engine(self, config_file, output_dir, frame_start, frame_end, frame_current):
        """
        Run the external acoustic rendering engine.
        """
        try:
            # This is where you would call your external engine
            print('_run_external_engine: ', config_file)
            self.entity_manager = EntityManager(config_file)
            self.acoustic_engine = AcousticEngine(self.entity_manager)

            self.report({'INFO'}, f"Starting acoustic rendering engine...")
            self.report({'INFO'}, f"Config: {config_file}")
            self.report({'INFO'}, f"Output: {output_dir}")
            self.report({'INFO'}, f"Frames: {frame_start}-{frame_end}")

            print(f"acoustic_engine.compute({frame_current})")
            self.acoustic_engine._compute_frame(frame_current)

            # Update progress
            total_frames = frame_end - frame_start + 1
            progress = (frame_current - frame_start + 1) / total_frames
            self.update_progress(progress)
            
            # Report frame completion
            self.report({'INFO'}, f"Rendered frame {frame_current}")

            if frame_current == frame_end:
                self.report({'INFO'}, f"Rendering ambisonic tracks...")
                self.acoustic_engine.render()

            return True

#            # Simulate rendering progress
#            total_frames = frame_end - frame_start + 1
#            for frame in range(frame_start, frame_end + 1):
#                if self._cancel_render:
#                    self.report({'INFO'}, "Render cancelled")
#                    return False
#                
#                # Update progress
#                progress = (frame - frame_start + 1) / total_frames
#                self.update_progress(progress)
#                
#                # Simulate frame processing
#                time.sleep(0.1)  # Replace with actual engine call
#                
#                # Report frame completion
#                self.report({'INFO'}, f"Rendered frame {frame}")
#           
#            return True
            
        except Exception as e:
            self.report({'ERROR'}, f"Engine error: {str(e)}")
            return False
    
    def _render_thread_func(self, depsgraph, scene, frame_start=None, frame_end=None, frame_current=None):
        """Main render thread function"""
        try:
            self._is_rendering = True
            self._cancel_render = False
            
            # Step 1: Export scene data using RenderExporter
            self.report({'INFO'}, "Exporting scene data...")
            
            # Create exporter
            self.exporter = RenderExporter(depsgraph=depsgraph, scene=scene, decimals=18)
            
            # Export scene
            #export_success = self.exporter.export_scene(frame_start, frame_end)
            export_success = self.exporter.export(frame_start, frame_end)
            
            if not export_success:
                self.report({'ERROR'}, "Scene export failed")
                self._is_rendering = False
                return

            # Step 2: Decode Ambisonic Environment sound track
            print(f"Decoding World Environment Ambisonic Sound Track...")
            self.report({'INFO'}, "Decoding World Environment Ambisonic Sound Track...")
            cache_path = scene.pbraudio.cache_path

            if cache_path.startswith('//'):
                cache_path = bpy.path.abspath(cache_path)

            # Create cache_path directory if it doesn't exist
            os.makedirs(cache_path, exist_ok=True)

            for obj in bpy.data.objects:
                if hasattr(obj, 'pbraudio') and obj.pbraudio.environment and not obj.pbraudio.environment_file == "":
                    # Save environment data
                    json_config_path = environment_json.save_environment_json(obj, cache_path)

                    # Decode enviroment ambisonic file
                    self.report({'INFO'}, f"Decoding ambisonic file for {obj.name}")

                    # Create decoder
                    decoder = AmbisonicDecoder(json_config_path=json_config_path)

                    # Decode to boundary positions
                    decoder.save_decoded_files()

            print(f"Export completed successfully!")
            self.report({'INFO'}, "Export completed successfully!")

            # Step 3: Run external acoustic engine

            config_file = os.path.join(cache_path, "AcousticDomain/config.json")

            output_dir = scene.pbraudio.output_path

            if output_dir.startswith('//'):
                output_dir = bpy.path.abspath(output_dir)

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            self.report({'INFO'}, "Starting acoustic rendering...")
            
            # Run external engine
            print(f"engine/base.py: current render frame {frame_current}")
            engine_success = self._run_external_engine(config_file, output_dir, frame_start, frame_end, frame_current)
            
            if engine_success:
                self.report({'INFO'}, "Acoustic rendering completed successfully!")
                
                # Step 3: Post-process results if needed
                self._post_process_results(output_dir, scene)
                
            else:
                self.report({'ERROR'}, "Acoustic rendering failed")
            
            self._is_rendering = False
            
        except Exception as e:
            self.report({'ERROR'}, f"Render error: {str(e)}")
            import traceback
            traceback.print_exc()
            self._is_rendering = False
    
    def _post_process_results(self, output_dir, scene):
        """Post-process rendered results (e.g., decode ambisonic files)"""
        try:
            self.report({'INFO'}, "Post-processing rendered audio")
            self.report({'INFO'}, "Post-processing completed")
            if scene.pbraudio.enable_graphical_preview:
                pass
            
        except Exception as e:
            self.report({'WARNING'}, f"Post-processing error: {str(e)}")
    
    def update_progress(self, progress):
        """Update render progress"""
        # This would update Blender's progress bar
        # In a real implementation, you'd use proper progress reporting
        pass
    
    # Render methods
    def update(self, data, depsgraph):
        """Update render data (called before render)"""
        scene = depsgraph.scene
        
        if self.is_preview:
            self.report({'INFO'}, "pbrAudio: Updating preview...")
        elif self.is_animation:
            self.report({'INFO'}, "pbrAudio: Updating animation rendering...")
        else:
            self.report({'INFO'}, "pbrAudio: Updating rendering...")
        
        # Validate scene settings
        self._validate_scene_settings(scene)
    
    def _validate_scene_settings(self, scene):
        """Validate scene settings before rendering"""
        # Check for acoustic domain
        has_domain = False
        for world in bpy.data.worlds:
            if hasattr(world, 'pbraudio') and world.pbraudio.acoustic_domain:
                has_domain = True
                break
        
        if not has_domain:
            self.report({'WARNING'}, "No acoustic domain defined in world settings")
        
        # Check for sound sources
        sources = [obj for obj in bpy.data.objects 
                  if hasattr(obj, 'pbraudio') and obj.pbraudio.source]
        
        if not sources:
            self.report({'WARNING'}, "No sound sources defined in scene")
        
        # Check for outputs
        outputs = [obj for obj in bpy.data.objects 
                  if hasattr(obj, 'pbraudio') and obj.pbraudio.output]
        
        if not outputs:
            self.report({'WARNING'}, "No sound outputs defined in scene")
    
    def render(self, depsgraph):
        """Main render method"""
        self.report({'INFO'}, "pbrAudio: Render begin...")
        scene = depsgraph.scene
        frame = scene.frame_current
        
        # Cancel any existing render
        self.cancel_render()
        
        # Start new render in background thread
        self._render_thread = threading.Thread(target=self._render_thread_func, args=(depsgraph, scene, frame, frame, frame), daemon=True)
        
        self._render_thread.start()
        
        # For Blender to know we're rendering asynchronously
        # We need to return and let the thread run
        self._is_rendering = True
        
        # In a real implementation, you'd use proper async rendering
        # For now, we'll wait for completion (not ideal for UI)
        self._render_thread.join()
        
        self.report({'INFO'}, "pbrAudio: Render completed")
    
    def view_update(self, context, depsgraph):
        """Update for viewport rendering"""
        if self._is_rendering:
            return
        
        # For viewport preview, we might want to show a simplified representation
        # or just show the acoustic domain and sources
        self.update(context.scene, depsgraph)
    
    def view_draw(self, context, depsgraph):
        """Draw in viewport"""
        # Draw acoustic domain boundaries
        for world in bpy.data.worlds:
            if hasattr(world, 'pbraudio') and world.pbraudio.acoustic_domain:
                domain = world.pbraudio.acoustic_domain
                # Draw domain bounds (simplified)
                self._draw_domain_bounds(domain)
        
        # Draw sound sources
        for obj in bpy.data.objects:
            if hasattr(obj, 'pbraudio') and obj.pbraudio.source:
                self._draw_sound_source(obj)
            
            if hasattr(obj, 'pbraudio') and obj.pbraudio.output:
                self._draw_sound_output(obj)
            
            if hasattr(obj, 'pbraudio') and obj.pbraudio.environment:
                self._draw_environment(obj)
    
    def _draw_domain_bounds(self, domain_obj):
        """Draw acoustic domain bounds in viewport"""
        # This would use OpenGL to draw the domain bounds
        # For now, it's a placeholder
        pass
    
    def _draw_sound_source(self, source_obj):
        """Draw sound source in viewport"""
        # Draw source representation based on type
        if source_obj.pbraudio.source_type == 'SPHERE':
            # Draw sphere
            pass
        elif source_obj.pbraudio.source_type == 'PLANE':
            # Draw plane
            pass
    
    def _draw_sound_output(self, output_obj):
        """Draw sound output in viewport"""
        # Draw microphone/listener representation
        pass
    
    def _draw_environment(self, env_obj):
        """DrawDraw environment sphere and boundaries"""
        # Draw environment sphere and boundary points
        pass
    
    # Preview rendering (simplified version for material preview)
    def preview_render(self):
        """Preview render for material preview"""
        self.report({'INFO'}, "pbrAudio: Material preview rendering")
        
        # For material preview, we might render a simple frequency response
        # or show material properties
        
        return {'FINISHED'}
    
    # Animation rendering support
    def animation_render(self, depsgraph):
        """Render animation sequence"""
        self.report({'INFO'}, "pbrAudio: Animation Render begin...")
        if self.is_animation:
            start_frame = scene.frame_start
            end_frame = scene.frame_end
        else:
            start_frame = scene.frame_current
            end_frame = start_frame

        scene = depsgraph.scene
        frame_current = scene.frame_current
        
        self.report({'INFO'}, f"pbrAudio: Starting animation render ({start_frame}-{end_frame})")
        
        # Use the same render thread but for animation
        self.cancel_render()
        
        self._render_thread = threading.Thread(target=self._render_thread_func, args=(depsgraph, scene, start_frame, end_frame, frame_current), daemon=True)
        
        self._render_thread.start()
        
        # Note: For proper animation rendering in Blender, you should
        # implement frame-by-frame rendering with proper callbacks
    
    def supports_save_buffers(self):
        """Return whether the engine supports saving render buffers"""
        return False
    
    def supports_glsl_shader(self, shader_type):
        """Return whether the engine supports GLSL shaders"""
        return False
    
    def get_result(self):
        """Get render result"""
        # For acoustic rendering, the result is audio files
        # We might return a reference to the generated files
        return None
    
    def get_image(self):
        """Get rendered image (not applicable for audio)"""
        return None
    
    def get_float_buffer(self):
        """Get float buffer (not applicable for audio)"""
        return None

classes.append(PBRAudioRenderEngine)
