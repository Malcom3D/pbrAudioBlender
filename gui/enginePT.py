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

class PBRAUDIO_PT_device_panel(Panel):
    """Panel for pbrAudio render device settings"""
    bl_label = "Device"
    bl_idname = "PBRAUDIO_PT_device_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.prop(scene.pbraudio, "device")
 
classes.append(PBRAUDIO_PT_device_panel)

#class PBRAUDIO_PT_graphical_preview_panel(Panel):
#    """Panel to enable pbrAudio graphical preview and settings"""
#    bl_label = "Graphical preview"
#    bl_idname = "PBRAUDIO_PT_graphical_preview_panel"
#    bl_space_type = 'PROPERTIES'
#    bl_region_type = 'WINDOW'
#    bl_context = "render"
#    bl_options = {'DEFAULT_CLOSED'}
#
#    @classmethod
#    def poll(cls, context):
#        return context.scene.render.engine == 'PBRAUDIO'
#
#    def draw_header(self, context):
#        scene = context.scene
#        layout.prop(scene.pbraudio, "enable_graphical_preview")
#
#    def draw(self, context):
#        layout = self.layout
#        layout.use_property_split = True
#        layout.use_property_decorate = False  # No animation.
#
#        scene = context.scene
#
#        if scene.pbraudio.enable_acoustic_preview:
#           pass
#
#classes.append(PBRAUDIO_PT_graphical_preview_panel)

class PBRAUDIO_PT_frequencies_range_panel(Panel):
    """Panel to set the pbrAudio acoustic frequencies range"""
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_frequencies_range_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "enable_frequencies_range_set")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        if scene.pbraudio.enable_acoustic_preview:
            layout.prop(scene.pbraudio, "lowest_frequency", text="Lowest Frequency")
            layout.prop(scene.pbraudio, "higher_frequency", text="Higher Frequency")

classes.append(PBRAUDIO_PT_frequencies_range_panel)


class PBRAUDIO_PT_acoustic_preview_panel(Panel):
    """Panel to enable pbrAudio acoustic preview and settings"""
#    bl_label = "Acoustic preview"
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_acoustic_preview_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudio, "enable_acoustic_preview")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        if scene.pbraudio.enable_acoustic_preview:
            layout.prop(scene.pbraudio, "preview_audio_quality")
            layout.prop(scene.pbraudio, "preview_sample_rate", text="Sample Rate")
            layout.prop(scene.pbraudio, "preview_bit_depth", text="Bit Depth")
    
classes.append(PBRAUDIO_PT_acoustic_preview_panel)

class PBRAUDIO_PT_sampling_panel(Panel):
    """Panel to configure pbrAudio sampling settings"""
    bl_label = "Sampling Settings"
    bl_idname = "PBRAUDIO_PT_sampling_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
       
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        layout.prop(scene.pbraudiorender, "max_interactions")
        layout.prop(scene.pbraudiorender, "bands_per_octave")
        layout.prop(scene.pbraudiorender, "use_dispersion_correction")
        if scene.pbraudiorender.use_dispersion_correction:
            layout.prop(scene.pbraudiorender, "dispersion_order")
        layout.prop(scene.pbraudiorender, "use_extended_reaction")
        if scene.pbraudiorender.use_extended_reaction:
            layout.prop(scene.pbraudiorender, "max_modal_reaction")
        layout.prop(scene.pbraudiorender, "use_complex_eigenray")
        if scene.pbraudiorender.use_complex_eigenray:
            layout.prop(scene.pbraudiorender, "max_complex_eigenray")

classes.append(PBRAUDIO_PT_sampling_panel)

class PBRAUDIO_PT_interface_panel(Panel):
    """Panel to configure pbrAudio interface settings"""
