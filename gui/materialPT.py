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
from bpy.types import Panel, UIList

classes = []

class PBRAUDIO_PT_material_panel(Panel):
    """Panel for pbrAudio material settings"""
    bl_label = 'Acoustic Material'
    bl_idname = 'PBRAUDIO_PT_material_panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO' and context.object is not None

    def draw(self, context):
        layout = self.layout
        object = context.object
        snode = object.pbraudio
        for world in bpy.data.worlds:
            if hasattr(world, 'pbraudio'):
                AcousticDomain = world.pbraudio.acoustic_domain

        if not object == AcousticDomain:
                layout.template_ID(snode, "nodetree", new="material.pbraudio_add")
                if not object.pbraudio.ground_disable:
                    layout.prop(snode, "ground", toggle=True)
        else:
            layout.label(text='Acoustic World Domain.')
            layout.label(text='Settings are in the world panel.')

classes.append(PBRAUDIO_PT_material_panel)

class PBRAUDIO_CONNECTED_UL_object_list(UIList):
    """UIList for displaying objects with float values"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Customize the draw for each item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Create a row with object name and float slider
            row = layout.row(align=True)
            row.label(text=item.connected_object)
            row.prop(item, "connected_value", text="", slider=True)
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.connected_object)
classes.append(PBRAUDIO_CONNECTED_UL_object_list)

class PBRAUDIO_CONNECTED_object_list(Panel):
    """Panel in Material Properties tab"""
    bl_label = "Connected Object List"
    bl_idname = "MATERIAL_PT_connected_object_list"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO' and context.object is not None
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Collection info
        collection = obj.users_collection[0]

        if collection:
            layout.label(text=f"Collection: {collection.name}", icon='OUTLINER_COLLECTION')
        else:
            layout.label(text="Object not in any collection", icon='ERROR')
        
        layout.separator()
        
        # List of objects with float values
        row = layout.row()
        row.template_list(
            "PBRAUDIO_CONNECTED_UL_object_list", "", obj, "pbraudio_connected", obj, "pbraudio_connected_index", rows=5)
        
        # Control buttons
        col = row.column(align=True)
        col.operator("object.pbraudio_add_to_list", icon='ADD', text="")
        col.operator("object.pbraudio_remove_from_list", icon='REMOVE', text="")
        col.separator()
        col.operator("object.pbraudio_refresh_list", icon='FILE_REFRESH', text="")
        col.operator("object.pbraudio_clear_list", icon='TRASH', text="")

        layout.prop_search(obj.pbraudio, "selected_connected_object", collection, "objects", icon='OBJECT_DATA')
        
classes.append(PBRAUDIO_CONNECTED_object_list)
