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
from bpy.props import PointerProperty, StringProperty, FloatProperty, IntProperty

from .baseND import AcousticMaterialNode

classes = []

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
    
    # Custom node width
    node_width: FloatProperty(
        name="Node Width",
        default=400.0,
        min=200.0,
        max=1000.0,
        description="Width of the node in pixels"
    )
    
    # Image display scale
    image_scale: FloatProperty(
        name="Image Scale",
        default=1.0,
        min=0.1,
        max=5.0,
        description="Scale factor for the displayed image"
    )
    
    # Display mode
    display_mode: bpy.props.EnumProperty(
        name="Display Mode",
        items=[
            ('FIT', "Fit", "Fit image to node width"),
            ('ACTUAL', "Actual Size", "Show image at actual pixel size"),
            ('SCALED', "Scaled", "Scale image by factor"),
        ],
        default='FIT'
    )
    
    # Show image info
    show_info: bpy.props.BoolProperty(
        name="Show Info",
        default=True,
        description="Show image information"
    )
    
    def init(self, context):
        # Create input socket
        self.inputs.new('NodeSocketFloat', 'Value')
        
        # Create output socket
        self.outputs.new('NodeSocketFloat', 'Result')
    
    def draw_buttons(self, context, layout):
        # Display image if one is selected
        if self.image:
            # Ensure image is loaded
            if not self.image.has_data:
                self.image.reload()
            
            # Create a box for the image
            box = layout.box()
            
            # Show image name and info
            if self.show_info:
                row = box.row()
                row.label(text=f"Image: {self.image.name}")
                
                if self.image.size[0] > 0:
                    row = box.row()
                    row.label(text=f"Size: {self.image.size[0]} × {self.image.size[1]} pixels")
                    
                    # Show color depth
                    if hasattr(self.image, 'depth'):
                        row = box.row()
                        row.label(text=f"Depth: {self.image.depth}-bit")
            
            # Display the image using custom operator
            row = box.row()
            op = row.operator("node.pbraudio_display_image", text="", icon='IMAGE_DATA')
            op.node_name = self.name
            op.tree_name = self.id_data.name
            
            # Display settings
            box.prop(self, "display_mode")
            if self.display_mode == 'SCALED':
                box.prop(self, "image_scale")
            box.prop(self, "show_info")
            
            # Open image button
            row = box.row()
            row.operator("image.open", text="Change Image").relative_path = True
            
            # Reload button
            row.operator("image.reload", text="Reload")
            
        else:
            # Button to add an image
            layout.operator("image.open", text="Load Image").relative_path = True
    
    def draw_buttons_ext(self, context, layout):
        # Extended draw for more options
        layout.prop(self, "image")
        layout.prop(self, "node_width")
        layout.prop(self, "display_mode")
        if self.display_mode == 'SCALED':
            layout.prop(self, "image_scale")
        layout.prop(self, "show_info")
        
        if self.image:
            layout.separator()
            # Image properties
            col = layout.column()
            col.enabled = False
            if self.image.size[0] > 0:
                col.label(text=f"Dimensions: {self.image.size[0]} × {self.image.size[1]}")
                col.label(text=f"Color Space: {self.image.colorspace_settings.name}")
    
    def copy(self, node):
        # Handle copying of the node
        self.image = node.image
        self.node_width = node.node_width
        self.image_scale = node.image_scale
        self.display_mode = node.display_mode
        self.show_info = node.show_info
    
    def free(self):
        # Cleanup when node is removed
        pass

classes.append(ImageDisplayNode)

class PBRAUDIO_OT_display_image(bpy.types.Operator):
    """Operator to display image in node"""
    bl_idname = "node.pbraudio_display_image"
    bl_label = "Display Image"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    node_name: StringProperty()
    tree_name: StringProperty()
    
    def execute(self, context):
        # This operator doesn't do anything in execute
        # It's just used to trigger the draw callback
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
    
    def draw(self, context):
        layout = self.layout
        
        # Find the node
        node_tree = bpy.data.node_groups.get(self.tree_name)
        if not node_tree:
            return
        
        node = node_tree.nodes.get(self.node_name)
        if not node or not node.image:
            return
        
        image = node.image
        
        # Calculate display size
        if node.display_mode == 'FIT':
            # Fit to node width (minus padding)
            max_width = node.node_width - 40
            if image.size[0] > max_width:
                scale = max_width / image.size[0]
                width = int(image.size[0] * scale)
                height = int(image.size[1] * scale)
            else:
                width = image.size[0]
                height = image.size[1]
        elif node.display_mode == 'SCALED':
            width = int(image.size[0] * node.image_scale)
            height = int(image.size[1] * node.image_scale)
        else:  # ACTUAL
            width = image.size[0]
            height = image.size[1]
        
        # Limit maximum size
        max_height = 600
        if height > max_height:
            scale = max_height / height
            width = int(width * scale)
            height = int(height * scale)
        
        # Display the image
        if image.gl_load():
            self.report({'ERROR'}, "Failed to load image")
            return
        
        # Create a custom layout with the image
        col = layout.column()
        
        # Add some padding
        col.separator(factor=0.5)
        
        # Draw the image
        row = col.row()
        row.alignment = 'CENTER'
        
        # Use template_ID_preview for better image display
        if hasattr(bpy.types, 'UILayout'):
            # Try to use template_ID_preview if available (Blender 2.8+)
            row.template_ID_preview(image, open="image.open", rows=3, cols=3)
        else:
            # Fallback to template_icon
            if image.preview:
                row.template_icon(icon_value=image.preview.icon_id, scale=10)
            else:
                row.label(text="No preview available")
        
        # Show dimensions
        if node.show_info:
            col.separator()
            row = col.row()
            row.alignment = 'CENTER'
            row.label(text=f"Display: {width} × {height} pixels")
        
        col.separator(factor=0.5)

classes.append(PBRAUDIO_OT_display_image)
