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
            node.frd_filepath = self.filepath
            # Extract filename without extension
            filename = os.path.basename(self.filepath)
            self.node.frd_filename = os.path.splitext(filename)[0]
            
            # Parse the FRD file immediately after loading
            self.node.parse_frd_data()
            
        return {'FINISHED'}

class FrequencyResponseNode(AcousticMaterialNode):
    """Node for loading and managing frequency response data from FRD files"""
    bl_idname = 'FrequencyResponseNode'
    bl_label = "Frequency Response"
    bl_icon = 'GRAPH'
    
    # File properties
    frd_filepath: StringProperty(
        name="FRD File",
        description="Path to FRD frequency response file",
        subtype='FILE_PATH',
        default="",
        update=lambda self, context: self.parse_frd_data()
    )
    
    frd_filename: StringProperty(
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
    
    show_raw_data: bpy.props.BoolProperty(
        name="Show Raw Data",
        description="Display raw FRD data information",
        default=False
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
    
    def init(self, context):
        """Initialize the node"""
        self.outputs.new('AcousticMaterialNodeSocket', "FrequencyResponse")
        
    def parse_frd_data(self):
        """Parse FRD file and store the data"""
        if not self.frd_filepath or not os.path.exists(self.frd_filepath):
            self.data_valid = False
            self.parsed_num_points = 0
            return
        
        try:
            # Parse the FRD file
            frequencies, magnitudes = parse_frd_file(self.frd_filepath)
            
            # Validate the data
            if not validate_frd_data(frequencies, magnitudes):
                print(f"Invalid FRD data in {self.frd_filepath}")
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
            
            # Clear remaining slots
            for i in range(num_points, 32):
                self.parsed_frequencies[i] = 0.0
                self.parsed_magnitudes[i] = 0.0
            
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
            
            self.data_valid = True
            print(f"Successfully parsed FRD file: {self.frd_filename}, {num_points} points")
            
            # Apply frequency filtering
            self.update_frequency_range()
            
        except Exception as e:
            print(f"Error parsing FRD file {self.frd_filepath}: {e}")
            self.data_valid = False
            self.parsed_num_points = 0
    
    def update_frequency_range(self):
        """Filter data based on frequency range"""
        if not self.data_valid or self.parsed_num_points == 0:
            return
        
        # Get numpy arrays from stored data
        frequencies = np.array([self.parsed_frequencies[i] for i in range(self.parsed_num_points)])
        magnitudes = np.array([self.parsed_magnitudes[i] for i in range(self.parsed_num_points)])
        
        # Apply frequency filter
        mask = (frequencies >= self.frequency_min) & (frequencies <= self.frequency_max)
        filtered_freq = frequencies[mask]
        filtered_mag = magnitudes[mask]
        
        # Store filtered data
        num_filtered = min(len(filtered_freq), 32)
        self.parsed_filtered_num_points = num_filtered
        
        for i in range(num_filtered):
            self.parsed_filtered_frequencies[i] = float(filtered_freq[i])
            self.parsed_filtered_magnitudes[i] = float(filtered_mag[i])
        
        # Clear remaining slots
        for i in range(num_filtered, 32):
            self.parsed_filtered_frequencies[i] = 0.0
            self.parsed_filtered_magnitudes[i] = 0.0
        
        # Resample if needed
        self.resample_data()
    
    def update_magnitude_range(self):
        """Update magnitude display range (doesn't filter data, just affects display)"""
        # This is called when magnitude_min/max changes
        # We don't filter data based on magnitude, just update display
        pass
    
    def resample_data(self):
        """Resample data to curve_resolution points"""
        if not self.data_valid or self.parsed_filtered_num_points < 2:
            return
        
        # Get filtered data
        frequencies = np.array([self.parsed_filtered_frequencies[i] for i in range(self.parsed_filtered_num_points)])
        magnitudes = np.array([self.parsed_filtered_magnitudes[i] for i in range(self.parsed_filtered_num_points)])
        
        # Sort by frequency (just in case)
        sort_idx = np.argsort(frequencies)
        frequencies = frequencies[sort_idx]
        magnitudes = magnitudes[sort_idx]
        
        # Resample
        resampled_freq, resampled_mag = resample_frd_data(frequencies, magnitudes, self.curve_resolution)
        
        # Store resampled data (could be stored in another property if needed)
        # For now, we'll just update the filtered data with resampled version
        num_resampled = min(len(resampled_freq), 32)
        
        for i in range(num_resampled):
            self.parsed_filtered_frequencies[i] = float(resampled_freq[i])
            self.parsed_filtered_magnitudes[i] = float(resampled_mag[i])
        
        # Update count
        self.parsed_filtered_num_points = num_resampled
        
        # Clear remaining slots
        for i in range(num_resampled, 32):
            self.parsed_filtered_frequencies[i] = 0.0
            self.parsed_filtered_magnitudes[i] = 0.0
    
    def get_frequency_response_data(self):
        """Get the current frequency response data as numpy arrays"""
        if not self.data_valid or self.parsed_filtered_num_points == 0:
            return np.array([]), np.array([])
        
        frequencies = np.array([self.parsed_filtered_frequencies[i] for i in range(self.parsed_filtered_num_points)])
        magnitudes = np.array([self.parsed_filtered_magnitudes[i] for i in range(self.parsed_filtered_num_points)])
        
        return frequencies, magnitudes
    
    def draw_buttons(self, context, layout):
        """Draw node buttons"""
        # File selection
        row = layout.row()
        row.prop(self, "frd_filename", text="")
        op = row.operator("node.load_frd_file", text="", icon='FILE_FOLDER')
        op.node_name = self.name
        op.tree_name = self.id_data.name
        
        # Data validation indicator
        if self.frd_filepath:
            if self.data_valid:
                layout.label(text="✓ Data loaded successfully", icon='CHECKMARK')
            else:
                layout.label(text="✗ Invalid or no data", icon='ERROR')
        
        if self.frd_filepath and os.path.exists(self.frd_filepath):
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
        
        # Curve settings
        layout.prop(self, "curve_resolution")
        
        # Preview button
        if self.data_valid:
            layout.operator("node.preview_frequency_response", text="Preview Response", icon='SHADING_RENDERED')
    
    def draw_buttons_ext(self, context, layout):
        """Draw additional buttons in sidebar"""
        layout.prop(self, "frd_filepath")
        
        # Advanced settings
        box = layout.box()
        box.label(text="Advanced Settings:", icon='SETTINGS')
        box.prop(self, "curve_resolution")
        
        # Data statistics
        if self.data_valid:
            box.label(text="Data Statistics:", icon='INFO')
            box.label(text=f"Raw points: {self.parsed_num_points}")
            box.label(text=f"Filtered points: {self.parsed_filtered_num_points}")
            
            if self.parsed_filtered_num_points > 0:
                # Calculate some statistics
                freqs, mags = self.get_frequency_response_data()
                box.label(text=f"Min magnitude: {np.min(mags):.2f} dB")
                box.label(text=f"Max magnitude: {np.max(mags):.2f} dB")
                box.label(text=f"Mean magnitude: {np.mean(mags):.2f} dB")
        
        # Import/Export options
        row = box.row()
        row.operator("node.export_frequency_response", text="Export")
        row.operator("node.import_frequency_response", text="Import")
    
    def update(self):
        """Update node output when properties change"""
        # This method is called when the node needs to update its output
        # We've already parsed the data when the file was loaded or properties changed
        
        # If we have valid data, we could set some output value here
        # For example, we could calculate an average magnitude or other metric
        if self.data_valid and self.parsed_filtered_num_points > 0:
            # Get the current data
            frequencies, magnitudes = self.get_frequency_response_data()
            
            # Calculate some representative value
            # For example, average magnitude in dB (converted to linear scale)
            if len(magnitudes) > 0:
                # Convert dB to linear scale for averaging
                linear_mags = 10 ** (magnitudes / 20.0)
                avg_linear = np.mean(linear_mags)
                avg_db = 20 * np.log10(avg_linear) if avg_linear > 0 else -120
                
                # You could set this as an output value if your socket supports it
                # For now, we'll just store it
                self['average_magnitude'] = avg_db
    
    def copy(self, node):
        """Copy node data"""
        self.frd_filepath = node.frd_filepath
        self.frd_filename = node.frd_filename
        # Note: The _frequencies and _magnitudes arrays won't be copied
        # automatically, so we need to re-parse the file
        if self.frd_filepath and os.path.exists(self.frd_filepath):
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
            frequencies, magnitudes = node.get_frequency_response_data()
            
            if len(frequencies) > 0:
                # Create a simple text preview
                preview_text = f"Frequency Response Preview:\n"
                preview_text += f"Points: {len(frequencies)}\n"
                preview_text += f"Frequency range: {frequencies[0]:.1f} - {frequencies[-1]:.1f} Hz"
                preview_text += f"Magnitude range: {np.min(magnitudes):.1f} - {np.max(magnitudes):.1f} dB"
                
                # Show first few points
                preview_text += "\nFirst 5 points:\n"
                for i in range(min(5, len(frequencies))):
                    preview_text += f"  {frequencies[i]:.1f} Hz: {magnitudes[i]:.1f} dB"
                
                self.report({'INFO'}, preview_text)
                
                # In a real implementation, you might:
                # 1. Open a new window with a plot

                # 2. Draw the curve in the node editor
                # 3. Create a curve object in the 3D view
                
                # For now, just show in the info area
                print(preview_text)
            else:
                self.report({'WARNING'}, "No valid data to preview")
        else:
            self.report({'WARNING'}, "No FRD file loaded or data invalid")
        
        return {'FINISHED'}

# Note: You'll need to add these operators to your classes list
classes.extend([
    NODE_OT_load_frd_file,
    FrequencyResponseNode,
    NODE_OT_preview_frequency_response
])
