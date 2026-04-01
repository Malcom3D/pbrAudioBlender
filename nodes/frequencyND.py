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
import os
import numpy as np
from bpy.types import Node
from bpy.props import StringProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty
from bpy_extras.io_utils import ImportHelper

from .baseND import AcousticMaterialNode
from ..utils.frd_parser import parse_frd_file, validate_frd_data, resample_frd_data

classes = []

class NODE_OT_load_frd_file(bpy.types.Operator, ImportHelper):
    """Load FRD frequency response file"""
    bl_idname = "node.load_frd_file"
    bl_label = "Load FRD File"
    
    filter_glob: StringProperty(
        default="*.frd;*.txt;*.csv",
        options={'HIDDEN'}
    )

    tree_name: StringProperty(
        default="",
    )
    
    node_name: StringProperty(
        default="",
    )
    
    def execute(self, context):
        if self.tree_name and self.node_name:
            node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
            node.pbraudio_frd_filepath = self.filepath
            # Extract filename without extension
            filename = os.path.basename(self.filepath)
            node.pbraudio_frd_filename = os.path.splitext(filename)[0]
            
            # Parse the FRD file immediately after loading
            node.parse_frd_data()
            
        return {'FINISHED'}

class FrequencyResponseNode(AcousticMaterialNode):
    """Node for loading and managing frequency response data from FRD files"""
    bl_idname = 'FrequencyResponseNode'
    bl_label = "Frequency Response"
    bl_icon = 'GRAPH'
    
    # File properties
    pbraudio_frd_filepath: StringProperty(
        name="FRD File",
        description="Path to FRD frequency response file",
        subtype='FILE_PATH',
        default="",
        update=lambda self, context: self.parse_frd_data()
    )
    
    pbraudio_frd_filename: StringProperty(
        name="Filename",
        description="Name of the FRD file",
        default=""
    )
    
    # Frequency range properties
    frequency_min: FloatProperty(
        name="Min Frequency",
        description="Minimum frequency in Hz",
        default=20.0,
        min=0.0,
        soft_max=20000.0,
        update=lambda self, context: self.update_frequency_range()
    )
    
    frequency_max: FloatProperty(
        name="Max Frequency",
        description="Maximum frequency in Hz",
        default=20000.0,
        min=0.0,
        soft_max=96000.0,
        update=lambda self, context: self.update_frequency_range()
    )
    
    # Magnitude properties
    magnitude_min: FloatProperty(
        name="Min Magnitude",
        description="Minimum magnitude in dB",
        default=-60.0,
        soft_min=-120.0,
        soft_max=0.0,
        update=lambda self, context: self.update_magnitude_range()
    )
    
    magnitude_max: FloatProperty(
        name="Max Magnitude",
        description="Maximum magnitude in dB",
        default=0.0,
        soft_min=-120.0,
        soft_max=20.0,
        update=lambda self, context: self.update_magnitude_range()
    )
    
    # Phase properties
    phase_min: FloatProperty(
        name="Min Phase",
        description="Minimum phase in degrees",
        default=-180.0,
        soft_min=-360.0,
        soft_max=0.0,
        update=lambda self, context: self.update_phase_range()
    )
    
    phase_max: FloatProperty(
        name="Max Phase",
        description="Maximum phase in degrees",
        default=180.0,
        soft_min=0.0,
        soft_max=360.0,
        update=lambda self, context: self.update_phase_range()
    )
    
    # FRD data storage (not saved with blend file)
    parsed_frequencies: bpy.props.FloatVectorProperty(
        name="Frequencies",
        description="Parsed frequency data",
        size=32,
        default=[0.0] * 32
    )
    
    parsed_magnitudes: bpy.props.FloatVectorProperty(
        name="Magnitudes",
        description="Parsed magnitude data",
        size=32,
        default=[0.0] * 32
    )
    
    parsed_phases: bpy.props.FloatVectorProperty(
        name="Phases",
        description="Parsed phase data",
        size=32,
        default=[0.0] * 32
    )
    
    parsed_num_points: bpy.props.IntProperty(
        name="Number of Points",
        description="Number of valid data points",
        default=0
    )
    
    # Filtered data (based on frequency range)
    parsed_filtered_frequencies: bpy.props.FloatVectorProperty(
        name="Filtered Frequencies",
        description="Filtered frequency data",
        size=32,
        default=[0.0] * 32
    )
    
    parsed_filtered_magnitudes: bpy.props.FloatVectorProperty(
        name="Filtered Magnitudes",
        description="Filtered magnitude data",
        size=32,
        default=[0.0] * 32
    )
    
    parsed_filtered_phases: bpy.props.FloatVectorProperty(
        name="Filtered Phases",
        description="Filtered phase data",
        size=32,
        default=[0.0] * 32
    )
    
    parsed_filtered_num_points: bpy.props.IntProperty(
        name="Filtered Number of Points",
        description="Number of filtered data points",
        default=0
    )
    
    # Display properties
    show_frequency_range: bpy.props.BoolProperty(
        name="Show Frequency Range",
        description="Display frequency range controls",
        default=False
    )
    
    show_magnitude_range: bpy.props.BoolProperty(
        name="Show Magnitude Range",
        description="Display magnitude range controls",
        default=False
    )
    
    show_phase_range: bpy.props.BoolProperty(
        name="Show Phase Range",
        description="Display phase range controls",
        default=False
    )
    
    show_raw_data: bpy.props.BoolProperty(
        name="Show Raw Data",
        description="Display raw FRD data information",
        default=False
    )
    
    # Data format properties
    data_format: EnumProperty(
        name="Data Format",
        description="Format of the FRD data",
        items=[
            ('MAG_ONLY', "Magnitude Only", "File contains only magnitude data"),
            ('MAG_PHASE', "Magnitude + Phase", "File contains magnitude and phase data"),
            ('REAL_IMAG', "Real + Imaginary", "File contains real and imaginary parts"),
        ],
        default='MAG_ONLY',
        update=lambda self, context: self.parse_frd_data()
    )
    
    # Curve visualization properties
    curve_resolution: IntProperty(
        name="Curve Resolution",
        description="Number of points for curve visualization",
        default=100,
        min=10,
        max=1000,
        update=lambda self, context: self.resample_data()
    )
    
    # Data validation flag
    data_valid: bpy.props.BoolProperty(
        name="Data Valid",
        description="Indicates if FRD data is valid",
        default=False
    )
    
    # Phase unwrapping
    unwrap_phase: bpy.props.BoolProperty(
        name="Unwrap Phase",
        description="Unwrap phase to avoid 360-degree jumps",
        default=True,
        update=lambda self, context: self.process_phase_data()
    )
    
    def init(self, context):
        """Initialize the node"""
        self.outputs.new('AcousticMaterialNodeSocket', "FrequencyResponse")
        
    def parse_frd_data(self):
        """Parse FRD file and store the data"""
        if not self.pbraudio_frd_filepath or not os.path.exists(self.pbraudio_frd_filepath):
            self.data_valid = False
            self.parsed_num_points = 0
            return
        
        try:
            # Parse the FRD file based on selected format
            if self.data_format == 'MAG_ONLY':
                frequencies, magnitudes = parse_frd_file(self.pbraudio_frd_filepath, has_phase=False)
                phases = np.zeros_like(magnitudes)
            elif self.data_format == 'MAG_PHASE':
                frequencies, magnitudes, phases = parse_frd_file(self.pbraudio_frd_filepath, has_phase=True)
            elif self.data_format == 'REAL_IMAG':
                frequencies, real_parts, imag_parts = parse_frd_file(self.pbraudio_frd_filepathpath, has_phase=False, has_imaginary=True)
                # Convert real/imaginary to magnitude/phase
                magnitudes = 20 * np.log10(np.sqrt(real_parts**2 + imag_parts**2))
                phases = np.degrees(np.arctan2(imag_parts, real_parts))
            
            # Validate the data
            if not validate_frd_data(frequencies, magnitudes, phases if 'phases' in locals() else None):
                print(f"Invalid FRD data in {self.pbraudio_frd_filepath}")
                self.data_valid = False
                self.parsed_num_points = 0
                return
            
            # Store the raw data
            num_points = min(len(frequencies), 32)  # Limit to array size
            self.parsed_num_points = num_points
            
            # Copy data to FloatVectorProperties
            for i in range(num_points):
                self.parsed_frequencies[i] = float(frequencies[i])
                self.parsed_magnitudes[i] = float(magnitudes[i])
                self.parsed_phases[i] = float(phases[i])
            
            # Clear remaining slots
            for i in range(num_points, 32):
                self.parsed_frequencies[i] = 0.0
                self.parsed_magnitudes[i] = 0.0
                self.parsed_phases[i] = 0.0
            
            # Update frequency range based on actual data
            if num_points > 0:
                self.frequency_min = float(np.min(frequencies[:num_points]))
                self.frequency_max = float(np.max(frequencies[:num_points]))
                
                # Update magnitude range
                mag_min = float(np.min(magnitudes[:num_points]))
                mag_max = float(np.max(magnitudes[:num_points]))
                
                # Add some padding to magnitude range
                mag_range = mag_max - mag_min
                self.magnitude_min = mag_min - 0.1 * mag_range
                self.magnitude_max = mag_max + 0.1 * mag_range
                
                # Update phase range
                phase_min = float(np.min(phases[:num_points]))
                phase_max = float(np.max(phases[:num_points]))
                
                # Add some padding to phase range
                phase_range = phase_max - phase_min
                self.phase_min = phase_min - 0.1 * phase_range
                self.phase_max = phase_max + 0.1 * phase_range
            
            self.data_valid = True
            print(f"Successfully parsed FRD file: {self.pbraudio_frd_filename}, {num_points} points")
            
            # Process phase data (unwrap if needed)
            self.process_phase_data()
            
            # Apply frequency filtering
            self.update_frequency_range()
            
        except Exception as e:
            print(f"Error parsing FRD file {self.pbraudio_frd_filepath}: {e}")
            self.data_valid = False
            self.parsed_num_points = 0
    
    def process_phase_data(self):
        """Process phase data (unwrap if needed)"""
        if not self.data_valid or self.parsed_num_points == 0:
            return
        
        # Get numpy arrays from stored data
        frequencies = np.array([self.parsed_frequencies[i] for i in range(self.parsed_num_points)])
        phases = np.array([self.parsed_phases[i] for i in range(self.parsed_num_points)])
        
        # Unwrap phase if requested
        if self.unwrap_phase:
            phases = np.unwrap(phases, period=360)
        
        # Store processed phases
        for i in range(self.parsed_num_points):
            self.parsed_phases[i] = float(phases[i])
        
        # Update filtered data if it exists
        if self.parsed_filtered_num_points > 0:
            self.update_frequency_range()
    
    def update_frequency_range(self):
        """Filter data based on frequency range"""
        if not self.data_valid or self.parsed_num_points == 0:
            return
        
        # Get numpy arrays from stored data
        frequencies = np.array([self.parsed_frequencies[i] for i in range(self.parsed_num_points)])
        magnitudes = np.array([self.parsed_magnitudes[i] for i in range(self.parsed_num_points)])
        phases = np.array([self.parsed_phases[i] for i in range(self.parsed_num_points)])
        
        # Apply frequency filter
        mask = (frequencies >= self.frequency_min) & (frequencies <= self.frequency_max)
        filtered_freq = frequencies[mask]
        filtered_mag = magnitudes[mask]
        filtered_phase = phases[mask]
        
        # Store filtered data
        num_filtered = min(len(filtered_freq), 32)
        self.parsed_filtered_num_points = num_filtered
        
        for i in range(num_filtered):
            self.parsed_filtered_frequencies[i] = float(filtered_freq[i])
            self.parsed_filtered_magnitudes[i] = float(filtered_mag[i])
            self.parsed_filtered_phases[i] = float(filtered_phase[i])
        
        # Clear remaining slots
        for i in range(num_filtered, 32):
            self.parsed_filtered_frequencies[i] = 0.0
            self.parsed_filtered_magnitudes[i] = 0.0
            self.parsed_filtered_phases[i] = 0.0
        
        # Resample if needed
        self.resample_data()
    
    def update_magnitude_range(self):
        """Update magnitude display range (doesn't filter data, just affects display)"""
        pass
    
    def update_phase_range(self):
        """Update phase display range (doesn't filter data, just affects display)"""
        pass
    
    def resample_data(self):
        """Resample data to curve_resolution points"""
        if not self.data_valid or self.parsed_filtered_num_points < 2:
            return
        
        # Get filtered data
        frequencies = np.array([self.parsed_filtered_frequencies[i] for i in range(self.parsed_filtered_num_points)])
        magnitudes = np.array([self.parsed_filtered_magnitudes[i] for i in range(self.parsed_filtered_num_points)])
        phases = np.array([self.parsed_filtered_phases[i] for i in range(self.parsed_filtered_num_points)])
        
        # Sort by frequency (just in case)
        sort_idx = np.argsort(frequencies)
        frequencies = frequencies[sort_idx]
        magnitudes = magnitudes[sort_idx]
        phases = phases[sort_idx]
        
        # Resample
        resampled_freq, resampled_mag, resampled_phase = resample_frd_data(
            frequencies, magnitudes, phases, self.curve_resolution
        )
        
        # Store resampled data
        num_resampled = min(len(resampled_freq), 32)
        
        for i in range(num_resampled):
            self.parsed_filtered_frequencies[i] = float(resampled_freq[i])
            self.parsed_filtered_magnitudes[i] = float(resampled_mag[i])
            self.parsed_filtered_phases[i] = float(resampled_phase[i])
        
        # Update count
        self.parsed_filtered_num_points = num_resampled
        
        # Clear remaining slots
        for i in range(num_resampled, 32):
            self.parsed_filtered_frequencies[i] = 0.0
            self.parsed_filtered_magnitudes[i] = 0.0
            self.parsed_filtered_phases[i] = 0.0
    
    def get_frequency_response_data(self):
        """Get the current frequency response data as numpy arrays"""
        if not self.data_valid or self.parsed_filtered_num_points == 0:
            return np.array([]), np.array([]), np.array([])
        
        frequencies = np.array([self.parsed_filtered_frequencies[i] for i in range(self.parsed_filtered_num_points)])
        magnitudes = np.array([self.parsed_filtered_magnitudes[i] for i in range(self.parsed_filtered_num_points)])
        phases = np.array([self.parsed_filtered_phases[i] for i in range(self.parsed_filtered_num_points)])
        
        return frequencies, magnitudes, phases
    
    def get_complex_response(self):
        """Get frequency response as complex numbers"""
        frequencies, magnitudes, phases = self.get_frequency_response_data()
        
        if len(frequencies) == 0:
            return np.array([]), np.array([])
        
        # Convert magnitude from dB to linear scale
        linear_magnitudes = 10 ** (magnitudes / 20.0)
        
        # Convert phase from degrees to radians
        phases_rad = np.radians(phases)
        
        # Create complex response
        complex_response = linear_magnitudes * np.exp(1j * phases_rad)
        
        return frequencies, complex_response
    
    def draw_buttons(self, context, layout):
        """Draw node buttons"""
        # File selection
        row = layout.row()
        row.prop(self, "pbraudio_frd_filename", text="")
        op = row.operator("node.load_frd_file", text="", icon='FILE_FOLDER')
        op.node_name = self.name
        op.tree_name = self.id_data.name
        
        # Data format selection
        layout.prop(self, "data_format")
        
        # Data validation indicator
        if self.pbraudio_frd_filepath:
            if self.data_valid:
                layout.label(text="✓ Data loaded successfully", icon='CHECKMARK')
            else:
                layout.label(text="✗ Invalid or no data", icon='ERROR')
        
        if self.pbraudio_frd_filepath and os.path.exists(self.pbraudio_frd_filepath):
            # Raw data info
            row = layout.row(align=True)
            row.prop(self, "show_raw_data", icon='TRIA_DOWN' if self.show_raw_data else 'TRIA_RIGHT', icon_only=True, emboss=False)
            row.label(text="Raw Data Info")
            
            if self.show_raw_data:
                box = layout.box()
                
                if self.data_valid:
                    box.label(text=f"Total points: {self.parsed_num_points}")
                    if self.parsed_num_points > 0:
                        # Show first and last frequency
                        first_freq = self.parsed_frequencies[0]
                        last_freq = self.parsed_frequencies[self.parsed_num_points - 1]
                        box.label(text=f"Frequency range: {first_freq:.1f} - {last_freq:.1f} Hz")
                        
                        # Show first and last magnitude
                        first_mag = self.parsed_magnitudes[0]
                        last_mag = self.parsed_magnitudes[self.parsed_num_points - 1]
                        box.label(text=f"Magnitude range: {first_mag:.1f} - {last_mag:.1f} dB")
                        
                        # Show first and last phase
                        first_phase = self.parsed_phases[0]
                        last_phase = self.parsed_phases[self.parsed_num_points - 1]
                        box.label(text=f"Phase range: {first_phase:.1f} - {last_phase:.1f}°")
                else:
                    box.label(text="No valid data", icon='ERROR')
        
        # Frequency range
        row = layout.row(align=True)
        row.prop(self, "show_frequency_range", icon='TRIA_DOWN' if self.show_frequency_range else 'TRIA_RIGHT', icon_only=True, emboss=False)
        row.label(text="Frequency Range")
        
        if self.show_frequency_range:
            col = layout.column(align=True)
            col.prop(self, "frequency_min", slider=True)
            col.prop(self, "frequency_max", slider=True)
            
            # Show filtered points count
            if self.data_valid:
                col.label(text=f"Filtered points: {self.parsed_filtered_num_points}")
        
        # Magnitude range
        row = layout.row(align=True)
        row.prop(self, "show_magnitude_range", icon='TRIA_DOWN' if self.show_magnitude_range else 'TRIA_RIGHT', icon_only=True, emboss=False)
        row.label(text="Magnitude Range")
        
        if self.show_magnitude_range:
            col = layout.column(align=True)
            col.prop(self, "magnitude_min", slider=True)
            col.prop(self, "magnitude_max", slider=True)
        
        # Phase range
        row = layout.row(align=True)
        row.prop(self, "show_phase_range", icon='TRIA_DOWN' if self.show_phase_range else 'TRIA_RIGHT', icon_only=True, emboss=False)
        row.label(text="Phase Range")
        
        if self.show_phase_range:
            col = layout.column(align=True)
            col.prop(self, "phase_min", slider=True)
            col.prop(self, "phase_max", slider=True)
            col.prop(self, "unwrap_phase")
        
        # Curve settings
        layout.prop(self, "curve_resolution")
        
        # Preview and plot buttons
        if self.data_valid:
            row = layout.row(align=True)
            row.operator("node.preview_frequency_response", text="Preview", icon='SHADING_RENDERED')
            row.operator("node.create_curve_plot", text="Plot", icon='GRAPH')

    def draw_buttons_ext(self, context, layout):
        """Draw additional buttons in sidebar"""
        layout.prop(self, "pbraudio_frd_filepath")
        
        # Advanced settings
        box = layout.box()
        box.label(text="Advanced Settings:", icon='SETTINGS')
        box.prop(self, "curve_resolution")
        box.prop(self, "unwrap_phase")
        
        # Data statistics
        if self.data_valid:
            box.label(text="Data Statistics:", icon='INFO')
            box.label(text=f"Raw points: {self.parsed_num_points}")
            box.label(text=f"Filtered points: {self.parsed_filtered_num_points}")
            
            if self.parsed_filtered_num_points > 0:
                # Calculate some statistics
                freqs, mags, phases = self.get_frequency_response_data()
                box.label(text=f"Min magnitude: {np.min(mags):.2f} dB")
                box.label(text=f"Max magnitude: {np.max(mags):.2f} dB")
                box.label(text=f"Mean magnitude: {np.mean(mags):.2f} dB")
                box.label(text=f"Min phase: {np.min(phases):.2f}°")
                box.label(text=f"Max phase: {np.max(phases):.2f}°")
                box.label(text=f"Mean phase: {np.mean(phases):.2f}°")
    
    def update(self):
        """Update node output when properties change"""
        if self.data_valid and self.parsed_filtered_num_points > 0:
            # Get the current data
            frequencies, magnitudes, phases = self.get_frequency_response_data()
            
            # Calculate some representative values
            if len(magnitudes) > 0:
                # Convert dB to linear scale for averaging
                linear_mags = 10 ** (magnitudes / 20.0)
                avg_linear = np.mean(linear_mags)
                avg_db = 20 * np.log10(avg_linear) if avg_linear > 0 else -120
                
                # Average phase
                avg_phase = np.mean(phases)
                
                # Store values
                self['average_magnitude'] = avg_db
                self['average_phase'] = avg_phase
    
    def copy(self, node):
        """Copy node data"""
        self.pbraudio_frd_filepath = node.pbraudio_frd_filepath
        self.pbraudio_frd_filename = node.pbraudio_frd_filename
        self.data_format = node.data_format
        self.unwrap_phase = node.unwrap_phase
        
        # Re-parse the file
        if self.pbraudio_frd_filepath and os.path.exists(self.pbraudio_frd_filepath):
            self.parse_frd_data()
    
    def free(self):
        """Clean up when node is removed"""
        # Clear any cached data
        self.parsed_num_points = 0
        self.parsed_filtered_num_points = 0
        self.data_valid = False

