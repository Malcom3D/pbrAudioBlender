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
from bpy.types import Node, NodeTree
from bpy.props import PointerProperty

from .baseND import AcousticMaterialNode

classes = []

# -------------------------------------------------------------------
#  Custom Node Type
# -------------------------------------------------------------------
class AcousticMaterialFrequencyCurve(AcousticMaterialNode):
    """A custom node that displays an interactive frequency response curve."""
    bl_idname = "AcousticMaterialFrequencyCurve"
    bl_label = "Frequency Response Curve"
    bl_icon = 'IPO_EASE_IN_OUT'   # Curve icon
    bl_width_default = 250

    # Property to hold the CurveMapping data block
    freq_curve: PointerProperty(
        name="Frequency Curve",
        type=bpy.types.CurveMapping,
        description="Gain vs. Frequency response curve"
    )

    # ---------------------------------------------------------------
    #  Initialise the node and create a default curve
    # ---------------------------------------------------------------
    def init(self, context):
        # Create a new CurveMapping data block
        curve = self.freq_curve
        if curve is None:
            # This should not happen, but safety first
            self.freq_curve = bpy.data.curves.new(name="FreqCurve", type='CURVE')
            curve = self.freq_curve

        # Set up the mapping range: X = normalized frequency (0-1), Y = gain (0-1)
        curve.tone = 'CURVE'           # Standard curve type
        curve.clip_min_x = 0.0
        curve.clip_max_x = 1.0
        curve.clip_min_y = 0.0
        curve.clip_max_y = 1.0

        # Remove default points and create a flat line (0,0) to (1,1)
        curve.curves[0].points.clear()
        p1 = curve.curves[0].points.new(0.0, 0.0)
        p2 = curve.curves[0].points.new(1.0, 1.0)
        p1.handle_type = 'VECTOR'
        p2.handle_type = 'VECTOR'
        curve.update()

    # ---------------------------------------------------------------
    #  Draw the curve widget in the node
    # ---------------------------------------------------------------
    def draw_buttons(self, context, layout):
        if self.freq_curve:
            layout.template_curve_mapping(self, "freq_curve", type='NONE')
        else:
            layout.label(text="Error: No curve data")

    # ---------------------------------------------------------------
    #  Copy the node – duplicate the CurveMapping
    # ---------------------------------------------------------------
    def copy(self, node):
        if node.freq_curve:
            # Create a new curve data block with the same points
            new_curve = bpy.data.curves.new(name="FreqCurve", type='CURVE')
            new_curve.tone = node.freq_curve.tone
            new_curve.clip_min_x = node.freq_curve.clip_min_x
            new_curve.clip_max_x = node.freq_curve.clip_max_x
            new_curve.clip_min_y = node.freq_curve.clip_min_y
            new_curve.clip_max_y = node.freq_curve.clip_max_y

            # Copy all control points
            src_curve = node.freq_curve.curves[0]
            dst_curve = new_curve.curves[0]
            dst_curve.points.clear()
            for p in src_curve.points:
                new_p = dst_curve.points.new(p.location[0], p.location[1])
                new_p.handle_type = p.handle_type
            new_curve.update()

            self.freq_curve = new_curve

    # ---------------------------------------------------------------
    #  Free the node – clean up custom CurveMapping data
    # ---------------------------------------------------------------
    def free(self):
        if self.freq_curve and self.freq_curve.name not in bpy.data.curves:
            # Only remove if not used elsewhere
            bpy.data.curves.remove(self.freq_curve)

    # ---------------------------------------------------------------
    #  (Optional) Evaluate the curve at a given frequency (0-1)
    # ---------------------------------------------------------------
    def evaluate(self, x):
        """Returns the curve value at normalized x (0..1)."""
        if self.freq_curve:
            return self.freq_curve.evaluate(x)
        return 0.0
classes.append(AcousticMaterialFrequencyCurve)
