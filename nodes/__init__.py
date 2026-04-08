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
from bpy.utils import register_class, unregister_class
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories

classes = []

from . import worldND, baseND, materialND, propertyND, outputND, plotND, audioND, spatialND

for mod in (worldND, baseND, materialND, propertyND, outputND, plotND, audioND, spatialND):
    classes += mod.classes

class WorldAcousticNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
#        return context.space_data.tree_type == 'AcousticNodeTree' and bpy.data.node_groups[context.space_data.node_tree.name].pbraudio_type == 'WORLD'
        return context.space_data.tree_type == 'AcousticNodeTree' and context.scene.pbraudio.acoustic_shader_type == 'WORLD'

class ObjectAcousticNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
#        return context.space_data.tree_type == 'AcousticNodeTree' and bpy.data.node_groups[context.space_data.node_tree.name].pbraudio_type == 'OBJECT'
        return context.space_data.tree_type == 'AcousticNodeTree' and context.scene.pbraudio.acoustic_shader_type == 'OBJECT'

class SoundAcousticNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
#        return context.space_data.tree_type == 'AcousticNodeTree' and bpy.data.node_groups[context.space_data.node_tree.name].pbraudio_type == 'SOUND'
        return context.space_data.tree_type == 'AcousticNodeTree' and context.scene.pbraudio.acoustic_shader_type == 'SOUND'

world_node_categories = [
    WorldAcousticNodeCategory("WORLD_NODES", "World", items=[
        NodeItem("pbrAudioWorldOutputNode"),
        NodeItem("pbrAudioWorldShaderNode"),
        NodeItem("pbrAudioImpedenceNode"),
        NodeItem("pbrAudioDensityNode"),
        NodeItem("pbrAudioTemperatureNode"),
        NodeItem("pbrAudioEnvironmentNode"),
    ]),
]

property_node_categories = [
    ObjectAcousticNodeCategory("PROPERTY_NODE", "Property", items=[
        NodeItem("AcousticPropertiesNode"),
    ]),
]

input_node_categories = [
    ObjectAcousticNodeCategory("INPUT_NODES", "Input", items=[
        NodeItem("FrequencyResponseFilesNode"),
        NodeItem("FrequencyResponseChartNode"),
        NodeItem("SpatialFrequencyResponseNode"),
    ]),
]

output_node_categories = [
    ObjectAcousticNodeCategory("OUTPUT_NODES", "Output", items=[
        NodeItem("AcousticMaterialOutputNode"),
        NodeItem("AcousticMaterialPreviewNode"),
        NodeItem("ResponsePreviewNode"),
    ]),
]

material_node_categories = [
    ObjectAcousticNodeCategory("MATERIAL_NODES", "Material", items=[
        NodeItem("AcousticShaderNode"),
        NodeItem("AcrylicShaderNode"),
        NodeItem("AluminumShaderNode"),
        NodeItem("AsphaltShaderNode"),
        NodeItem("ConcreteShaderNode"),
        NodeItem("GlassShaderNode"),
        NodeItem("GypsumShaderNode"),
        NodeItem("IronShaderNode"),
        NodeItem("MarbleShaderNode"),
        NodeItem("TimberShaderNode"),
    ]),
]

def register():
    for cls in classes:
        register_class(cls)
    register_node_categories("WORLD", world_node_categories)
    register_node_categories("INPUT", input_node_categories)
    register_node_categories("OUTPUT", output_node_categories)
    register_node_categories("MATERIAL", material_node_categories)
    register_node_categories("PROPERTY", property_node_categories)

def unregister():
    unregister_node_categories("PROPERTY")
    unregister_node_categories("MATERIAL")
    unregister_node_categories("OUTPUT")
    unregister_node_categories("INPUT")
    unregister_node_categories("WORLD")
    for cls in reversed(classes):
        unregister_class(cls)