#    bl_label = "Interfaces Settings"
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_interface_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudiorender, "enable_interface")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
    
        if scene.pbraudiorender.enable_interface:
            layout.prop(scene.pbraudiorender, "enable_absorption")
            layout.prop(scene.pbraudiorender, "enable_reflection")
            if scene.pbraudiorender.enable_reflection:
                layout.prop(scene.pbraudiorender, "max_reflection")
            layout.prop(scene.pbraudiorender, "enable_scattering")
            if scene.pbraudiorender.enable_scattering:
                layout.prop(scene.pbraudiorender, "max_scattering")
            layout.prop(scene.pbraudiorender, "enable_refraction")
            if scene.pbraudiorender.enable_refraction:
                layout.prop(scene.pbraudiorender, "max_refraction")
            layout.prop(scene.pbraudiorender, "enable_diffraction")
            if scene.pbraudiorender.enable_diffraction:
                layout.prop(scene.pbraudiorender, "max_diffraction")
            layout.prop(scene.pbraudiorender, "min_impedance_ratio")
            layout.prop(scene.pbraudiorender, "max_impedance_ratio")

classes.append(PBRAUDIO_PT_interface_panel)

class PBRAUDIO_PT_resonances_panel(Panel):
    """Panel to configure pbrAudio resonance settings"""
#    bl_label = "Resonance Settings"
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_resonances_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudiorender, "enable_resonance")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
    
        if scene.pbraudiorender.enable_resonance:
            layout.prop(scene.pbraudiorender, "max_resonance_structure")
            layout.prop(scene.pbraudiorender, "decay_time_constant")
            layout.prop(scene.pbraudiorender, "resonance_threshold")
            layout.prop(scene.pbraudiorender, "enable_helmholtz")
            if scene.pbraudiorender.enable_helmholtz:
                layout.prop(scene.pbraudiorender, "min_cavity_volume")
                layout.prop(scene.pbraudiorender, "max_resonance_room_modes")
            layout.prop(scene.pbraudiorender, "enable_parallel_wall")
            if scene.pbraudiorender.enable_parallel_wall:
                layout.prop(scene.pbraudiorender, "min_wall_distance")
                layout.prop(scene.pbraudiorender, "max_wall_distance")
            layout.prop(scene.pbraudiorender, "enable_tube")
            if scene.pbraudiorender.enable_tube:
                layout.prop(scene.pbraudiorender, "min_tube_length")
                layout.prop(scene.pbraudiorender, "min_tube_aspect_ratio")

classes.append(PBRAUDIO_PT_resonances_panel)

class PBRAUDIO_PT_termination_panel(Panel):
    """Panel to configure pbrAudio termination settings"""
#    bl_label = "Termination Settings"
    bl_label = ""
    bl_idname = "PBRAUDIO_PT_termination_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
        
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'
    
    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene.pbraudiorender, "enable_termination")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene

        if scene.pbraudiorender.enable_termination:
            layout.prop(scene.pbraudiorender, "termination_type")
            if scene.pbraudiorender.termination_type == 'SAMPLE_END':
                layout.prop(scene.pbraudiorender, "samples_after")
                layout.prop(scene.pbraudiorender, "min_active_sources")
            if scene.pbraudiorender.termination_type == 'REVERBERATION_TIME':
                layout.prop(scene.pbraudiorender, "max_reverberation_time")
            if scene.pbraudiorender.termination_type == 'ENERGY_THRESHOLD':
                layout.prop(scene.pbraudiorender, "max_energy_threshold")
                layout.prop(scene.pbraudiorender, "min_energy_threshold")

classes.append(PBRAUDIO_PT_termination_panel)

class PBRAUDIO_PT_grease_pencil_panel(Panel):
    """Panel for grease pencil settings in pbrAudio"""
    bl_label = "Grease Pencil"
    bl_idname = "PBRAUDIO_PT_grease_pencil_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        props = scene.grease_pencil_settings

        col = layout.column()
        col.prop(props, "antialias_threshold", text="SMAA Threshold")

classes.append(PBRAUDIO_PT_grease_pencil_panel)
