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
from bpy.types import Panel

classes = []

class PBRAUDIO_PT_Collision_panel(Panel):
    """Panel for pbrAudio Collision synthesis settings"""
    bl_label = "PbrAudio Collision"
    bl_idname = "PBRAUDIO_PT_Collision_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # Draw progress bar if baking are processed
        if scene.pbraudio.shader_processing:
            layout.progress(factor=scene.pbraudio.status_progress, type='BAR')
#            layout.prop(scene.pbraudio, "status_progress", text="Shader Progress", slider=True)

        layout.enabled = not scene.pbraudio.shader_processing

        layout.prop(scene.pbraudio, "collision_collection", text="Select Collection")
        collision_collection = scene.pbraudio.collision_collection
        if collision_collection is not None:
            if collision_collection['is_valid']:
                layout.label(text="Cache Valid", icon='CHECKMARK')
            else:
                layout.label(text="Cache Invalid - full re-bake required", icon='ERROR')

        layout.prop(scene.pbraudio, "collision_margin", text="Collision Margin", slider=True)
        layout.prop(scene.pbraudio, "samples_per_object", text="Samples per Object", slider=True)
        layout.prop(scene.pbraudio, "modal_modes", text="Modal Modes")

        # scene fracture value
        fracture_enabled = False
        if hasattr(scene.pbraudio.collision_collection, 'objects'):
            for object in scene.pbraudio.collision_collection.objects.values():
                if object.pbraudio.fractured and not len(object.pbraudio_shard.values()) == 0 and not scene.pbraudio.fracture:
                    fracture_enabled = True

        # operator button
        row_clear_coll_cache = layout.row()
        row_clear_coll_cache.operator('scene.pbraudio_clear_coll_cache')
        row_clear_coll_cache.enabled = not scene.pbraudio.shader_processing
        row_clear_coll_cache.enabled = True if row_clear_coll_cache.enabled and collision_collection['is_valid'] else False
        row_physics = layout.row()
        row_physics.operator('scene.pbraudio_physics')
        row_physics.enabled = not scene.pbraudio.shader_processing and collision_collection['is_valid']
#        row_physics.enabled = True if row_physics.enabled and not scene.pbraudio.physics else False
        collection_physics = collision_collection['physics'] if collision_collection is not None and 'physics' in collision_collection.keys() else False
        row_physics.enabled = True if row_physics.enabled and not collection_physics else False
        row_prebake = layout.row()
        row_prebake.operator('scene.pbraudio_prebake')
        row_prebake.enabled = not scene.pbraudio.shader_processing and collision_collection['is_valid']
#        row_prebake.enabled = True if row_prebake.enabled and not scene.pbraudio.prebake else False
        collection_prebake = collision_collection['prebake'] if collision_collection is not None and 'prebake' in collision_collection.keys() else False
        row_prebake.enabled = True if row_prebake.enabled and not collection_prebake else False
        row_bake = layout.row()
        row_bake.operator('scene.pbraudio_bake')
        row_bake.enabled = not scene.pbraudio.shader_processing and collision_collection['is_valid']
#        row_bake.enabled = True if row_bake.enabled and not scene.pbraudio.bake else False
        collection_bake = collision_collection['bake'] if collision_collection is not None and 'bake' in collision_collection.keys() else False
        row_bake.enabled = True if row_bake.enabled and not collection_bake else False
        row_fracture = layout.row()
        row_fracture.operator('scene.pbraudio_fracture')
        row_fracture.enabled = not scene.pbraudio.shader_processing and collision_collection['is_valid']
        collection_fracture = collision_collection['fracture'] if collision_collection is not None and 'fracture' in collision_collection.keys() else False
        row_fracture.enabled = True if row_fracture.enabled and fracture_enabled and not collection_fracture else False

classes.append(PBRAUDIO_PT_Collision_panel)

class PBRAUDIO_PT_small_mesh_proxy_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_small_mesh_proxy_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "enable_small_proxy")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Small Mesh Proxy parameters
        layout.enabled = scene.pbraudio.enable_small_proxy and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "proxy_size_threshold", slider=True)

classes.append(PBRAUDIO_PT_small_mesh_proxy_panel)

class PBRAUDIO_PT_audioforcesdenoiser_panel(Panel):
    """Panel for pbrAudio AudioForcesDenoiser settings"""
#    bl_label = "PbrAudio AudioForcesDenoiser"
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "enable_forces_denoiser")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.enabled = not scene.pbraudio.cache_status

classes.append(PBRAUDIO_PT_audioforcesdenoiser_panel)

class PBRAUDIO_PT_dcoffset_panel(Panel):
    bl_label = "" 
    bl_idname = "PBRAUDIO_PT_dcoffset_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.enabled = scene.pbraudio.enable_forces_denoiser and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "enable_dc_blocker")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # DC Offset Removal parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser and scene.pbraudio.enable_dc_blocker and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "dc_blocker_alpha", slider=True)

classes.append(PBRAUDIO_PT_dcoffset_panel)

class PBRAUDIO_PT_noisegate_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_noisegate_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.enabled = scene.pbraudio.enable_forces_denoiser and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "enable_noise_gate")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Adaptive Noise Gate parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser and scene.pbraudio.enable_noise_gate and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "gate_threshold_db", slider=True)
        layout.prop(scene.pbraudio, "gate_attack_ms", slider=True)
        layout.prop(scene.pbraudio, "gate_release_ms", slider=True)
        layout.prop(scene.pbraudio, "gate_hold_ms", slider=True)
classes.append(PBRAUDIO_PT_noisegate_panel)

