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

class pbrAudioWorldPropertyNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioWorldPropertyNodeSocket'
    bl_label = "pbrAudio World Property Node Socket"

#    type: StringProperty(default=self.bl_idname)

    default_value: FloatProperty(default=0.0)

    def draw(self, context, layout, node, text):
        layout.prop(self, "default_value", text=text, slider=True)

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray for Float

classes.append(pbrAudioWorldPropertyNodeSocket)

class pbrAudioWorldParameterNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioWorldParameterNodeSocket'
    bl_label = "pbrAudio World Parameter Node Socket"

#    type: StringProperty(default=self.bl_idname)

    default_value: FloatProperty(default=0.0)

    def draw(self, context, layout, node, text):
        if not self.is_linked and not self.is_output:
            layout.prop(self, "default_value", text=text, slider=True)
        else:
            layout.label(text=text)

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray for Float

classes.append(pbrAudioWorldParameterNodeSocket)

class pbrAudioWorldOutputNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioWorldOutputNodeSocket'
    bl_label = "pbrAudio World Output Node Socket"

#    type: StringProperty(default=self.bl_idname)

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.65, 0.65, 0.65, 1.0) # Light Gray for Float

classes.append(pbrAudioWorldOutputNodeSocket)

class pbrAudioWorldEnvironmentNodeSocket(NodeSocket):
    bl_idname = 'pbrAudioWorldEnvironmentNodeSocket'
    bl_label = "pbrAudio World Environment Socket"

#    type: StringProperty(default=self.bl_idname)

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (1.0, 1.0, 1.0, 1.0) # white for collection data

#classes.append(pbrAudioWorldEnvironmentNodeSocket)
