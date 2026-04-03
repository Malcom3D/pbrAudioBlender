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
from bpy.props import IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList
from bpy_extras.io_utils import ImportHelper

from .baseND import AcousticBaseNode

classes = []

class FrequencyResponseFilesNode(AcousticBaseNode):
    """Node to load frequency response data from a file (.frd or .cal)"""
    bl_idname = 'FrequencyResponseFilesNode'
    bl_label = 'Frequency Response Files'
    bl_icon = 'FILE_FOLDER'

    pbraudio_type: StringProperty(default='AcousticProperties')

    pbraudio_response_filepath: StringProperty(
        name="Response File",
        description="Select a frequency response file (.frd or .cal)",
        subtype='FILE_PATH',
        default="",
    )

    def init(self, context):
        self.outputs.new('AcousticValueNodeSocket', "Frequency Response Data")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pbraudio_response_filepath", text="Response File")
#        layout.operator("node.load_response_file", text="Load Response").node_name = self.name

#    def load_response(self, context):
#        # Optional: Implement custom loading/parsing logic here
#        pass

classes.append(FrequencyResponseFilesNode)

class FRDDataPoint(PropertyGroup):
    frequency: FloatProperty(
        name="Frequency (Hz)",
        description="Frequency in Hz",
        default=100.0,
        min=0.01
    )
    magnitude: FloatProperty(
        name="Magnitude",
        description="Magnitude (linear or dB based on context)",
        default=1.0,
        soft_min=0.0
    )
    phase: FloatProperty(
        name="Phase (degrees)",
        description="Phase in degrees",
        default=0.0
    )
classes.append(FRDDataPoint)

class FRDDATA_UL_Points(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "frequency", text="Freq")
        row.prop(item, "magnitude", text="Mag")
        row.prop(item, "phase", text="Phase")
classes.append(FRDDATA_UL_Points)

class FrequencyResponseChartNode(AcousticBaseNode):
    bl_idname = 'FrequencyResponseChartNode'
    bl_label = "Frequency Response Chart"
    bl_icon = 'GRAPH'

    pbraudio_type: StringProperty(default='AcousticProperties')

    # Collection of data points
    frd_points: CollectionProperty(type=FRDDataPoint)
    frd_points_index: bpy.props.IntProperty(name='Index', default=0)

    frd_id_file: bpy.props.IntProperty(name='frd_id_file', default=0)

    # File path or name for export
    pbraudio_response_filepath: StringProperty(
        name="FRD Filename",
        description="Filename to export the response data",
        default="frequency_response.frd",
        subtype='FILE_PATH'
    )

    # Whether to use phase or not
    has_phase: BoolProperty(
        name="Include Phase",
        description="Whether phase data is provided",
        default=True
    )

    def init(self, context):
        self.outputs.new('AcousticValueNodeSocket', "Frequency Response Data")
        self.frd_id_file = id(self)
        cache_path = bpy.context.scene.pbraudio.cache_path
        self.pbraudio_response_filepath = f"{cache_path}/{self.frd_id_file}.frd"

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.template_list("FRDDATA_UL_Points", "", self, "frd_points", self, "frd_points_index", rows=4)
        col = row.column(align=True)
        col.operator("node.add_frd_point", text="", icon='ADD')
        col.operator("node.remove_frd_point", text="", icon='REMOVE')
#        layout.prop(self, "pbraudio_response_filepath")
        layout.prop(self, "has_phase")
        layout.operator("node.export_frd_response", text="Export FRD")

    def socket_value_update(self, context)
        #layout.operator("node.export_frd_response", text="Export FRD")
        pass

classes.append(FrequencyResponseChartNode)
