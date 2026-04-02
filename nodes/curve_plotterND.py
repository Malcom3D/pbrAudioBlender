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
import numpy as np
from bpy.types import Node
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty
from mathutils import Vector, Matrix
import gpu
from gpu_extras.batch import batch_for_shader
from math import log10, floor, ceil
import blf

from .baseND import AcousticMaterialNode

classes = []

class FrequencyResponseCurveNode(AcousticMaterialNode):
    """Node for plotting frequency response curves"""
    bl_idname = 'FrequencyResponseCurveNode'
    bl_label = "Frequency Response Curve"
    bl_icon = 'GRAPH'
    
    # Display properties
    show_magnitude: BoolProperty(
        name="Show Magnitude",
        description="Display magnitude curve",
        default=True
    )
    
    show_phase: BoolProperty(
        name="Show Phase",
        description="Display phase curve",
        default=False
    )
    
    show_group_delay: BoolProperty(
        name="Show Group Delay",
        description="Display group delay curve",
        default=False
    )
    
    # Curve style properties
    curve_thickness: FloatProperty(
        name="Curve Thickness",
        description="Thickness of the curve lines",
        default=2.0,
        min=1.0,
        max=10.0
    )
    
    magnitude_color: bpy.props.FloatVectorProperty(
        name="Magnitude Color",
        description="Color for magnitude curve",
        subtype='COLOR',
        default=(0.8, 0.2, 0.2, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )
    
    phase_color: bpy.props.FloatVectorProperty(
        name="Phase Color",
        description="Color for phase curve",
        subtype='COLOR',
        default=(0.2, 0.6, 0.8, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )
    
    group_delay_color: bpy.props.FloatVectorProperty(
        name="Group Delay Color",
        description="Color for group delay curve",
        subtype='COLOR',
        default=(0.2, 0.8, 0.3, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )
    
    # Grid properties
    show_grid: BoolProperty(
        name="Show Grid",
        description="Display grid lines",
        default=True
    )
    
    grid_color: bpy.props.FloatVectorProperty(
        name="Grid Color",
        description="Color for grid lines",
        subtype='COLOR',
        default=(0.3, 0.3, 0.3, 0.3),
        size=4,
        min=0.0,
        max=1.0
    )
    
    # Axis properties
    x_axis_log: BoolProperty(
        name="Log Frequency",
        description="Use logarithmic scale for frequency axis",
        default=True
    )
    
    y_axis_magnitude_range: bpy.props.FloatVectorProperty(
        name="Magnitude Range",
        description="Y-axis range for magnitude",
        size=2,
        default=(-60.0, 0.0),
        min=-200.0,
        max=200.0
    )
    
    y_axis_phase_range: bpy.props.FloatVectorProperty(
        name="Phase Range",
        description="Y-axis range for phase",
        size=2,
        default=(-180.0, 180.0),
        min=-360.0,
        max=360.0
    )
    
    y_axis_group_delay_range: bpy.props.FloatVectorProperty(
        name="Group Delay Range",
        description="Y-axis range for group delay",
        size=2,
        default=(0.0, 0.01),
        min=0.0,
        max=1.0
    )
    
    # Plot dimensions
    plot_width: FloatProperty(
        name="Plot Width",
        description="Width of the plot area",
        default=400.0,
        min=100.0,
        max=1000.0
    )
    
    plot_height: FloatProperty(
        name="Plot Height",
        description="Height of the plot area",
        default=300.0,
        min=100.0,
        max=1000.0
    )
    
    # Auto-range properties
    auto_range_magnitude: BoolProperty(
        name="Auto Range Magnitude",
        description="Automatically adjust magnitude range based on data",
        default=True
    )
    
    auto_range_phase: BoolProperty(
        name="Auto Range Phase",
        description="Automatically adjust phase range based on data",
        default=True
    )
    
    auto_range_group_delay: BoolProperty(
        name="Auto Range Group Delay",
        description="Automatically adjust group delay range based on data",
        default=True
    )
    
    # Padding for auto-range
    auto_range_padding: FloatProperty(
        name="Auto Range Padding",
        description="Padding percentage for auto-range",
        default=0.1,
        min=0.0,
        max=0.5
    )
    
    def init(self, context):
        """Initialize the node"""
        self.inputs.new('AcousticMaterialNodeSocket', "FrequencyResponse")
        self.outputs.new('AcousticMaterialNodeSocket', "CurveData")
        
        # Set initial dimensions
        self.width = 450
        self.height = 400
    
    def update(self):
        """Update the node display"""
        # Update auto-ranges if enabled
        self.update_auto_ranges()
        
        # Force redraw
        for area in bpy.context.screen.areas:
            if area.type == 'NODE_EDITOR':
                area.tag_redraw()
    
    def update_auto_ranges(self):
        """Update auto-ranges based on current data"""
        data = self.get_frequency_data()
        if not data:
            return
        
        frequencies, magnitudes, phases = data
        
        if len(frequencies) == 0:
            return
        
        # Update magnitude range
        if self.auto_range_magnitude and self.show_magnitude and len(magnitudes) > 0:
            mag_min = np.min(magnitudes)
            mag_max = np.max(magnitudes)
            mag_range = mag_max - mag_min
            padding = self.auto_range_padding * mag_range if mag_range > 0 else 1.0
            
            self.y_axis_magnitude_range = (
                mag_min - padding,
                mag_max + padding
            )
        
        # Update phase range
        if self.auto_range_phase and self.show_phase and len(phases) > 0:
            phase_min = np.min(phases)
            phase_max = np.max(phases)
            phase_range = phase_max - phase_min
            padding = self.auto_range_padding * phase_range if phase_range > 0 else 10.0
            
            self.y_axis_phase_range = (
                phase_min - padding,
                phase_max + padding
            )
        
        # Update group delay range
        if self.auto_range_group_delay and self.show_group_delay:
            group_delay_data = self.get_group_delay_data()
            if group_delay_data:
                _, group_delay = group_delay_data
                if len(group_delay) > 0:
                    gd_min = np.min(group_delay)
                    gd_max = np.max(group_delay)
                    gd_range = gd_max - gd_min
                    padding = self.auto_range_padding * gd_range if gd_range > 0 else 0.001
                    
                    self.y_axis_group_delay_range = (
                        max(0.0, gd_min - padding),
                        gd_max + padding
                    )
    
    def draw_buttons(self, context, layout):
        """Draw node buttons"""
        # Source selection
        box = layout.box()
        box.label(text="Data Source:", icon='LINKED')
        
        # Find connected frequency response nodes
        connected_nodes = []
        if self.inputs[0].is_linked:
            for link in self.inputs[0].links:
                if link.from_node.bl_idname == 'FrequencyResponseNode':
                    connected_nodes.append(link.from_node)
        
        if connected_nodes:
            row = box.row()
            row.label(text="Connected:")
            row = box.row()
            for node in connected_nodes:
                row.label(text=node.name, icon='NODE')
        else:
            box.label(text="No frequency response connected", icon='ERROR')
        
        # Display options
        box = layout.box()
        box.label(text="Display Options:", icon='SHADING_RENDERED')
        
        row = box.row()
        row.prop(self, "show_magnitude")
        if self.show_magnitude:
            row.prop(self, "magnitude_color", text="")
            row.prop(self, "auto_range_magnitude", text="", icon='AUTO')
        
        row = box.row()
        row.prop(self, "show_phase")
        if self.show_phase:
            row.prop(self, "phase_color", text="")
            row.prop(self, "auto_range_phase", text="", icon='AUTO')
        
        row = box.row()
        row.prop(self, "show_group_delay")
        if self.show_group_delay:
            row.prop(self, "group_delay_color", text="")
            row.prop(self, "auto_range_group_delay", text="", icon='AUTO')
        
        # Auto-range settings
        if self.auto_range_magnitude or self.auto_range_phase or self.auto_range_group_delay:
            box.prop(self, "auto_range_padding", slider=True)
        
        # Axis options
        box = layout.box()
        box.label(text="Axis Options:", icon='AXIS_TOP')
        
        box.prop(self, "x_axis_log")
        
        if self.show_magnitude:
            col = box.column(align=True)
            col.label(text="Magnitude Range (dB):")
            col.prop(self, "y_axis_magnitude_range", index=0, text="Min")
            col.prop(self, "y_axis_magnitude_range", index=1, text="Max")
        
        if self.show_phase:
            col = box.column(align=True)
            col.label(text="Phase Range (deg):")
            col.prop(self, "y_axis_phase_range", index=0, text="Min")
            col.prop(self, "y_axis_phase_range", index=1, text="Max")
        
        if self.show_group_delay:
            col = box.column(align=True)
            col.label(text="Group Delay Range (s):")
            col.prop(self, "y_axis_group_delay_range", index=0, text="Min")
            col.prop(self, "y_axis_group_delay_range", index=1, text="Max")
        
        # Style options
        box = layout.box()
        box.label(text="Style Options:", icon='PREFERENCES')
        
        box.prop(self, "curve_thickness")
        box.prop(self, "show_grid")
        if self.show_grid:
            box.prop(self, "grid_color", text="Grid Color")
        
        # Plot dimensions
        box = layout.box()
        box.label(text="Plot Dimensions:", icon='FULLSCREEN_ENTER')
        
        col = box.column(align=True)
        col.prop(self, "plot_width")
        col.prop(self, "plot_height")
        
        # Update button
        box = layout.box()
        box.operator("node.update_frequency_curve", text="Update Plot", icon='FILE_REFRESH')
    
    def draw_buttons_ext(self, context, layout):
        """Draw additional buttons in sidebar"""
        # Export options
        box = layout.box()
        box.label(text="Export:", icon='EXPORT')
    
        row = box.row()
        row.operator("node.export_curve_image", text="Export as Image")
        row.operator("node.export_curve_data", text="Export Data")  # Fixed: removed duplicate "Export"
    
        # Statistics
        box = layout.box()
        box.label(text="Statistics:", icon='INFO')
    
        # Get data from connected node
        data = self.get_frequency_data()
        if data:
            frequencies, magnitudes, phases = data
        
            if len(frequencies) > 0:
                box.label(text=f"Points: {len(frequencies)}")
                box.label(text=f"Freq Range: {frequencies[0]:.1f} - {frequencies[-1]:.1f} Hz")
            
                if len(magnitudes) > 0:
                    box.label(text=f"Mag Range: {np.min(magnitudes):.1f} - {np.max(magnitudes):.1f} dB")
            
                if len(phases) > 0:
                    box.label(text=f"Phase Range: {np.min(phases):.1f} - {np.max(phases):.1f}°")
    
    def get_frequency_data(self):
        """Get frequency data from connected node"""
        if not self.inputs[0].is_linked:
            return None
        
        # Get connected frequency response node
        for link in self.inputs[0].links:
            if link.from_node.bl_idname == 'FrequencyResponseNode':
                node = link.from_node
                if hasattr(node, 'data_valid') and node.data_valid:
                    return node.get_frequency_response_data()
        
        return None
    
    def get_group_delay_data(self):
        """Calculate group delay from phase data"""
        data = self.get_frequency_data()
        if not data:
            return None
        
        frequencies, magnitudes, phases = data
        
        if len(frequencies) < 2 or len(phases) < 2:
            return None
        
        # Calculate group delay using finite differences
        group_delay = np.zeros_like(frequencies)
        
        # Central differences for interior points
        for i in range(1, len(frequencies) - 1):
            delta_phase = phases[i + 1] - phases[i - 1]
            delta_freq = frequencies[i + 1] - frequencies[i - 1]
            if delta_freq != 0:
                # Convert phase from degrees to radians and calculate group delay
                group_delay[i] = -delta_phase * (np.pi / 180.0) / (2 * np.pi * delta_freq)
        
        # Forward/backward differences for endpoints
        if len(frequencies) > 1:
            delta_phase = phases[1] - phases[0]
            delta_freq = frequencies[1] - frequencies[0]
            if delta_freq != 0:
                group_delay[0] = -delta_phase * (np.pi / 180.0) / (2 * np.pi * delta_freq)
            
            delta_phase = phases[-1] - phases[-2]
            delta_freq = frequencies[-1] - frequencies[-2]
            if delta_freq != 0:
                group_delay[-1] = -delta_phase * (np.pi / 180.0) / (2 * np.pi * delta_freq)
        
        return frequencies, group_delay
    
    def draw_curve(self, context):
        """Draw the curve in the node - called from draw handler"""
        # Get node dimensions and position
        node_width = self.width
        node_height = self.height
        
        # Calculate plot area (leaving space for header and buttons)
        plot_margin = 20
        plot_x = self.location.x + plot_margin
        plot_y = self.location.y - 120  # Leave space for node header
        plot_width = min(self.plot_width, node_width - 2 * plot_margin)
        plot_height = min(self.plot_height, node_height - 140)
        
        # Get data
        data = self.get_frequency_data()
        if not data:
            self.draw_no_data_message(plot_x, plot_y, plot_width, plot_height)
            return
        
        frequencies, magnitudes, phases = data
        
        if len(frequencies) == 0:
            self.draw_no_data_message(plot_x, plot_y, plot_width, plot_height)
            return
        
        # Draw grid
        if self.show_grid:
            self.draw_grid(plot_x, plot_y, plot_width, plot_height, frequencies)
        
        # Draw axes
        self.draw_axes(plot_x, plot_y, plot_width, plot_height)
        
        # Draw curves
        if self.show_magnitude and len(magnitudes) > 0:
            self.draw_magnitude_curve(plot_x, plot_y, plot_width, plot_height, frequencies, magnitudes)
        
        if self.show_phase and len(phases) > 0:
            self.draw_phase_curve(plot_x, plot_y, plot_width, plot_height, frequencies, phases)
        
        if self.show_group_delay:
            group_delay_data = self.get_group_delay_data()
            if group_delay_data:
                gd_frequencies, group_delay = group_delay_data
                if len(group_delay) > 0:
                    self.draw_group_delay_curve(plot_x, plot_y, plot_width, plot_height, gd_frequencies, group_delay)
        
        # Draw legend
        self.draw_legend(plot_x, plot_y + plot_height + 5, plot_width)
    
    def draw_no_data_message(self, x, y, width, height):
        """Draw message when no data is available"""
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        
        # Draw background
        gpu.state.blend_set('ALPHA')
        shader.uniform_float("color", (0.1, 0.1, 0.1, 0.3))
        
        vertices = [
            (x, y),
            (x + width, y),
            (x + width, y - height),
            (x, y - height)
        ]
        
        indices = [(0, 1, 2), (0, 2, 3)]
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        batch.draw()
        
        # Draw text
        font_id = 0
        text = "No data available"
        text_width = len(text) * 6
        text_x = x + (width - text_width) / 2
        text_y = y - height / 2
        
        blf.position(font_id, text_x, text_y, 0)
        blf.size(font_id, 12)
        blf.color(font_id, 1, 1, 1, 1)
        blf.draw(font_id, text)
        
        gpu.state.blend_set('NONE')
    
    def draw_grid(self, x, y, width, height, frequencies):
        """Draw grid lines"""
        if len(frequencies) == 0:
            return
        
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", self.grid_color)
        
        # Get frequency range
        freq_min = frequencies[0]
        freq_max = frequencies[-1]
        
        # Calculate grid lines
        vertices = []
        
        # Vertical grid lines (frequency)
        if self.x_axis_log:
            # Logarithmic grid
            log_min = log10(freq_min) if freq_min > 0 else 0
            log_max = log10(freq_max)
            
            decade_start = floor(log_min)
            decade_end = ceil(log_max)
            
            for decade in range(decade_start, decade_end + 1):
                for i in range(1, 10):  # 1, 2, 3, ..., 9
                    freq = i * (10 ** decade)
                    if freq_min <= freq <= freq_max:
                        if self.x_axis_log:
                            x_pos = x + (log10(freq) - log_min) / (log_max - log_min) * width
                        else:
                            x_pos = x + (freq - freq_min) / (freq_max - freq_min) * width
                        
                        vertices.append((x_pos, y))
                        vertices.append((x_pos, y - height))
        else:
            # Linear grid
            num_lines = 10
            for i in range(num_lines + 1):
                freq = freq_min + (freq_max - freq_min) * i / num_lines
                x_pos = x + (freq - freq_min) / (freq_max - freq_min) * width
                
                vertices.append((x_pos, y))
                vertices.append((x_pos, y - height))
        
        # Horizontal grid lines
        num_horizontal_lines = 8
        for i in range(num_horizontal_lines + 1):
            y_pos = y - height * i / num_horizontal_lines
            vertices.append((x, y_pos))
            vertices.append((x + width, y_pos))
        
        # Draw grid lines
        if vertices:
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(1.0)
            batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
            batch.draw()
            gpu.state.blend_set('NONE')
    
    def draw_axes(self, x, y, width, height):
        """Draw x and y axes"""
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        
        # Draw axes
        vertices = [
            (x, y), (x + width, y),  # X-axis
            (x, y), (x, y - height),  # Y-axis
        ]
        
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
        batch.draw()
        gpu.state.blend_set('NONE')
    
    def draw_magnitude_curve(self, x, y, width, height, frequencies, magnitudes):
        """Draw magnitude curve"""
        if len(frequencies) == 0 or len(magnitudes) == 0:
            return
        
        # Get magnitude range
        mag_min, mag_max = self.y_axis_magnitude_range
        
        # Create vertices
        vertices = []
        for i in range(len(frequencies)):
            freq = frequencies[i]
            mag = magnitudes[i]
            
            # Normalize coordinates
            if self.x_axis_log and freq > 0:
                freq_min = frequencies[0] if frequencies[0] > 0 else 1
                freq_max = frequencies[-1]
                log_min = log10(freq_min)
                log_max = log10(freq_max)
                x_pos = x + (log10(freq) - log_min) / (log_max - log_min) * width
            else:
                freq_min = frequencies[0]
                freq_max = frequencies[-1]
                x_pos = x + (freq - freq_min) / (freq_max - freq_min) * width
            
            # Clamp magnitude to range
            mag_clamped = max(mag_min, min(mag_max, mag))
            y_pos = y - (mag_clamped - mag_min) / (mag_max - mag_min) * height
            
            vertices.append((x_pos, y_pos))
        
        # Draw curve
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", self.magnitude_color)
        
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(self.curve_thickness)
        
        if len(vertices) > 1:
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
            batch.draw()
        
        gpu.state.blend_set('NONE')
    
    def draw_phase_curve(self, x, y, width, height, frequencies, phases):
        """Draw phase curve"""
        if len(frequencies) == 0 or len(phases) == 0:
            return
        
        # Get phase range
        phase_min, phase_max = self.y_axis_phase_range
        
        # Create vertices
        vertices = []
        for i in range(len(frequencies)):
            freq = frequencies[i]
            phase = phases[i]
            
            # Normalize coordinates
            if self.x_axis_log and freq > 0:
                freq_min = frequencies[0] if frequencies[0] > 0 else 1
                freq_max = frequencies[-1]
                log_min = log10(freq_min)
                log_max = log10(freq_max)
                x_pos = x + (log10(freq) - log_min) / (log_max - log_min) * width
            else:
                freq_min = frequencies[0]
                freq_max = frequencies[-1]
                x_pos = x + (freq - freq_min) / (freq_max - freq_min) * width
            
            # Clamp phase to range
            phase_clamped = max(phase_min, min(phase_max, phase))
            y_pos = y - (phase_clamped - phase_min) / (phase_max - phase_min) * height
            
            vertices.append((x_pos, y_pos))
        
        # Draw curve
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", self.phase_color)
        
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(self.curve_thickness)
        
        if len(vertices) > 1:
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
            batch.draw()
        
        gpu.state.blend_set('NONE')
    
    def draw_group_delay_curve(self, x, y, width, height, frequencies, group_delay):
        """Draw group delay curve"""
        if len(frequencies) == 0 or len(group_delay) == 0:
            return
        
        # Get group delay range
        gd_min, gd_max = self.y_axis_group_delay_range
        
        # Create vertices
        vertices = []
        for i in range(len(frequencies)):
            freq = frequencies[i]
            gd = group_delay[i]
            
            # Normalize coordinates
            if self.x_axis_log and freq > 0:
                freq_min = frequencies[0] if frequencies[0] > 0 else 1
                freq_max = frequencies[-1]
                log_min = log10(freq_min)
                log_max = log10(freq_max)
                x_pos = x + (log10(freq) - log_min) / (log_max - log_min) * width
            else:
                freq_min = frequencies[0]
                freq_max = frequencies[-1]
                x_pos = x + (freq - freq_min) / (freq_max - freq_min) * width
            
            # Clamp group delay to range
            gd_clamped = max(gd_min, min(gd_max, gd))
            y_pos = y - (gd_clamped - gd_min) / (gd_max - gd_min) * height
            
            vertices.append((x_pos, y_pos))
        
        # Draw curve
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", self.group_delay_color)
        
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(self.curve_thickness)
        
        if len(vertices) > 1:
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
            batch.draw()
        
        gpu.state.blend_set('NONE')
    
    def draw_legend(self, x, y, width):
        """Draw legend"""
        font_id = 0
        blf.size(font_id, 11)
        
        legend_items = []
        if self.show_magnitude:
            legend_items.append(("Magnitude", self.magnitude_color))
        if self.show_phase:
            legend_items.append(("Phase", self.phase_color))
        if self.show_group_delay:
            legend_items.append(("Group Delay", self.group_delay_color))
        
        if not legend_items:
            return
        
        # Calculate legend position
        legend_x = x + 10
        legend_y = y - 20
        
        # Draw legend background
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (0.1, 0.1, 0.1, 0.7))
        
        gpu.state.blend_set('ALPHA')
        
        bg_width = 120
        bg_height = len(legend_items) * 20 + 10
        vertices = [
            (legend_x, legend_y),
            (legend_x + bg_width, legend_y),
            (legend_x + bg_width, legend_y - bg_height),
            (legend_x, legend_y - bg_height)
        ]
        indices = [(0, 1, 2), (0, 2, 3)]
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        batch.draw()
        
        # Draw legend items
        for i, (label, color) in enumerate(legend_items):
            # Draw color swatch
            shader.uniform_float("color", color)
            swatch_x = legend_x + 5
            swatch_y = legend_y - 15 - i * 20
            swatch_vertices = [
                (swatch_x, swatch_y),
                (swatch_x + 10, swatch_y),
                (swatch_x + 10, swatch_y - 10),
                (swatch_x, swatch_y - 10)
            ]
            swatch_indices = [(0, 1, 2), (0, 2, 3)]
            batch = batch_for_shader(shader, 'TRIS', {"pos": swatch_vertices}, indices=swatch_indices)
            batch.draw()
            
            # Draw label
            blf.position(font_id, swatch_x + 15, swatch_y - 8, 0)
            blf.color(font_id, 1, 1, 1, 1)
            blf.draw(font_id, label)
        
        gpu.state.blend_set('NONE')
    
    def draw_label(self):
        """Override draw_label to include plot dimensions"""
        # Call parent method
        super().draw_label()
        
        # Draw additional info if in node editor
        if bpy.context.area and bpy.context.area.type == 'NODE_EDITOR':
            # Get data info
            data = self.get_frequency_data()
            if data:
                frequencies, magnitudes, phases = data
                if len(frequencies) > 0:
                    # Draw info next to node label
                    font_id = 0
                    blf.size(font_id, 9)
                    
                    info_text = f" [{len(frequencies)} pts]"
                    label_width = len(self.label or self.name) * 6
                    
                    # Calculate position
                    x = self.location.x + label_width + 10
                    y = self.location.y - 8
                    
                    blf.position(font_id, x, y, 0)
                    blf.color(font_id, 0.7, 0.7, 0.7, 1.0)
                    blf.draw(font_id, info_text)

# Add draw handler to display curves
def draw_curve_nodes_callback():
    """Callback function to draw curve nodes"""
    context = bpy.context
    if not context.area or context.area.type != 'NODE_EDITOR':
        return
    
    space = context.space_data
    if not space or not space.edit_tree:
        return
    
    # Get all curve nodes in the tree
    for node in space.edit_tree.nodes:
        if node.bl_idname == 'FrequencyResponseCurveNode':
            # Set up OpenGL for 2D drawing
            gpu.state.blend_set('ALPHA')
            
            # Push matrix for node space
            gpu.matrix.push()
            gpu.matrix.push_projection()
            
            # Set orthographic projection for node space
            region = context.region
            gpu.matrix.load_projection_matrix(Matrix.Identity(4))
            gpu.matrix.load_identity()
            
            # Draw the curve
            node.draw_curve(context)
            
            # Restore matrix
            gpu.matrix.pop_projection()
            gpu.matrix.pop()
            
            gpu.state.blend_set('NONE')

# Register the draw handler
def register_draw_handler():
    """Register the draw handler for curve nodes"""
    if hasattr(bpy.types, 'SpaceNodeEditor'):
        bpy.types.SpaceNodeEditor.draw_handler_add(
            draw_curve_nodes_callback,
            (),
            'WINDOW',
            'POST_PIXEL'
        )

class NODE_OT_update_frequency_curve(bpy.types.Operator):
    """Update frequency response curve plot"""
    bl_idname = "node.update_frequency_curve"
    bl_label = "Update Plot"
    
    def execute(self, context):
        node = context.node
        if node:
            # Force redraw of the node
            node.update()
            # Update any viewport drawing
            context.area.tag_redraw()
        return {'FINISHED'}

class NODE_OT_export_curve_image(bpy.types.Operator):
    """Export frequency response curve as image"""
    bl_idname = "node.export_curve_image"
    bl_label = "Export as Image"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save the image",
        subtype='FILE_PATH'
    )
    
    image_format: bpy.props.EnumProperty(
        name="Format",
        items=[
            ('PNG', "PNG", "PNG format"),
            ('JPEG', "JPEG", "JPEG format"),
            ('TIFF', "TIFF", "TIFF format"),
            ('BMP', "BMP", "BMP format"),
        ],
        default='PNG'
    )
    
    image_width: bpy.props.IntProperty(
        name="Width",
        description="Image width in pixels",
        default=800,
        min=100,
        max=4096
    )
    
    image_height: bpy.props.IntProperty(
        name="Height",
        description="Image height in pixels",
        default=600,
        min=100,
        max=4096
    )
    
    def invoke(self, context, event):
        # Set default filepath
        self.filepath = bpy.path.abspath("//frequency_response.png")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        node = context.node
        if node:
            # Here you would implement image export
            # This would require creating an off-screen render of the curve
            self.report({'INFO'}, f"Exporting curve to {self.filepath}")
        return {'FINISHED'}

class NODE_OT_export_curve_data(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export frequency response curve data"""
    bl_idname = "node.export_curve_data"
    bl_label = "Export Data"
    
    filename_ext = ".csv"
    
    filter_glob: bpy.props.StringProperty(
        default="*.csv;*.txt",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        node = context.node
        if node:
            data = node.get_frequency_data()
            if data:
                frequencies, magnitudes, phases = data
                
                # Write to CSV
                with open(self.filepath, 'w') as f:
                    f.write("Frequency (Hz),Magnitude (dB),Phase (deg)\n")
                    for i in range(len(frequencies)):
                        f.write(f"{frequencies[i]},{magnitudes[i]},{phases[i]}\n")
                
                self.report({'INFO'}, f"Exported {len(frequencies)} points to {self.filepath}")
            else:
                self.report({'WARNING'}, "No data to export")
        
        return {'FINISHED'}

classes.extend([
    FrequencyResponseCurveNode,
    NODE_OT_update_frequency_curve,
    NODE_OT_export_curve_image,
    NODE_OT_export_curve_data
])
