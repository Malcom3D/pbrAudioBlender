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
        self.outputs.new('AcousticPropertiesNodeSocket', "AcousticProperties")
        self.inputs.new('AcousticMaterialNodeSocket', "absorption")
        self.inputs.new('AcousticMaterialNodeSocket', "refraction")
        self.inputs.new('AcousticMaterialNodeSocket', "reflection")
        self.inputs.new('AcousticMaterialNodeSocket', "scattering")

classes.append(AcousticPropertiesNode)

class AcousticShaderNode(AcousticMaterialNode):
    """Acoustic shader node"""
    bl_idname = 'AcousticShaderNode'
    bl_label = "Acoustic Shader"

    def init(self, context):
        self.outputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticProperties")

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
