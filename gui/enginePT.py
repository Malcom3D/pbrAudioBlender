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

class PBRAUDIO_PT_graphical_preview_panel(Panel):
    """Panel to enable pbrAudio graphical preview and settings"""
    bl_label = "Graphical preview"
    bl_idname = "PBRAUDIO_PT_graphical_preview_panel"
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

        layout.prop(scene.pbraudio, "enable_graphical_preview")
        if scene.pbraudio.enable_acoustic_preview:
           pass

classes.append(PBRAUDIO_PT_graphical_preview_panel)

class PBRAUDIO_PT_acoustic_preview_panel(Panel):
    """Panel to enable pbrAudio acoustic preview and settings"""
    bl_label = "Acoustic preview"
    bl_idname = "PBRAUDIO_PT_acoustic_preview_panel"
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

        layout.prop(scene.pbraudio, "enable_acoustic_preview")
        if scene.pbraudio.enable_acoustic_preview:
            layout.prop(scene.pbraudio, "preview_audio_quality")
            col = layout.column(align=True)
            col.prop(scene.pbraudio, "preview_sample_rate", text="Sample Rate")
    
classes.append(PBRAUDIO_PT_acoustic_preview_panel)

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
