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

    def sync_data(self, context):
        # input absorption
        if not self.inputs[0].is_linked and not self.pbraudio_absorption == self.inputs[0].default_value:
           # the value of the slider is the input socket, write it's value to self.pbraudio_absorption to be readed from exporter and used for computation
           self.pbraudio_absorption = self.inputs[0].default_value
        # input reflection
        if not self.inputs[1].is_linked and not self.pbraudio_reflection == self.inputs[1].default_value:
           # the value of the slider is the input socket, write it's value to self.pbraudio_reflection to be readed from exporter and used for computation
           self.pbraudio_reflection = self.inputs[1].default_value
        # input reflection
        if not self.inputs[2].is_linked and not self.pbraudio_reflection == self.inputs[2].default_value:
           # the value of the slider is the input socket, write it's value to self.pbraudio_reflection to be readed from exporter and used for computation
           self.pbraudio_reflection = self.inputs[2].default_value
        # input scattering
        if not self.inputs[3].is_linked and not self.pbraudio_scattering == self.inputs[3].default_value:
           # the value of the slider is the input socket, write it's value to self.pbraudio_scattering to be readed from exporter and used for computation
           self.pbraudio_scattering = self.inputs[3].default_value

    pbraudio_absorption: FloatProperty(
        name="absorption",
        description="WideBand absorption coeff",
        default=0.5,
        min=0.0,
        max=1.0
    )

    pbraudio_refraction: FloatProperty(
        name="reflection",
        description="WideBand reflection coeff",
        default=0.5,
        min=0.0,
        max=1.0
    )

    pbraudio_reflection: FloatProperty(
        name="reflection",
        description="WideBand reflection coeff",
        default=0.5,
        min=0.0,
        max=1.0
    )

    pbraudio_scattering: FloatProperty(
        name="scattering",
        description="WideBand scattering coeff",
        default=0.5,
        min=0.0,
        max=1.0
    )

    pbraudio_type: StringProperty(default='AcousticProperties')

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticProperties")
        self.inputs.new('AcousticValueNodeSocket', "absorption")
        self.inputs.new('AcousticValueNodeSocket', "refraction")
        self.inputs.new('AcousticValueNodeSocket', "reflection")
        self.inputs.new('AcousticValueNodeSocket', "scattering")

    def socket_value_update(context):
        self.sync_data(context)

classes.append(AcousticPropertiesNode)
