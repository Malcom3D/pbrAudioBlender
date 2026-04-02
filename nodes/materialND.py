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
from bpy.props import StringProperty, PointerProperty, FloatProperty

from ..properties import materialPG
from .baseND import DefaultAcousticShaderNode

classes = []

class AcousticShaderNode(DefaultAcousticShaderNode):
    """Acoustic shader node"""
    bl_idname = 'AcousticShaderNode'
    bl_label = "AcousticShader"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

classes.append(AcousticShaderNode)

class GlassShaderNode(DefaultAcousticShaderNode):
    """Glass acoustic shader node"""
    bl_idname = 'GlassShaderNode'
    bl_label = "Glass"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 5700
        self.pbraudio_sound_speed_max = 5600
        self.pbraudio_sound_speed_min = 5800
        self.pbraudio_young_modulus = 70
        self.pbraudio_poisson_ratio = 0.22
        self.pbraudio_density = 2500
        self.pbraudio_damping = 0.3
        self.pbraudio_friction = 0.2
        self.pbraudio_roughness = 0.001
classes.append(GlassShaderNode)

class AluminumShaderNode(DefaultAcousticShaderNode):
    """Aluminum acoustic shader node"""
    bl_idname = 'AluminumShaderNode'
    bl_label = "Aluminum"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 6300
        self.pbraudio_young_modulus = 69
        self.pbraudio_poisson_ratio = 0.33
        self.pbraudio_density = 2700
        self.pbraudio_damping = 0.005
        self.pbraudio_friction = 0.47
        self.pbraudio_roughness = 0.04
        self.pbraudio_low_frequency = 300
        self.pbraudio_high_frequency = 10000
classes.append(AluminumShaderNode)

class AcrylicShaderNode(DefaultAcousticShaderNode):
    """Acrylic acoustic shader node"""
    bl_idname = 'AcrylicShaderNode'
    bl_label = "Acrylic"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 2680
        self.pbraudio_young_modulus = 3.15
        self.pbraudio_poisson_ratio = 0.36
        self.pbraudio_density = 1283
        self.pbraudio_damping = 2
        self.pbraudio_friction = 0.5
        self.pbraudio_roughness = 0.1
classes.append(AcrylicShaderNode)

class AsphaltShaderNode(DefaultAcousticShaderNode):
    """Asphalt acoustic shader node"""
    bl_idname = 'AsphaltShaderNode'
    bl_label = "Asphalt"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 2000
        self.pbraudio_young_modulus = 2.5
        self.pbraudio_poisson_ratio = 0.3
        self.pbraudio_density = 2400
        self.pbraudio_damping = 2
        self.pbraudio_friction = 0.7
        self.pbraudio_roughness = 0.5
        self.pbraudio_low_frequency = 5
        self.pbraudio_high_frequency = 100
classes.append(AsphaltShaderNode)

class ConcreteShaderNode(DefaultAcousticShaderNode):
    """Concrete acoustic shader node"""
    bl_idname = 'ConcreteShaderNode'
    bl_label = "Concrete"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 3600
        self.pbraudio_young_modulus = 31
        self.pbraudio_poisson_ratio = 0.16
        self.pbraudio_density = 2320
        self.pbraudio_damping = 5
        self.pbraudio_friction = 0.5
        self.pbraudio_roughness = 0.75
        self.pbraudio_low_frequency = 5
        self.pbraudio_high_frequency = 500
classes.append(ConcreteShaderNode)

class MarbleShaderNode(DefaultAcousticShaderNode):
    """Marble acoustic shader node"""
    bl_idname = 'MarbleShaderNode'
    bl_label = "Marble"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 5000
        self.pbraudio_young_modulus = 40
        self.pbraudio_poisson_ratio = 0.23
        self.pbraudio_density = 2563
        self.pbraudio_damping = 1.0
        self.pbraudio_friction = 0.3
        self.pbraudio_roughness = 0.01
classes.append(MarbleShaderNode)

class IronShaderNode(DefaultAcousticShaderNode):
    """Iron acoustic shader node"""
    bl_idname = 'IronShaderNode'
    bl_label = "Iron"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 4723
        self.pbraudio_young_modulus = 130
        self.pbraudio_poisson_ratio = 0.24
        self.pbraudio_density = 7150
        self.pbraudio_damping = 2
        self.pbraudio_friction = 0.15
        self.pbraudio_roughness = 0.12
        self.pbraudio_low_frequency = 25
classes.append(IronShaderNode)

class TimberShaderNode(DefaultAcousticShaderNode):
    """Timber acoustic shader node"""
    bl_idname = 'TimberShaderNode'
    bl_label = "Timber"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed = 3500
        self.pbraudio_young_modulus = 12
        self.pbraudio_poisson_ratio = 0.4
        self.pbraudio_density = 610
        self.pbraudio_damping = 0.8
        self.pbraudio_friction = 0.3
        self.pbraudio_roughness = 0.2
        self.pbraudio_low_frequency = 100
        self.pbraudio_high_frequency = 2000
classes.append(TimberShaderNode)

class GypsumShaderNode(DefaultAcousticShaderNode):
    """Gypsum acoustic shader node"""
    bl_idname = 'GypsumShaderNode'
    bl_label = "Gypsum"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

        self.pbraudio_sound_speed_min = 1400
        self.pbraudio_sound_speed_max = 1600
        self.pbraudio_young_modulus_min = 2
        self.pbraudio_young_modulus_max = 4
        self.pbraudio_poisson_ratio_min = 0.24
        self.pbraudio_poisson_ratio_max = 0.35
        self.pbraudio_density_min = 600
        self.pbraudio_density_max = 1200
        self.pbraudio_damping_min = 1
        self.pbraudio_damping_max = 5
        self.pbraudio_low_frequency_min = 10
        self.pbraudio_low_frequency_max = 20
        self.pbraudio_high_frequency_min = 2000
        self.pbraudio_high_frequency_max = 4000

        self.pbraudio_sound_speed = 1500
        self.pbraudio_young_modulus = 2.3
        self.pbraudio_poisson_ratio = 0.3
        self.pbraudio_density = 825
        self.pbraudio_damping = 2
        self.pbraudio_low_frequency = 5
        self.pbraudio_high_frequency = 3700
classes.append(GypsumShaderNode)

#class ShaderNode(DefaultAcousticShaderNode):
#    """Template acoustic shader node"""
#    bl_idname = 'ShaderNode'
#    bl_label = "Shader"
#
#    def init(self, context):
#        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
#        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")
#
#        self.pbraudio_sound_speed =
#        self.pbraudio_young_modulus =
#        self.pbraudio_poisson_ratio =
#        self.pbraudio_density =
#        self.pbraudio_damping =
#        self.pbraudio_friction =
#        self.pbraudio_roughness =
#        self.pbraudio_low_frequency =
#        self.pbraudio_high_frequency =
#classes.append(ShaderNode)
