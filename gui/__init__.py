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
#from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

classes = []

from . import enginePT, materialPT, worldPT, dataPT, outputPT, scenePT, view3d_menu, nodetree_switch

for mod in (enginePT, materialPT, worldPT, dataPT, outputPT, scenePT, view3d_menu):
    classes += mod.classes

def register():
    # Unregister blender DATA_PT_empty
    bpy.utils.unregister_class(bpy.types.DATA_PT_empty)

    for cls in classes:
        register_class(cls)

    # Add menu to 3D Viewport Add menu
    bpy.types.VIEW3D_MT_add.append(view3d_menu.menu_func)

    # Add acoustic shader type menu to nodetree menu
    nodetree_switch.register()

def unregister():
    """Unregister all classes and properties"""
    # Remove acoustic shader type menu to nodetree menu
    nodetree_switch.unregister()

    # Remove menu from 3D Viewport Add menu
    bpy.types.VIEW3D_MT_add.remove(view3d_menu.menu_func)
    for cls in reversed(classes):
        unregister_class(cls)

    # Register blender DATA_PT_empty
    bpy.utils.register_class(bpy.types.DATA_PT_empty)
