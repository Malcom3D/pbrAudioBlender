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
from bpy.props import StringProperty, PointerProperty, IntProperty, FloatProperty, CollectionProperty

from .baseND import AcousticMaterialNode

from ..properties import materialPG

classes = []

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

class AcousticMaterialFrequencyResponseNode(AcousticMaterialNode):
    """Custom node for defining audio frequency response curves"""
    bl_idname = "AcousticMaterialFrequencyResponseNode"
    bl_label = "Frequency Response Curve"
    bl_icon = 'GRAPH'

    # Collection of user‑defined points
    points: CollectionProperty(type=materialPG.PBRAudioFreqPointProperties)
    # Index of the currently selected point in the UI list
    point_index: IntProperty(default=0)

    # Scaling factors for the generated curve
    x_scale: FloatProperty(
        name="X Scale",
        description="Scales the log10(frequency) coordinate",
        default=2.0,
        min=0.1,
        max=10.0
    )
    y_scale: FloatProperty(
        name="Y Scale",
        description="Scales the magnitude coordinate",
        default=0.05,
        min=0.01,
        max=1.0
    )

    # Optional X offset (moves the curve along X)
    x_offset: FloatProperty(
        name="X Offset",
        default=-5.0,
        description="Shift the curve left/right"
    )
    def init(self, context):
        """Add two example points when the node is first created"""
        pt1 = self.points.add()
        pt1.frequency = 100.0
        pt1.magnitude = -20.0
        pt2 = self.points.add()
        pt2.frequency = 1000.0
        pt2.magnitude = 0.0
        pt3 = self.points.add()
        pt3.frequency = 10000.0
        pt3.magnitude = -10.0

    def draw_buttons(self, context, layout):
        """UI inside the node"""
        # --- List of points ---
        row = layout.row()
        col = row.column()
        col.template_list(
            "UI_UL_list", "freq_points", self, "points",
            self, "point_index", rows=3
        )

        # Add / remove buttons
        col = row.column(align=True)
        col.operator("acoustic.point_add", icon='ADD', text="")
        col.operator("acoustic.point_remove", icon='REMOVE', text="")

        # --- Point properties (when a point is selected) ---
        if self.point_index < len(self.points):
            pt = self.points[self.point_index]
            box = layout.box()
            box.label(text="Selected Point", icon='DOT')
            box.prop(pt, "frequency")
            box.prop(pt, "magnitude")

        # --- Scaling and generation ---
        layout.separator()
        layout.prop(self, "x_scale")
        layout.prop(self, "y_scale")
        layout.prop(self, "x_offset")
        layout.separator()
        layout.operator("acoustic.generate_curve", text="Generate Curve", icon='OUTLINER_OB_CURVE')

    def draw_buttons_ext(self, context, layout):
        """Extra UI in the sidebar (N‑panel) – same as main UI"""
        self.draw_buttons(context, layout)

classes.append(AcousticMaterialFrequencyResponseNode)

class DispertionPatternGraph(AcousticMaterialNode):
    """Dispertion Pattern Graph node"""
    bl_idname = 'DispertionPatternGraph'
    bl_label = "Dispertion Pattern Graph"

    def init(self, context):
        pass

classes.append(DispertionPatternGraph)
