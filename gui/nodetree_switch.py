import bpy
from bpy.types import Header
from bpy.props import EnumProperty

# Define the draw function for the header
def draw_shader_type(self, context):
    layout = self.layout
    layout.prop(context.scene, "acoustic_shader_type", text="")

def register():
    bpy.types.NODEODE_HT_header.prepend(draw_shader_type)

def unregister():
    bpy.types.NODE_HT_header.remove(draw_shader_type)


