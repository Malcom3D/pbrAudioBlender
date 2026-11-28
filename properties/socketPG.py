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
        name="Enable Link",
        description="Enable or disable the pbrAudioDAW link",
        default=False,
    )
    
    show_advanced: BoolProperty(
        name="Advanced Options",
        description="Show advanced link options",
        default=False,
    )
    
    host: StringProperty(
        name="Host",
        description="Host IP of pbrAudioDAW",
        default="localhost",
    )
    
    port: IntProperty(
        name="Port",
        description="Port number of pbrAudio",
        default=55555,
        min=1024,
        max=65535,
    )

classes.append(PBRAudioSocketProperties)
