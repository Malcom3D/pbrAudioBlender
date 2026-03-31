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
from bpy.types import Node
from bpy.props import StringProperty, PointerProperty, IntProperty, FloatProperty, CollectionProperty

from .baseND import AcousticMaterialNode

from ..properties import materialPG

classes = []

class AcousticPropertiesNode(AcousticMaterialNode):
    """Acoustic properties node"""
    bl_idname = 'AcousticPropertiesNode'
    bl_label = "Acoustic Properties"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticProperties")
        self.inputs.new('AcousticPropertiesNodeSocket', "absorption", slider=True)
        self.inputs.new('AcousticValueNodeSocket', "refraction")
        self.inputs.new('AcousticValueNodeSocket', "reflection")
        self.inputs.new('AcousticValueNodeSocket', "scattering")

classes.append(AcousticPropertiesNode)

class DispertionPatternGraph(AcousticMaterialNode):
    """Dispertion Pattern Graph node"""
    bl_idname = 'DispertionPatternGraph'
    bl_label = "Dispertion Pattern Graph"

    def init(self, context):
        pass

classes.append(DispertionPatternGraph)
