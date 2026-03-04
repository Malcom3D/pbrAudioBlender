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
from bpy.props import StringProperty

classes = []

class AudioMaterialNode(Node):
    """Base class for all audio material nodes"""
    bl_idname = 'AudioMaterialNode'
    bl_label = "Audio Material Node"
    bl_icon = 'SOUND'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'AudioMaterialNodeTree'

classes.append(AudioMaterialNode)

class AudioInputNode(AudioMaterialNode):
    """Audio input node"""
    bl_idname = 'AudioInputNode'
    bl_label = "Audio Input"

    audio_file: StringProperty(
        name="Audio File",
        description="Path to audio file",
        subtype='FILE_PATH'
    )

    def init(self, context):
        self.outputs.new('AudioMaterialNodeSocket', "Audio Signal")

classes.append(AudioInputNode)

class AcousticPropertiesNode(AudioMaterialNode):
    """Acoustic properties node"""
    bl_idname = 'AcousticPropertiesNode'
    bl_label = "Acoustic Properties"

    def init(self, context):
        self.outputs.new('AcousticPropertiesNodeSocket', "AcousticProperties")
        self.inputs.new('AudioMaterialNodeSocket', "absorption")
        self.inputs.new('AudioMaterialNodeSocket', "refraction")
        self.inputs.new('AudioMaterialNodeSocket', "reflection")
        self.inputs.new('AudioMaterialNodeSocket', "scattering")

classes.append(AcousticPropertiesNode)

class AcousticShaderNode(AudioMaterialNode):
    """Acoustic shader node"""
    bl_idname = 'AcousticShaderNode'
    bl_label = "Acoustic Shader"

    def init(self, context):
        self.outputs.new('AudioMaterialNodeSocket', "AudioMaterial")
        self.inputs.new('AudioMaterialNodeSocket', "AcousticProperties")

    def draw_buttons(self, context, layout):
        object = context.object.pbraudio
        layout.prop(object, "sound_speed", slider=True)
        layout.prop(object, "young_modulus", slider=True)
        layout.prop(object, "poisson_ratio", slider=True)
        layout.prop(object, "density", slider=True)
        layout.prop(object, "damping", slider=True)
        layout.prop(object, "friction", slider=True)
        layout.prop(object, "roughness", slider=True)
        layout.prop(object, "low_frequency", slider=True)
        layout.prop(object, "high_frequency", slider=True)

classes.append(AcousticShaderNode)

class AudioMaterialPreviewNode(AudioMaterialNode):
    """Audio material preview node for pbr synthesis"""
    bl_idname = 'AudioMaterialPreviewNode'
    bl_label = "Audio Material Preview"

    def init(self, context):
        self.inputs.new('AudioMaterialNodeSocket', "AudioMaterial")

classes.append(AudioMaterialPreviewNode)

class AudioMaterialOutputNode(AudioMaterialNode):
    """Audio material output node"""
    bl_idname = 'AudioMaterialOutputNode'
    bl_label = "Material Output"

    def init(self, context):
        self.inputs.new('AudioMaterialNodeSocket', "AudioMaterial")

classes.append(AudioMaterialOutputNode)
