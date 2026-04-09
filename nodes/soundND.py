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
import os, sys
from bpy.types import Node
from bpy.props import IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList
from bpy_extras.io_utils import ImportHelper

from .baseND import AcousticSoundNode

classes = []

class SoundOutputNode(AcousticSoundNode):
    """Node to combine multiple frequency responses into a spatial response"""
    bl_idname = 'SoundOutputNode'
    bl_label = 'Recorder Input Node'
    bl_icon = 'SOUND'

    pbraudio_type: StringProperty(default='SoundOutputNode')

classes.append(SoundOutputNode)

class SoundInputNode(AcousticSoundNode):
    """Node to combine multiple frequency responses into a spatial response"""
    bl_idname = 'SoundInputNode'
    bl_label = 'Recorder Input Node'
    bl_icon = 'SOUND'

    pbraudio_type: StringProperty(default='SoundInputNode')

classes.append(SoundInputNode)
