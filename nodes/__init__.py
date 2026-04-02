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

from . import worldND, baseND, materialND, inputND, outputND, frequencyND, dispersionND, curve_plotterND

for mod in (worldND, baseND, materialND, inputND, outputND, frequencyND, dispersionND, curve_plotterND):
    classes += mod.classes

class WorldNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'AcousticWorldNodeTree'

world_node_categories = [
    WorldNodeCategory("WORLD_NODES", "World", items=[
        NodeItem("pbrAudioWorldOutputNode"),
        NodeItem("pbrAudioWorldMediumNode"),
        NodeItem("pbrAudioImpedenceNode"),
        NodeItem("pbrAudioDensityNode"),
        NodeItem("pbrAudioTemperatureNode"),
        NodeItem("pbrAudioEnvironmentNode"),
    ]),
]

class MaterialNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'AcousticMaterialNodeTree'

input_node_categories = [
    MaterialNodeCategory("INPUT_NODES", "Input", items=[
        NodeItem("AcousticPropertiesNode"),
        NodeItem("FrequencyResponseNode"),
#        NodeItem("DispersionPatternNode"),
    ]),
]

output_node_categories = [
    MaterialNodeCategory("OUTPUT_NODES", "Output", items=[
        NodeItem("AcousticMaterialOutputNode"),
        NodeItem("AcousticMaterialPreviewNode"),
        NodeItem("FrequencyResponseCurveNode"),
    ]),
]

material_node_categories = [
    MaterialNodeCategory("MATERIAL_NODES", "Material", items=[
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

    # Register the draw handler for curve nodes
    from .curve_plotterND import register_draw_handler
    register_draw_handler()

def unregister():
    unregister_node_categories("MATERIAL")
    unregister_node_categories("OUTPUT")
    unregister_node_categories("INPUT")
    unregister_node_categories("WORLD")
    for cls in reversed(classes):
        unregister_class(cls)

    # Remove draw handler
    if hasattr(bpy.types, 'SpaceNodeEditor'):
        # Note: In In practice, you'd need to store the handler reference
        # and remove it properly. This is a simplified version.
        pass