class NODE_OT_preview_frequency_response(bpy.types.Operator):
    """Preview frequency response curve"""
    bl_idname = "node.preview_frequency_response"
    bl_label = "Preview Frequency Response"
    
    def execute(self, context):
        node = context.node
        if node and node.data_valid:
            # Get the frequency response data
            frequencies, magnitudes, phases = node.get_frequency_response_data()
            
            if len(frequencies) > 0:
                # Create a simple text preview
                preview_text = f"Frequency Response Preview:\n"
                preview_text += f"Points: {len(frequencies)}\n"
                preview_text += f"Frequency range: {frequencies[0]:.1f} - {frequencies[-1]:.1f} Hz"
                preview_text += f"Magnitude range: {np.min(magnitudes):.1f} - {np.max(magnitudes):.1f} dB"
                preview_text += f"Phase range: {np.min(phases):.1f} - {np.max(phases):.1f}°\n"
                
                # Show first few points
                preview_text += "\nFirst 5 points:\n"
                for i in range(min(5, len(frequencies))):
                    preview_text += f"  {frequencies[i]:.1f} Hz: {magnitudes[i]:.1f} dB, {phases[i]:.1f}°\n"
                
                self.report({'INFO'}, preview_text)
                print(preview_text)
            else:
                self.report({'WARNING'}, "No valid data to preview")
        else:
            self.report({'WARNING'}, "No FRD file loaded or data invalid")
        
        return {'FINISHED'}

