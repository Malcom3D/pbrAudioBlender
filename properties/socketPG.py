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
from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty

classes = []

class PBRAudioSocketProperties(PropertyGroup):
    """Socket server properties for pbrAudio"""
    
    enabled: BoolProperty(
        name="Enable Server",
        description="Enable or disable the socket server",
        default=False,
    )
    
    show_advanced: BoolProperty(
        name="Advanced Options",
        description="Show advanced socket options",
        default=False,
    )
    
    host: StringProperty(
        name="Host",
        description="Host IP to bind (use 'localhost' or '0.0.0.0' for all interfaces)",
        default="localhost",
    )
    
    port: IntProperty(
        name="Port",
        description="Port number to listen on",
        default=55555,
        min=1024,
        max=65535,
    )

classes.append(PBRAudioSocketProperties)
