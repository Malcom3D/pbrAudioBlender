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
from bpy.props import FloatProperty, StringProperty, IntProperty

classes = []

class AcousticMaterialNodeSocket(NodeSocket):
    """Custom socket type for acoustic material nodes"""
    bl_idname = 'AcousticMaterialNodeSocket'
    bl_label = "Acoustic Material Socket"

    default_value: FloatProperty(default=0.0)

    def draw(self, context, layout, node, text):
        layout.label(text=text)

classes.append(AcousticMaterialNodeSocket)

class AcousticPropertiesNodeSocket(NodeSocket):
    """Custom socket type for acoustic properties nodes"""
    bl_idname = 'AcousticPropertiesNodeSocket'
    bl_label = "Acoustic Properties Socket"

    default_value: FloatProperty(default=0.0)

    def draw(self, context, layout, node, text):
        layout.label(text=text)

classes.append(AcousticPropertiesNodeSocket)

class AcousticValueNodeSocket(NodeSocket):
    """Custom socket type for acoustic value nodes"""
    bl_idname = 'AcousticValueNodeSocket'
    bl_label = "Acoustic Value Socket"

    default_value: FloatProperty(
        default=0.0,
        min=-1.0,
        max=1.0
    )

    default_path: StringProperty(
        subtype='FILE_PATH', 
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default='//'
    )

    identifier: StringProperty(
        name='identifier',
    )

    point_index: IntProperty(
        name='point_index',
    )

    def draw(self, context, layout, node, text):
        if self.is_linked or self.is_output:
            layout.label(text=text)
        else:
            layout.prop(self, "default_value", text=text, slider=True)

classes.append(AcousticValueNodeSocket)
