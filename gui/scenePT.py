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
    bl_context = "scene"
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

        layout.prop(scene.pbraudio, "collision_collection", text="Select Collection")
        layout.prop(scene.pbraudio, "collision_margin", text="Collision Margin", slider=True)
        layout.prop(scene.pbraudio, "modal_modes", text="Modal Modes")

        # scene fracture value
        fracture_enabled = False
        if hasattr(scene.pbraudio.collision_collection, 'objects'):
            for object in scene.pbraudio.collision_collection.objects.values():
                if object.pbraudio.fractured and not len(object.pbraudio_shard.values()) == 0 and not scene.pbraudio.fracture:
                    fracture_enabled = True

        # operator button
        row_clear_cache = layout.row()
        row_clear_cache.operator('scene.pbraudio_clear_cache')
        row_clear_cache.enabled = True if scene.pbraudio.cache_status else False
        row_physics = layout.row()
        row_physics.operator('scene.pbraudio_physics')
        row_physics.enabled = True if not scene.pbraudio.physics else False
        row_prebake = layout.row()
        row_prebake.operator('scene.pbraudio_prebake')
        row_prebake.enabled = True if not scene.pbraudio.prebake else False
        row_bake = layout.row()
        row_bake.operator('scene.pbraudio_bake')
        row_bake.enabled = True if not scene.pbraudio.bake else False
        row_fracture = layout.row()
        row_fracture.operator('scene.pbraudio_fracture')
        row_fracture.enabled = fracture_enabled

classes.append(PBRAUDIO_PT_Collision_panel)

class PBRAUDIO_PT_audioforcesdenoiser_panel(Panel):
    """Panel for pbrAudio AudioForcesDenoiser settings"""
    bl_label = "PbrAudio AudioForcesDenoiser"
    bl_idname = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
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
    bl_label = "DC Offset" 
    bl_idname = "PBRAUDIO_PT_dcoffset_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        # DC Offset Removal parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser
        layout.prop(scene.pbraudio, "dc_blocker_alpha", slider=True)

classes.append(PBRAUDIO_PT_dcoffset_panel)

class PBRAUDIO_PT_noisegate_panel(Panel):
    bl_label = "Adaptive Noise Gate"
    bl_idname = "PBRAUDIO_PT_noisegate_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Adaptive Noise Gate parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser
        layout.prop(scene.pbraudio, "gate_threshold_db", slider=True)
        layout.prop(scene.pbraudio, "gate_attack_ms", slider=True)
        layout.prop(scene.pbraudio, "gate_release_ms", slider=True)
        layout.prop(scene.pbraudio, "gate_hold_ms", slider=True)
classes.append(PBRAUDIO_PT_noisegate_panel)

class PBRAUDIO_PT_temporalsmoothing_panel(Panel):
    bl_label = "Temporal Smoothing"
    bl_idname = "PBRAUDIO_PT_temporalsmoothing_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Temporal Smoothing parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser
        layout.prop(scene.pbraudio, "temporal_smoothing_window", slider=True)
classes.append(PBRAUDIO_PT_temporalsmoothing_panel)

class PBRAUDIO_PT_spectralnoise_panel(Panel):
    bl_label = "Spectral Noise Reduction"
    bl_idname = "PBRAUDIO_PT_spectralnoise_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Spectral Noise Reduction parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser
        layout.prop(scene.pbraudio, "spectral_fft_size", slider=True)
        layout.prop(scene.pbraudio, "spectral_hop_size", slider=True)
        layout.prop(scene.pbraudio, "spectral_noise_floor_db", slider=True)
        layout.prop(scene.pbraudio, "spectral_reduction_strength", slider=True)
        layout.prop(scene.pbraudio, "spectral_smoothing", slider=True)
classes.append(PBRAUDIO_PT_spectralnoise_panel)

class PBRAUDIO_PT_envelopeshaping_panel(Panel):
    bl_label = "Envelope Shaping"
    bl_idname = "PBRAUDIO_PT_envelopeshaping_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Envelope Shaping parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser
        layout.prop(scene.pbraudio, "envelope_attack_ms", slider=True)
        layout.prop(scene.pbraudio, "envelope_release_ms", slider=True)
        layout.prop(scene.pbraudio, "envelope_smoothing", slider=True)
classes.append(PBRAUDIO_PT_envelopeshaping_panel)

class PBRAUDIO_PT_adaptivesmooting_panel(Panel):
    bl_label = "Gaussian Adaptive Smoothing"
    bl_idname = "PBRAUDIO_PT_adaptivesmooting_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "PBRAUDIO_PT_audioforcesdenoiser_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        # Gaussian Adaptive Smoothing parameters
        layout.enabled = scene.pbraudio.enable_forces_denoiser
        layout.prop(scene.pbraudio, "gaussian_sigma_min", slider=True)
        layout.prop(scene.pbraudio, "gaussian_sigma_max", slider=True)
        layout.prop(scene.pbraudio, "gaussian_force_threshold", slider=True)
classes.append(PBRAUDIO_PT_adaptivesmooting_panel)

class PBRAUDIO_PT_cache_panel(Panel):
    """Panel for pbrAudio cache path and settings"""
    bl_label = "PbrAudio Cache"
    bl_idname = "PBRAUDIO_PT_cache_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
#    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.enabled = not scene.pbraudio.cache_status
        layout.prop(scene.pbraudio, "cache_path", toggle=scene.pbraudio.cache_status)

classes.append(PBRAUDIO_PT_cache_panel)
