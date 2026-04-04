import bpy
from bpy.types import Header
from bpy.props import EnumProperty

# Define the enum items
my_enum_items = [
    ('OPTION_A', "Option A", "First option"),
    ('OPTION_B', "Option B", "Second option"),
    ('OPTION_C', "Option C", "Third option"),
]

# Define the draw function for the header
def draw_my_enum(self, context):
    layout = self.layout
    layout.prop(context.scene, "my_enum_property", text="")

# Register the property
bpy.types.Scene.my_enum_property = EnumProperty(
    name="My Enum",
    description="A custom enum property",
    items=my_enum_items,
    default='OPTION_A'
)

# Prepend the draw function to NODE_HT_header
bpy.types.NODE_HT_header.prepend(draw_my_enum)

# Optional: Function to unregister everything
def unregister():
    del bpy.types.Scene.my_enum_property
    bpy.types.NODE_HT_header.remove(draw_my_enum)

# To use this in an addon, you'd typically wrap it in register/unregister functions:

def register():
    bpy.types.Scene.my_enum_property = EnumProperty(
        name="My Enum",
        description="A custom enum property",
        items=my_enum_items,
        default='OPTION_A'
    )
    bpy.types.NODEODE_HT_header.prepend(draw_my_enum)

def unregister():
    del bpy.types.Scene.my_enum_property
    bpy.types.NODE_HT_header.remove(draw_my_enum)


