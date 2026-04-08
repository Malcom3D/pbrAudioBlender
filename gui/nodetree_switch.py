#import bpy
#from bpy.types import Header
#from bpy.props import EnumProperty

#def draw_shader_type(self, context):
#    """Draw the shader type selector in the node editor header"""
#    if context.space_data.tree_type == 'AcousticNodeTree':
#        layout = self.layout
#        row = layout.row(align=True)
#        row.prop(context.scene.pbraudio, "acoustic_shader_type", text="")
#        
#        if context.scene.pbraudio.acoustic_shader_type == 'OBJECT':
#            row.label(icon='OBJECT_DATA')
#        elif context.scene.pbraudio.acoustic_shader_type == 'WORLD':
#            row.label(icon='WORLD')
#        elif context.scene.pbraudio.acoustic_shader_type == 'SOUND':
#            row.label(icon='SPEAKER')
#
#def register():
#    # Register to draw in the node editor header
#    bpy.types.NODE_HT_header.append(draw_shader_type)
#    bpy.types.NODE_MT_editor_menus.prepend(draw_shader_type)
#
#def unregister():
#    # Remove from node editor header
#    bpy.types.NODE_HT_header.remove(draw_shader_type)
#    bpy.types.NODE_MT_editor_menus.remove(draw_shader_type)

import bpy

class NODE_MT_acoustic_shader_type(bpy.types.Menu):
    bl_label = "Shader Type"
    bl_idname = "NODE_MT_acoustic_shader_type"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.pbraudio, "acoustic_shader_type", expand=True)

def draw_header_menu(self, context):
    if context.space_data.tree_type == 'AcousticNodeTree':
        layout = self.layout
        layout.menu("NODE_MT_acoustic_shader_type", text="", icon='SHADING_TEXTURE')

def register():
    bpy.utils.register_class(NODE_MT_acoustic_shader_type)
    bpy.types.NODE_HT_header.append(draw_header_menu)

def unregister():
    bpy.types.NODE_HT_header.remove(draw_header_menu)
    bpy.utils.unregister_class(NODE_MT_acoustic_shader_type)