class NODE_OT_create_curve_plot(bpy.types.Operator):
    """Create a curve plot node for this frequency response"""
    bl_idname = "node.create_curve_plot"
    bl_label = "Create Curve Plot"
    
    def execute(self, context):
        node = context.node
        if node and node.data_valid:
            # Get the node tree
            tree = context.space_data.edit_tree
            
            # Create curve plot node
            curve_node = tree.nodes.new('FrequencyResponseCurveNode')
            curve_node.location = (node.location.x + 400, node.location.y)
            curve_node.name = f"{node.name}_Curve"
            
            # Connect the nodes
            tree.links.new(node.outputs[0], curve_node.inputs[0])
            
            # Set curve node properties based on frequency response data
            frequencies, magnitudes, phases = node.get_frequency_response_data()
            if len(frequencies) > 0:
                # Set magnitude range with some padding
                mag_min = np.min(magnitudes)
                mag_max = np.max(magnitudes)
                mag_range = mag_max - mag_min
                curve_node.y_axis_magnitude_range = (
                    mag_min - 0.1 * mag_range,
                    mag_max + 0.1 * mag_range
                )
                
                # Set phase range with some padding
                phase_min = np.min(phases)
                phase_max = np.max(phases)
                phase_range = phase_max - phase_min
                curve_node.y_axis_phase_range = (
                    phase_min - 0.1 * phase_range,
                    phase_max + 0.1 * phase_range
                )
            
            self.report({'INFO'}, f"Created curve plot node: {curve_node.name}")
        else:
            self.report({'WARNING'}, "No valid frequency response data")
        
        return {'FINISHED'}

classes.extend([
    NODE_OT_load_frd_file,
    FrequencyResponseNode,
    NODE_OT_preview_frequency_response
    NODE_OT_create_curve_plot
])
