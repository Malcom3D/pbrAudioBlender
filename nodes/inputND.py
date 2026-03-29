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
from bpy.types import Node, CurveMapping
from bpy.props import StringProperty, PointerProperty, FloatProperty

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
    bl_icon = 'IPO_EASE_IN_OUT'

    # Curve mapping property - this creates the widget
    frequency_curve: PointerProperty(
        name="Frequency Response",
        description="Frequency response curve",
        type=CurveMapping,
    )

    # Optional: preview frequency input for evaluation
    preview_frequency: FloatProperty(
        name="Preview Frequency",
        description="Frequency to preview response value (Hz)",
        default=1000.0,
        min=5.0,
        max=24000.0,
        step=10,
        precision=0,
        subtype='FREQUENCY'
    )

    def init(self, context):
        """Initialize the node and set up the curve mapping defaults"""
        # Set up the curve mapping
        curve = self.frequency_curve
        curve.tot_rect = (0.0, 0.0, 1.0, 1.0)  # Reset to normalized space

        # Create a new curve map with standard settings for audio frequency response
        curve.initialize()
        
        # Set curve to use logarithmic x-axis for frequency perception
        curve.clip_min_x = 0.0
        curve.clip_max_x = 1.0
        curve.clip_min_y = -30.0  # -30 dB
        curve.clip_max_y = 30.0   # +30 dB
        curve.use_clip = True
        
        # Add curve points for a flat response (0 dB)
        curve.curves[0].points.new(0.0, 0.0)    # 5 Hz at normalized 0
        curve.curves[0].points.new(1.0, 0.0)    # 24 kHz at normalized 1
        
        # Set interpolation to Bezier for smooth curves
        for point in curve.curves[0].points:
            point.handle_type = 'AUTO'
        
        # Update the curve mapping
        curve.update()

        # Create output sockets
        self.outputs.new('NodeSocketFloat', "Gain")
        self.outputs.new('NodeSocketFloat', "Preview Response")

    def draw_buttons(self, context, layout):
        """Draw the curve widget in the node interface"""
        col = layout.column(align=True)
        
        # Display the frequency response curve widget
        col.template_curve_mapping(
            self, "frequency_curve",
            type='NONE',  # No predefined type, we use custom ranges
            levels=False,
            brush=False,
            use_alpha=False
        )
        
        # Add frequency range labels
        row = col.row(align=True)
        row.label(text="5 Hz")
        row.label(text="1 kHz")
        row.label(text="24 kHz")
        
        # Add gain range label
        col.label(text=f"Range: -30 dB to +30 dB")
        
        # Preview section
        col.separator()
        col.prop(self, "preview_frequency")
        
        # Calculate and show preview value
        preview_gain = self.evaluate_at_frequency(self.preview_frequency)
        col.label(text=f"Response: {preview_gain:.2f} dB")
        
        # Display the preview response in the second output socket
        if "Preview Response" in self.outputs:
            self.outputs["Preview Response"].default_value = self._normalize_gain(preview_gain)

    def draw_buttons_ext(self, context, layout):
        """Extended UI in sidebar"""
        self.draw_buttons(context, layout)
        layout.separator()
        layout.label(text="Usage:")
        layout.label(text="• Link 'Gain' output to material")
        layout.label(text="• Gain = dB multiplier for frequency")
        layout.label(text="• 0 dB = no change, positive = boost")

    def evaluate_at_frequency(self, frequency_hz):
        """Evaluate curve response at given frequency in Hz"""
        if not self.frequency_curve:
            return 0.0
        
        # Convert frequency to normalized x-coordinate (log scale)
        # Map 5 Hz -> 0.0, 24,000 Hz -> 1.0
        import math
        f_min = 5.0
        f_max = 24000.0
        
        # Logarithmic mapping for perceived frequency
        log_f = math.log10(max(frequency_hz, f_min))
        log_min = math.log10(f_min)
        log_max = math.log10(f_max)
        
        # Normalized position
        x = (log_f - log_min) / (log_max - log_min)
        x = max(0.0, min(1.0, x))  # Clamp to [0, 1]
        
        # Evaluate curve at x
        try:
            # Get the first curve (RGB curve)
            curve_map = self.frequency_curve.curves[0]
            # Evaluate returns (y, y) but we need the y value
            value = curve_map.evaluate(curve_map, x)
            # The evaluate method returns a float value
            return value
        except Exception as e:
            print(f"Error evaluating curve: {e}")
            return 0.0

    def _normalize_gain(self, gain_db):
        """Convert dB gain to linear multiplier (0-2 range for UI)"""
        # Normalize -30..30 dB to 0..1 range
        # 0 dB = 0.5 normalized (no change)
        return (gain_db + 30.0) / 60.0

    def update(self):
        """Called when node properties change"""
        if self.frequency_curve:
            self.frequency_curve.update()
        
        # Update output socket values
        if "Preview Response" in self.outputs:
            preview_gain = self.evaluate_at_frequency(self.preview_frequency)
            self.outputs["Preview Response"].default_value = self._normalize_gain(preview_gain)
classes.append(AcousticMaterialFrequencyResponseNode)

class DispertionPatternGraph(AcousticMaterialNode):
    """Dispertion Pattern Graph node"""
    bl_idname = 'DispertionPatternGraph'
    bl_label = "Dispertion Pattern Graph"

    def init(self, context):
        pass

classes.append(DispertionPatternGraph)
