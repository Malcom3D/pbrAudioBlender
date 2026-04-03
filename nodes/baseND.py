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

class ThreeDfrequencyNode(Node):
    """Base class only for sources and outputs nodes"""
    bl_idname = 'ThreeDfrequencyNode'
    bl_label = "3D Frequency Response Node"
    bl_icon = 'IPO_EASE_IN_OUT'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AcousticMaterialNodeTree' and (bpy.context.active_object.type == 'EMPTY' or bpy.context.active_object.type == 'CAMERA') and (hasattr(bpy.context.active_object.pbraudio, 'output_type') or hasattr(bpy.context.active_object.pbraudio, 'source_type'))

classes.append(ThreeDfrequencyNode)

class AcousticWorldNode(Node):
    """Base class for all acoustic world nodes"""
    bl_idname = 'AcousticWorldNode'
    bl_label = "Acoustic World Node"
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AcousticWorldNodeTree'

classes.append(AcousticWorldNode)

class AcousticMaterialNode(Node):
    """Base class for all acoustic material nodes"""
    bl_idname = 'AcousticMaterialNode'
    bl_label = "Acoustic Material Node"
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AcousticMaterialNodeTree'

classes.append(AcousticMaterialNode)

class AcousticBaseNode(Node):
    """Base class for all acoustic world nodes"""
    bl_idname = 'AcousticBaseNode'
    bl_label = "Acoustic Base Node for Material and World NodeTree"
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AcousticWorldNodeTree' or ntree.bl_idname == 'AcousticMaterialNodeTree'

classes.append(AcousticBaseNode)

class DefaultAcousticShaderNode(AcousticMaterialNode):
    """Default acoustic shader node"""
    bl_idname = 'DefaultAcousticShaderNode'
    bl_label = "DefaultAcousticShader"

    pbraudio_type: StringProperty(default='AcousticShader')

    """Acoustic Shader properties"""
    pbraudio_sound_speed: FloatProperty(
        name="Sound Speed in m/s",
        default=1000.0,
        soft_min=0.0,
        soft_max=20000.0,
        precision=5,
    )

    pbraudio_young_modulus: FloatProperty(
        name="Young modulus in GPa",
        default=0.005,
        min=0.0,
        soft_max=1500.0,
        precision=5
    )

    pbraudio_poisson_ratio: FloatProperty(
        name="Poisson Ratio",
        default=0.46,
        min=-1.0,
        max=0.5,
        precision=5
    )

    pbraudio_density: FloatProperty(
        name="Density in kg/m³",
        default=800.0,
        min=0.0,
        soft_max=25000.0,
        precision=5
    )

    pbraudio_damping: FloatProperty(
        name="Rayleigh Damping in %",
        default=5,
        min=0.0,
        max=100,
        precision=5
    )

    pbraudio_friction: FloatProperty(
        name="Friction",
        default=0.5,
        min=0.0,
        soft_max=1.0,
        precision=5
    )

    pbraudio_roughness: FloatProperty(
        name="Normalized Roughness",
        default=0.4,
        min=0.0,
        max=1.0,
        precision=5
    )

    pbraudio_low_frequency: FloatProperty(
        name="Low Frequency",
        default=5.0,
        min=0.0,
        soft_max=1000.0,
        precision=5
    )

    pbraudio_high_frequency: FloatProperty(
        name="High Frequency",
        default=24000.0,
        soft_min=1000.0,
        max=96000.0,
        precision=5
    )

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

    def draw_buttons(self, context, layout):
        # Get the active material from context or node property
        layout.prop(self, "pbraudio_sound_speed", slider=True)
        layout.prop(self, "pbraudio_young_modulus", slider=True)
        layout.prop(self, "pbraudio_poisson_ratio", slider=True)
        layout.prop(self, "pbraudio_density", slider=True)
        layout.prop(self, "pbraudio_damping", slider=True)
        layout.prop(self, "pbraudio_friction", slider=True)
        layout.prop(self, "pbraudio_roughness", slider=True)
        layout.prop(self, "pbraudio_low_frequency", slider=True)
        layout.prop(self, "pbraudio_high_frequency", slider=True)

classes.append(DefaultAcousticShaderNode)
