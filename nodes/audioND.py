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
from bpy_extras.io_utils import ImportHelper

# Add to your nodes list
# classes = []

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
        self.outputs.new('AcousticValueNodeSocket', "Frequency Response")

    def draw_buttons(self, context, layout):
        layout.prop(self, "pbraudio_respose_filepath", text="Response File")
        layout.operator("node.load_response_file", text="Load Response").node_name = self.name

    def load_response(self, context):
        # Optional: Implement custom loading/parsing logic here
        pass

classes.append(FrequencyResponseFilesNode)
