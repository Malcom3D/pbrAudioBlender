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
from bpy.types import NodeSocket
from bpy.props import FloatProperty, StringProperty

from ..properties import worldPG

classes = []

class pbrAudioWorldNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioWorldNodeSocket'
    bl_label = "pbrAudio World Node Socket"

    def default_value_update(self, context):
        if self.is_output and self.is_linked:
            for link in self.links:
                link.to_node.sync_data(context)

    default_value: FloatProperty(
        default=0.0,
        update=default_value_update
    )

    def draw(self, context, layout, node, text):
        if self.is_output or (not self.is_output and not self.is_linked):
            layout.prop(self, "default_value", text=text, slider=True)
        elif not self.is_output and self.is_linked:
            layout.label(text=text)

    def draw_color(self, context, node):
        return (1.0, 0.1, 0.0, 1.0) # Orange

classes.append(pbrAudioWorldNodeSocket)

class pbrAudioWorldPropertyNodeSocket(pbrAudioWorldNodeSocket):
    bl_idname = 'pbrAudioWorldPropertyNodeSocket'
    bl_label = "pbrAudio World Property Node Socket"

    pbraudio_type: StringProperty(default='WorldMaterial')

    def draw_color(self, context, node):
        return (1.0, 1.0, 1.0, 1.0) # white

classes.append(pbrAudioWorldPropertyNodeSocket)

class pbrAudioWorldParameterNodeSocket(pbrAudioWorldNodeSocket):
    bl_idname = 'pbrAudioWorldParameterNodeSocket'
    bl_label = "pbrAudio World Parameter Node Socket"

    pbraudio_type: StringProperty(default='WorldParameter')

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray

classes.append(pbrAudioWorldParameterNodeSocket)

class pbrAudioWorldMaterialNodeSocket(pbrAudioWorldNodeSocket):
    bl_idname = 'pbrAudioWorldMaterialNodeSocket'
    bl_label = "pbrAudio World Material Node Socket"

    pbraudio_type: StringProperty(default='WorldMaterial')

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.3, 0.5, 0.8, 1.0) # Light Blue

classes.append(pbrAudioWorldMaterialNodeSocket)

class pbrAudioWorldEnvironmentNodeSocket(pbrAudioWorldNodeSocket):
    bl_idname = 'pbrAudioWorldEnvironmentNodeSocket'
    bl_label = "pbrAudio World Environment Socket"

    default_value: StringProperty(
        name="default_value",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
    )

    pbraudio_type: StringProperty(default='WorldEnvironment')

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.0, 1.0, 0.0, 1.0) # Green

classes.append(pbrAudioWorldEnvironmentNodeSocket)
