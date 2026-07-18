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
from bpy.types import Operator
from bpy.props import StringProperty, PointerProperty

classes = []

class PBRAUDIO_OT_collection_add(bpy.types.Operator):
    bl_idname = "collection.pbraudio_add"
    bl_label = "Add pbrAudio Properties to Collection"
    
    # Store collection name as property
    collection_name: bpy.props.StringProperty()
    
    def execute(self, context):
        collection = bpy.data.collections.get(self.collection_name)
        if collection:
            collision_collection['is_valid'] = True
            collision_collection['physics'] = False
            collision_collection['prebake'] = False
            collision_collection['bake'] = False
            collision_collection['fracture'] = False
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_collection_add)
