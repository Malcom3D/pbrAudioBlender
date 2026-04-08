import bpy
from bpy.types import Menu
from bpy.props import EnumProperty

# Define the enum items
acoustic_shader_type_items = [
    ('OBJECT', "Object", "Edit Shader Node from Object"),
    ('WORLD', "World", "Edit Shader Node from World"),
    ('SOUND', "Sound", "Edit Shader Node from Sound"),
]

# Property group to store the enum value
class AcousticNodeEditorProperties(bpy.types.PropertyGroup):
    acoustic_shader_type: EnumProperty(
        name="Acoustic Shader Node Editor Type",
        description="Select an option",
        items=acoustic_shader_type_items,
        default="OBJECT",
    )


def draw_acoustic_shader_type(self, context):
    layout = self.layout

    if context.scene.render.engine == 'PBRAUDIO' and context.space_data.tree_type == 'AcousticNodeTree': 
#       if space.type == "NODE_EDITOR" and not space.pin:
       # Create a dropdown menu directly
       row = layout.row(align=True)
       row.prop(context.scene.acoustic_node_editor_props, "acoustic_shader_type", text="")

       if context.scene.acoustic_node_editor_props.acoustic_shader_type == 'OBJECT':
           row.label(icon='OBJECT_DATA')
       elif context.scene.acoustic_node_editor_props.acoustic_shader_type == 'WORLD':
           row.label(icon='WORLD')
       elif context.scene.acoustic_node_editor_props.acoustic_shader_type == 'SOUND':
           row.label(icon='SPEAKER')
    
# Register and add to NODE_MT_editor_menus
def register():
    bpy.utils.register_class(AcousticNodeEditorProperties)
    
    # Add the property to the scene
    bpy.types.Scene.acoustic_node_editor_props = bpy.props.PointerProperty(type=AcousticNodeEditorProperties)
    
    bpy.types.NODE_MT_editor_menus.prepend(draw_acoustic_shader_type)

def unregister():
    # Remove from menu
    bpy.types.NODE_MT_editor_menus.remove(draw_acoustic_shader_type)
    # Unregister classes
    bpy.utils.unregister_class(AcousticNodeEditorProperties)
    # Remove the property
    del bpy.types.Scene.acoustic_node_editor_props
