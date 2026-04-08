import bpy
from bpy.types import Header
from bpy.props import EnumProperty

def draw_shader_type(self, context):
    """Draw the shader type selector in the node editor header"""
    if context.space_data.tree_type == 'AcousticNodeTree':
        layout = self.layout
        row = layout.row(align=True)
        row.prop(context.scene.pbraudio, "acoustic_shader_type", text="")
        
#        if context.scene.pbraudio.acoustic_shader_type == 'OBJECT':
        if bpy.data.node_groups[context.space_data.node_tree.name].pbraudio_type == 'OBJECT':
            row.label(icon='OBJECT_DATA')
#        elif context.scene.pbraudio.acoustic_shader_type == 'WORLD':
        elif bpy.data.node_groups[context.space_data.node_tree.name].pbraudio_type == 'WORLD':
            row.label(icon='WORLD')
#        elif context.scene.pbraudio.acoustic_shader_type == 'SOUND':
        elif bpy.data.node_groups[context.space_data.node_tree.name].pbraudio_type == 'SOUND':
            row.label(icon='SPEAKER')

def register():
    # Register to draw in the node editor header
    bpy.types.NODE_HT_header.append(draw_shader_type)
#    bpy.types.NODE_MT_editor_menus.prepend(draw_shader_type)

def unregister():
    # Remove from node editor header
    bpy.types.NODE_HT_header.remove(draw_shader_type)
#    bpy.types.NODE_MT_editor_menus.remove(draw_shader_type)
