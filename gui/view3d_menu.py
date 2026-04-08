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
from bpy.types import Menu

classes = []

class VIEW3D_MT_pbraudio_add(Menu):
    """pbrAudio add menu"""
    bl_idname = "VIEW3D_MT_pbraudio_add"
    bl_label = "pbrAudio"

    def draw(self, context):
        layout = self.layout
        
        # Sources
        layout.menu("VIEW3D_MT_pbraudio_sources", text="Sources", icon='SPEAKER')
        
        # Outputs
        layout.menu("VIEW3D_MT_pbraudio_outputs", text="Outputs", icon='LIGHT_SPOT')
        
        # Separator
        layout.separator()
        
        # Utilities
        layout.operator("object.pbraudio_add_properties", text="Add Properties", icon='PROPERTIES')

classes.append(VIEW3D_MT_pbraudio_add)

class VIEW3D_MT_pbraudio_sources(Menu):
    """pbrAudio sources menu"""
    bl_idname = "VIEW3D_MT_pbraudio_sources"
    bl_label = "Sources"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.pbraudio_add_spherical_source", text="Spherical Source", icon='MESH_UVSPHERE')
        layout.operator("object.pbraudio_add_planar_source", text="Planar Source", icon='MESH_PLANE')

classes.append(VIEW3D_MT_pbraudio_sources)

class VIEW3D_MT_pbraudio_outputs(Menu):
    """pbrAudio outputs menu"""
    bl_idname = "VIEW3D_MT_pbraudio_outputs"
    bl_label = "Outputs"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.pbraudio_add_world_environment", text="World Environment", icon='WORLD')

classes.append(VIEW3D_MT_pbraudio_outputs)

def menu_func(self, context):
    """Add pbrAudio menu to Add menu"""
    if context.scene.render.engine == 'PBRAUDIO':
        self.layout.menu("VIEW3D_MT_pbraudio_add", icon='SOUND')

classes.append(menu_func)
