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
from bpy.props import StringProperty, PointerProperty, FloatProperty

from ..properties import materialPG

classes = []

class AcousticMaterialNode(Node):
    """Base class for all acoustic material nodes"""
    bl_idname = 'AcousticMaterialNode'
    bl_label = "Acoustic Material Node"
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AcousticMaterialNodeTree'

classes.append(AcousticMaterialNode)

#class AudioInputNode(AcousticMaterialNode):
#    """Audio input node"""
#    bl_idname = 'AudioInputNode'
#    bl_label = "Audio Input"
#
#    audio_file: StringProperty(
#        name="Audio File",
#        description="Path to audio file",
#        subtype='FILE_PATH'
#    )
#
#    def init(self, context):
#        self.outputs.new('AudioNodeSocket', "Audio Signal")
#
#classes.append(AudioInputNode)

class AcousticPropertiesNode(AcousticMaterialNode):
    """Acoustic properties node"""
    bl_idname = 'AcousticPropertiesNode'
    bl_label = "Acoustic Properties"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticProperties")
        self.inputs.new('AcousticPropertiesNodeSocket', "absorption")
        self.inputs.new('AcousticPropertiesNodeSocket', "refraction")
        self.inputs.new('AcousticPropertiesNodeSocket', "reflection")
        self.inputs.new('AcousticPropertiesNodeSocket', "scattering")

classes.append(AcousticPropertiesNode)

class AcousticShaderNode(AcousticMaterialNode):
    """Acoustic shader node"""
    bl_idname = 'AcousticShaderNode'
    bl_label = "AcousticShader"

    """Acoustic Shader properties"""
    pbraudio_sound_speed: FloatProperty(
        name="Sound Speed in m/s",
        default=1000.0,
        soft_min=0.0,
        soft_max=20000.0
    )

    pbraudio_young_modulus: FloatProperty(
        name="Young modulus in GPa",
        default=1.0,
        min=0.0,
        soft_max=1500.0
    )

    pbraudio_poisson_ratio: FloatProperty(
        name="Poisson Ratio",
        default=0.46,
        min=-1.0,
        max=0.5
    )

    pbraudio_density: FloatProperty(
        name="Density in kg/m³",
        default=800.0,
        min=0.0,
        soft_max=25000.0
    )

    pbraudio_damping: FloatProperty(
        name="Rayleigh Damping in %",
        default=5,
        min=0.0,
        max=100
    )

    pbraudio_friction: FloatProperty(
        name="Friction",
        default=0.0,
        min=0.0,
        soft_max=1.0
    )

    pbraudio_roughness: FloatProperty(
        name="Normalized Roughness",
        default=0.0,
        min=0.0,
        max=1.0
    )

    pbraudio_low_frequency: FloatProperty(
        name="Low Frequency",
        default=5.0,
        min=0.0,
        soft_max=1000.0
    )

    pbraudio_high_frequency: FloatProperty(
        name="High Frequency",
        default=24000.0,
        soft_min=10000.0,
        max=96000.0
    )

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

    def draw_buttons(self, context, layout):
        # Get the active material from context or node property
        props = self

        layout.prop(props, "pbraudio_sound_speed", slider=True)
        layout.prop(props, "pbraudio_young_modulus", slider=True)
        layout.prop(props, "pbraudio_poisson_ratio", slider=True)
        layout.prop(props, "pbraudio_density", slider=True)
        layout.prop(props, "pbraudio_damping", slider=True)
        layout.prop(props, "pbraudio_friction", slider=True)
        layout.prop(props, "pbraudio_roughness", slider=True)
        layout.prop(props, "pbraudio_low_frequency", slider=True)
        layout.prop(props, "pbraudio_high_frequency", slider=True)

classes.append(AcousticShaderNode)

class AcousticMaterialPreviewNode(AcousticMaterialNode):
    """Acoustic material preview node for pbr synthesis"""
    bl_idname = 'AcousticMaterialPreviewNode'
    bl_label = "Acoustic Material Preview"

    def init(self, context):
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")

classes.append(AcousticMaterialPreviewNode)

class AcousticMaterialOutputNode(AcousticMaterialNode):
    """Acoustic material output node"""
    bl_idname = 'AcousticMaterialOutputNode'
    bl_label = "Material Output"

    def init(self, context):
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")

classes.append(AcousticMaterialOutputNode)
