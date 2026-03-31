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

"""
Simple FRD file parser for frequency response data
FRD format is typically a text file with frequency and magnitude pairs
"""
import numpy as np

def parse_frd_file(filepath):
    """
    Parse FRD file and return frequency and magnitude arrays
    
    Args:
        filepath: Path to FRD file
        
    Returns:
        tuple: (frequencies, magnitudes) as numpy arrays
    """
    frequencies = []
    magnitudes = []
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Try to parse two numbers (frequency and magnitude)
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        freq = float(parts[0])
                        mag = float(parts[1])
                        frequencies.append(freq)
                        magnitudes.append(mag)
                    except ValueError:
                        continue
        
        return np.array(frequencies), np.array(magnatures)
    
    except Exception as e:
        print(f"Error parsing FRD file {filepath}: {e}")
        return np.array([]), np.array([])

def validate_frd_data(frequencies, magnitudes):
    """
    Validate FRD data
    
    Args:
        frequencies: Array of frequencies
        magnitudes: Array of magnitudes
        
    Returns:
        bool: True if data is valid
    """
    if len(frequencies) == 0 or len(magnitudes) == 0:
        return False
    
    if len(frequencies) != len(magnitudes):
        return False
    
    # Check if frequencies are monotonic (usually they should be)
    if not np.all(np.diff(frequencies) > 0):
        print("Warning: Frequencies are not strictly increasing")
    
    return True

def resample_frd_data(frequencies, magnitudes, num_points=100):
    """
    Resample FRD data to specified number of points
    
    Args:
        frequencies: Original frequency array
        magnitudes: Original magnitude array
        num_points: Number of points for resampling
        
    Returns:
        tuple: (resampled_frequencies, resampled_magnitudes)
    """
    if len(frequencies) < 2:
        return frequencies, magnitudes
    
    # Create log-spaced frequencies for resampling
    log_freq_min = np.log10(frequencies[0])
    log_freq_max = np.log10(frequencies[-1])
    resampled_freq = np.logspace(log_freq_min, log_freq_max, num_points)
    
    # Interpolate magnitudes
    resampled_mag = np.interp(np.log10(resampled_freq), 
                             np.log10(frequencies), 
                             magnitudes)
    
    return resampled_freq, resampled_mag
