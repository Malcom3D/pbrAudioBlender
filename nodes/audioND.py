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
from ..utils import frd_io 

classes = []

class FrequencyResponseFilesNode(AcousticBaseNode):
    """Node to load frequency response data from a file (.frd or .cal)"""
    bl_idname = 'FrequencyResponseFilesNode'
    bl_label = 'Frequency Response Files'
    bl_icon = 'FILE_FOLDER'

    def validate_frd_file(self, context):
        # validate the data inside the file
        abs_frd_filepath = self.frd_filepath
        if not os.path.isabs(self.frd_filepath):
            abs_frd_filepath = bpy.path.abspath(self.frd_filepath)
        if not abs_frd_filepath == '' and frd_io.validate_frd_file(abs_frd_filepath):
            bpy.ops.report({'INFO'}, f"{self.frd_filepath} is a valid FRD file")
            self.pbraudio_response_filepath = self.frd_filepath
        else:
            bpy.ops.report({'ERROR'}, f"An unexpected error occurred while processing the file: {self.frd_filepath} is not a valid FRD file")
            self.frd_filepath = ''

    pbraudio_type: StringProperty(default='FrequencyResponse')

    frd_filepath: StringProperty(
        name="ResponseFile",
        description="Select a frequency response file (.frd or .cal)",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default='',
        update=validate_frd_file
    )

    pbraudio_response_filepath: StringProperty(
        name="ValidatedResponseFile",
        description="Validated frequency response file (.frd or .cal or .csv or .txt or text file)",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default=''
    )

    def init(self, context):
        self.outputs.new('AcousticValueNodeSocket', "Frequency Response Data")

    def draw_buttons(self, context, layout):
        layout.prop(self, "frd_filepath", text="Response File")

classes.append(FrequencyResponseFilesNode)

class FRDDataPoint(PropertyGroup):
    frequency: FloatProperty(
        name="Frequency (Hz)",
        description="Frequency in Hz",
        default=1000.0,
        min=0.01,
        max=96000
    )
    magnitude: FloatProperty(
        name="Magnitude",
        description="Magnitude (linear or dB based on context)",
        default=0.0
    )
    phase: FloatProperty(
        name="Phase (degrees)",
        description="Phase in degrees",
        default=0.0,
        soft_min=-180.0,
        soft_max=180.0
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

    def write_frd_file_id(self, context):
        bpy.ops.node.export_frd_response(node_tree=self.id_data.name, node_name=self.name, filepath=self.pbraudio_response_filepath)

    pbraudio_type: StringProperty(default='FrequencyResponse')

    # Collection of data points
    frd_points: CollectionProperty(type=FRDDataPoint)
    frd_points_index: bpy.props.IntProperty(
        name='Index',
        default=0,
        update=write_frd_file_id
    )

    frd_id_file: bpy.props.StringProperty(default='frd_id_file')

    # File path or name for export
    pbraudio_response_filepath: StringProperty(
        name="FRD Filename",
        description="Filename to export the response data",
        default="frequency_response.frd",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
    )

    # Whether to use phase or not
    has_phase: BoolProperty(
        name="Include Phase",
        description="Whether phase data is provided",
        default=True
    )

    def init(self, context):
        self.outputs.new('AcousticValueNodeSocket', "Frequency Response Data")
        self.frd_id_file = str(id(self))
        cache_path = bpy.context.scene.pbraudio.cache_path
        self.pbraudio_response_filepath = f"{cache_path}/{self.frd_id_file}.frd"

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.template_list("FRDDATA_UL_Points", "", self, "frd_points", self, "frd_points_index", rows=4)
        col = row.column(align=True)
        op = col.operator("node.add_frd_point", text="", icon='ADD')
        op.node_name = self.name
        op.node_tree = self.id_data.name
        op = col.operator("node.remove_frd_point", text="", icon='REMOVE')
        op.node_name = self.name
        op.node_tree = self.id_data.name
        layout.prop(self, "has_phase")
        op = layout.operator("node.export_frd_response", text="Export FRD")
        op.node_name = self.name
        op.node_tree = self.id_data.name

    def update(self):
        bpy.ops.node.export_frd_response(node_tree=self.id_data.name, node_name=self.name, filepath=self.pbraudio_response_filepath)

classes.append(FrequencyResponseChartNode)
