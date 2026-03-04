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
from bpy.props import StringProperty, FloatProperty
from bpy.types import Operator

classes = []

class OBJECT_OT_pbraudio_add_to_list(Operator):
    """Add selected objects to the list"""
    bl_idname = "object.pbraudio_add_to_list"
    bl_label = "Add Selected Objects"
    bl_description = "Add selected objects from the collection to the list"
    
    def execute(self, context):
        obj = context.object
        
        # Get the collection the object belongs to
        collection = obj.users_collection[0]
        
        # Add objects from the collection to the list
        for collection_obj in collection.objects.values():
            # Check if object is already in the list
            exists = False
            for item in obj.pbraudio_connected.values():
                if item.connected_object == collection_obj.name:
                    exists = True
                    break
            
            # Add if not already in list
            if not exists:
                new_item = obj.pbraudio_connected.add()
                new_item.connected_object = collection_obj.name
                new_item.connected_value = 0.5
        
        return {'FINISHED'}
classes.append(OBJECT_OT_pbraudio_add_to_list)

class OBJECT_OT_pbraudio_remove_from_list(Operator):
    """Remove selected item from the list"""
    bl_idname = "object.pbraudio_remove_from_list"
    bl_label = "Remove Selected"
    bl_description = "Remove selected item from the list"
    
    def execute(self, context):
        obj = context.object
        
        # Remove the active item
        if obj.pbraudio_connected_index >= 0 and obj.pbraudio_connected_index < len(obj.pbraudio_connected):
            obj.pbraudio_connected.remove(obj.pbraudio_connected_index)
            
            # Adjust index if needed
            if obj.pbraudio_connected_index >= len(obj.pbraudio_connected):
                obj.pbraudio_connected_index = len(obj.pbraudio_connected) - 1
        
        return {'FINISHED'}
classes.append(OBJECT_OT_pbraudio_remove_from_list)

class OBJECT_OT_pbraudio_clear_list(Operator):
    """Clear all items from the list"""
    bl_idname = "object.pbraudio_clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items from the list"
    
    def execute(self, context):
        obj = context.object
        
        # Clear the list
        obj.pbraudio_connected.clear()
        obj.pbraudio_connected_index = -1
        
        return {'FINISHED'}
classes.append(OBJECT_OT_pbraudio_clear_list)

class OBJECT_OT_pbraudio_refresh_list(Operator):
    """Refresh list with objects from collection"""
    bl_idname = "object.pbraudio_refresh_list"
    bl_label = "Refresh List"
    bl_description = "Refresh list with objects from the collection"
    
    def execute(self, context):
        obj = context.object
        
        # Get the collection the object belongs to
        collection = obj.users_collection[0]
        
        # Clear existing list
        obj.pbraudio_connected.clear()
        
        # Add all objects from collection
        for collection_obj in collection.objects.values():
            new_item = obj.pbraudio_connected.add()
            new_item.connected_object = collection_obj.name
            new_item.connected_value = 0.5
        
        obj.pbraudio_connected_index = 0 if collection.objects else -1
        
        return {'FINISHED'}
classes.append(OBJECT_OT_pbraudio_refresh_list)
