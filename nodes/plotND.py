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

from .baseND import AcousticMaterialNode

classes = []

# Custom node class
class ImageDisplayNode(AcousticMaterialNode):
    """Custom node to display an image"""
    bl_idname = 'ImageDisplayNode'
    bl_label = 'Image Display'
    bl_icon = 'IMAGE_DATA'
    
    pbraudio_type: StringProperty(default='AcousticProperties')

    # Property to hold the image
    image: PointerProperty(
        name="Image",
        type=bpy.types.Image,
        description="Image to display in the node"
    )
    
    # Optional: Custom node width
    node_width: bpy.props.FloatProperty(default=300.0)
    
    def init(self, context):
        # Create input socket
        self.inputs.new('NodeSocketFloat', 'Value')
        
        # Create output socket
        self.outputs.new('NodeSocketFloat', 'Result')
    
    def draw_buttons(self, context, layout):
        # Display image if one is selected
        if self.image:
            # Create a box for the image
            box = layout.box()
            box.scale_y = 1.0
            
            # Show image name
            row = box.row()
            row.label(text=self.image.name)
            
            # Display the image preview
            if self.image.preview:
#                box.template_icon(self.image.preview.icon_id, scale=100)
                box.template_preview(self.image)
            else:
                # Try to load preview
                self.image.reload()
                if self.image.preview:
#                    box.template_icon(self.image.preview.icon_id, scale=100)
                    box.template_preview(self.image)
                else:
                    box.label(text="No preview available")
            
            # Show image info
            if self.image.size[0] > 0:
                box.label(text=f"Size: {self.image.size[0]}x{self.image.size[1]}")
            
            # Open image button
            row = box.row()
            row.operator("image.open", text="Change Image").relative_path = True
            
        else:
            # Button to add an image
            layout.operator("image.open", text="Load Image").relative_path = True
    
    def draw_buttons_ext(self, context, layout):
        # Extended draw for more options
        layout.prop(self, "image")
        layout.prop(self, "node_width")
        
        if self.image:
            layout.separator()
            layout.operator("image.reload", text="Reload Image")
    
    def copy(self, node):
        # Handle copying of the node
        self.image = node.image
    
    def free(self):
        # Cleanup when node is removed
        pass
classes.append(ImageDisplayNode)
