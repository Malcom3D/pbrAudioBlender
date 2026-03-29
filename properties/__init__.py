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
from bpy.props import PointerProperty, CollectionProperty, IntProperty
from bpy.utils import register_class, unregister_class

classes = []

from . import objectPG, scenePG, worldPG, materialPG

for mod in (objectPG, scenePG, worldPG, materialPG):
    classes += mod.classes

def register():
    for cls in classes:
        register_class(cls)

    # Register property groups
    bpy.types.Scene.pbraudio = PointerProperty(type=scenePG.PBRAudioSceneProperties)
    bpy.types.Object.pbraudio = PointerProperty(type=objectPG.PBRAudioObjectProperties)
    bpy.types.Object.pbraudio_connected = CollectionProperty(type=objectPG.PBRAudioConnectedObjectList)
    bpy.types.Object.pbraudio_connected_index = IntProperty(name="Index", default=-1, description="Active index in the connected object list")
    bpy.types.Object.pbraudio_shard = CollectionProperty(type=objectPG.PBRAudioShardObjectList)
    bpy.types.Object.pbraudio_shard_index = IntProperty(name="Index", default=-1, description="Active index in the shard object list")
    bpy.types.World.pbraudio = PointerProperty(type=worldPG.PBRAudioWorldProperties)
    # pbrAudio World Enviroment Properties
#    bpy.types.World.pbraudioEnv = CollectionProperty(type=worldPG.PBRAudioWorldEnvironmentProperties)

def unregister():
    """Unregister all classes and properties"""
    # Remove property groups
#    del bpy.types.World.pbraudioEnv
    del bpy.types.World.pbraudio
    del bpy.types.Object.pbraudio_shard_index
    del bpy.types.Object.pbraudio_shard
    del bpy.types.Object.pbraudio_connected_index
    del bpy.types.Object.pbraudio_connected
    del bpy.types.Object.pbraudio
    del bpy.types.Scene.pbraudio

    for cls in reversed(classes):
        unregister_class(cls)
