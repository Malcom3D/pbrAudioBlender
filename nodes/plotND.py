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

import os
import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from bpy.types import Node, ShaderNodeCustomGroup
from bpy.props import PointerProperty, StringProperty

from .baseND import AcousticBaseNode

classes = []

bpy.types.WindowManager.image = bpy.props.PointerProperty(name='Image', type=bpy.types.Image)

class ResponsePreviewNode(AcousticBaseNode):
    """Custom node to display an image"""
    bl_idname = 'ResponsePreviewNode'
    bl_label = 'Preview Frequency Response Node'
    bl_icon = 'IMAGE_DATA'
    
    pbraudio_type: StringProperty(default='AcousticProperties')

    def init(self, context):
        self.inputs.new('AcousticValueNodeSocket', "Frequency Response")

    def draw_buttons(self, context, layout):
        layout.template_ID_preview(context.window_manager, 'image', open='image.open')
        layout.operator("pbraudio.big_preview")
    
classes.append(ResponsePreviewNode)