class PBRAUDIO_PT_temporalsmoothing_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_temporalsmoothing_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.enabled = scene.pbraudio.enable_forces_denoiser and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "enable_temporal_smoothing")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Temporal Smoothing parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser and scene.pbraudio.enable_temporal_smoothing and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "temporal_smoothing_window", slider=True)
classes.append(PBRAUDIO_PT_temporalsmoothing_panel)

class PBRAUDIO_PT_spectralnoise_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_spectralnoise_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.enabled = scene.pbraudio.enable_forces_denoiser and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "enable_spectral_noise_reduction")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Spectral Noise Reduction parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser and scene.pbraudio.enable_spectral_noise_reduction and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "spectral_fft_size", slider=True)
        layout.prop(scene.pbraudio, "spectral_hop_size", slider=True)
        layout.prop(scene.pbraudio, "spectral_noise_floor_db", slider=True)
        layout.prop(scene.pbraudio, "spectral_reduction_strength", slider=True)
        layout.prop(scene.pbraudio, "spectral_smoothing", slider=True)
classes.append(PBRAUDIO_PT_spectralnoise_panel)

class PBRAUDIO_PT_envelopeshaping_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_envelopeshaping_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.enabled = scene.pbraudio.enable_forces_denoiser and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "enable_envelope_shaping")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Envelope Shaping parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser and scene.pbraudio.enable_envelope_shaping and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "envelope_attack_ms", slider=True)
        layout.prop(scene.pbraudio, "envelope_release_ms", slider=True)
        layout.prop(scene.pbraudio, "envelope_smoothing", slider=True)
classes.append(PBRAUDIO_PT_envelopeshaping_panel)

class PBRAUDIO_PT_adaptivesmooting_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_adaptivesmooting_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.enabled = scene.pbraudio.enable_forces_denoiser and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "enable_gaussian_adaptive_smoothing")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Gaussian Adaptive Smoothing parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser and scene.pbraudio.enable_gaussian_adaptive_smoothing and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "gaussian_sigma_min", slider=True)
        layout.prop(scene.pbraudio, "gaussian_sigma_max", slider=True)
        layout.prop(scene.pbraudio, "gaussian_force_threshold", slider=True)
classes.append(PBRAUDIO_PT_adaptivesmooting_panel)

class PBRAUDIO_PT_postprocess_panel(Panel):
    """Panel for pbrAudio PostProcess settings"""
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_postprocess_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "enable_postprocess")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.enabled = not scene.pbraudio.cache_status

classes.append(PBRAUDIO_PT_postprocess_panel)

class PBRAUDIO_PT_postprocess_dynamic_amplify_panel(Panel):
    bl_label = "Audio-Force drived dynamic Amplification"
    bl_idname = "PBRAUDIO_PT_postprocess_dynamic_amplify_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_postprocess_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        layout.prop(scene.pbraudio, "postprocess_target_rms", slider=True)
        layout.prop(scene.pbraudio, "postprocess_max_gain_db", slider=True)
        layout.prop(scene.pbraudio, "postprocess_dynamic_range_compression", slider=True)

classes.append(PBRAUDIO_PT_postprocess_dynamic_amplify_panel)

class PBRAUDIO_PT_postprocess_dynamic_denoise_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_postprocess_dynamic_denoise_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_postprocess_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "postprocess_dynamic_denoise_enabled")
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        
        scene = context.scene
        layout.enabled = scene.pbraudio.postprocess_dynamic_denoise_enabled and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "postprocess_noise_gate_threshold_db", slider=True)
        layout.prop(scene.pbraudio, "postprocess_noise_floor_estimate_db", slider=True)
        layout.prop(scene.pbraudio, "postprocess_spectral_reduction_strength", slider=True)
        layout.prop(scene.pbraudio, "postprocess_temporal_smoothing_window", slider=True)
        layout.prop(scene.pbraudio, "postprocess_force_reference_weight", slider=True)
        layout.prop(scene.pbraudio, "postprocess_min_force_threshold", slider=True)

classes.append(PBRAUDIO_PT_postprocess_dynamic_denoise_panel)

class PBRAUDIO_PT_postprocess_smoothing_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_postprocess_smoothing_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_postprocess_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "postprocess_smoothing_enabled")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        layout.enabled = scene.pbraudio.postprocess_smoothing_enabled and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "postprocess_smoothing_window_ms", slider=True)
        layout.prop(scene.pbraudio, "postprocess_adaptive_smoothing", slider=True)
        layout.prop(scene.pbraudio, "postprocess_phase_align_enabled", slider=True)
        layout.prop(scene.pbraudio, "postprocess_crossfade_samples", slider=True)

classes.append(PBRAUDIO_PT_postprocess_smoothing_panel)

class PBRAUDIO_PT_postprocess_blend_panel(Panel):
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_postprocess_blend_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_parent_id = "PBRAUDIO_PT_postprocess_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "postprocess_blend_enabled")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        layout.enabled = scene.pbraudio.postprocess_blend_enabled and not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "postprocess_dry_wet_mix", slider=True)
        layout.prop(scene.pbraudio, "postprocess_normalize_output", slider=True)

classes.append(PBRAUDIO_PT_postprocess_blend_panel)

class PBRAUDIO_PT_cache_panel(Panel):
    """Panel for pbrAudio cache path and settings"""
    bl_label = "PbrAudio Cache"
    bl_idname = "PBRAUDIO_PT_cache_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.enabled = not scene.pbraudio.cache_status
        layout.operator('scene.pbraudio_clear_cache')
        layout.enabled = not scene.pbraudio.shader_processing
        layout.enabled = True if layout.enabled and not scene.pbraudio.cache_status else False
        layout.prop(scene.pbraudio, "cache_path", toggle=scene.pbraudio.cache_status)

classes.append(PBRAUDIO_PT_cache_panel)
