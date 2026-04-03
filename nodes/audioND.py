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
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, CollectionProperty
from bpy.types import PropertyGroup
from bpy_extras.io_utils import ImportHelper

from .baseND import AcousticBaseNode

classes = []

class FrequencyResponseFilesNode(AcousticBaseNode):
    """Node to load frequency response data from a file (.frd or .cal)"""
    bl_idname = 'FrequencyResponseFilesNode'
    bl_label = 'Frequency Response Files'
    bl_icon = 'FILE_FOLDER'

    pbraudio_type: StringProperty(default='AcousticProperties')

    pbraudio_respose_filepath: StringProperty(
        name="Response File",
        description="Select a frequency response file (.frd or .cal)",
        subtype='FILE_PATH',
        default="",
    )

    def init(self, context):
        self.outputs.new('AcousticValueNodeSocket', "Frequency Response", slider=False)

    def draw_buttons(self, context, layout):
        layout.prop(self, "pbraudio_respose_filepath", text="Response File")
#        layout.operator("node.load_response_file", text="Load Response").node_name = self.name

#    def load_response(self, context):
#        # Optional: Implement custom loading/parsing logic here
#        pass

classes.append(FrequencyResponseFilesNode)

class FrequencyResponseData(PropertyGroup):
    frequency: FloatProperty(name="Frequency (Hz)", default=1000.0)
    magnitude: FloatProperty(name="Magnitude", default=0.0)
    phase: FloatProperty(name="Phase (degrees)", default=0.0)
classes.append(FrequencyResponseData)

class FrequencyResponseChartNode(AcousticBaseNode):
    """Manual Frequency Response Data Input Node"""
    bl_idname = 'FrequencyResponseChartNode'
    bl_label = "Frequency Response Chart"
    bl_icon = 'LINE_DATA'

    pbraudio_type: StringProperty(default='AcousticProperties')

    # Store the data collection
    response_data: CollectionProperty(type=FrequencyResponseData)

    # Whether to include phase
    has_phase: BoolProperty(name="Has Phase Data", default=False)

    def init(self, context):
        self.outputs.new('AcousticValueNodeSocket', "Frequency Response Data")
        # Add a collection property for input data
        # (In UI, user will add items manually)

    def draw_buttons(self, context, layout):
        layout.prop(self, "has_phase")
        row = layout.row()
        row.operator("node.add_freq_response_data", text="Add Data Point")
        row.operator("node.clear_freq_response_data", text="Clear Data")

        # Display data points
        for idx, item in enumerate(self.response_data):
            box = layout.box()
            box.prop(item, "frequency")
            box.prop(item, "magnitude")
            if self.has_phase:
                box.prop(item, "phase")
classes.append(FrequencyResponseChartNode)
