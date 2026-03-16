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

        scene = context.scene

        layout.prop(scene.pbraudio, "collision_collection", text="Select Collection")
        layout.prop(scene.pbraudio, "collision_margin", text="Collision Margin")

        # operator button
        layout.operator('scene.pbraudio_clear_cache', emboss=True if not scene.pbraudio.cache_status else False)
        layout.operator('scene.pbraudio_physics', emboss=True if not scene.pbraudio.physics else False)
        layout.operator('scene.pbraudio_prebake', emboss=True if not scene.pbraudio.prebake else False)
        layout.operator('scene.pbraudio_bake', emboss=True if not scene.pbraudio.bake else False)
        for obj in scene.pbraudio.collision_collection.objects.values():
            if obj.pbraudio.fractured and not len(obj.pbraudio_shard.values()) == 0:
                break
        if obj.pbraudio.fractured:
            layout.operator('scene.pbraudio_fracture', emboss=True if not scene.pbraudio.fracture else False)

classes.append(PBRAUDIO_PT_Collision_panel)

class PBRAUDIO_PT_cache_panel(Panel):
    """Panel for pbrAudio cache path and settings"""
    bl_label = "PbrAudio Cache"
    bl_idname = "PBRAUDIO_PT_cache_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

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
