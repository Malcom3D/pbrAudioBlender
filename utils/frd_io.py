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
FRD file parser for frequency response data with magnitude and phase support
FRD format is typically a text file with frequency, magnitude, and optionally phase
"""
import numpy as np

def parse_frd_file(filepath, has_phase=False, has_imaginary=False):
    """
    Parse FRD file and return frequency, magnitude, and phase arrays
    
    Args:
        filepath: Path to FRD file
        has_phase: If True, expects frequency, magnitude, phase columns
        has_imaginary: If True, expects frequency, real, imaginary columns
        
    Returns:
        tuple: (frequencies, magnitudes, phases) as numpy arrays
                or (frequencies, magnitudes) if has_phase=False and has_imaginary=False
                or (frequencies, real_parts, imag_parts) if has_imaginary=True
    """
    frequencies = []
    magnitudes = []
    phases = []
    real_parts = []
    imag_parts = []
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Try to parse numbers
                parts = line.split()
                
                if has_imaginary:
                    # Expecting frequency, real, imaginary
                    if len(parts) >= 3:
                        try:
                            freq = float(parts[0])
                            real = float(parts[1])
                            imag = float(parts[2])
                            frequencies.append(freq)
                            real_parts.append(real)
                            imag_parts.append(imag)
                        except ValueError:
                            continue
                elif has_phase:
                    # Expecting frequency, magnitude, phase
                    if len(parts) >= 3:
                        try:
                            freq = float(parts[0])
                            mag = float(parts[1])
                            phase = float(parts[2])
                            frequencies.append(freq)
                            magnitudes.append(mag)
                            phases.append(phase)
                        except ValueError:
                            continue
                else:
                    # Expecting frequency, magnitude only
                    if len(parts) >= 2:
                        try:
                            freq = float(parts[0])
                            mag = float(parts[1])
                            frequencies.append(freq)
                            magnitudes.append(mag)
                        except ValueError:
                            continue
        
        if has_imaginary:
            return np.array(frequencies), np.array(real_parts), np.array(imag_parts)
        elif has_phase:
            return np.array(frequencies), np.array(magnitudes), np.array(phases)
        else:
            return np.array(frequencies), np.array(magnitudes)
    
    except Exception as e:
        print(f"Error parsing FRD file {filepath}: {e}")
        if has_imaginary:
            return np.array([]), np.array([]), np.array([])
        elif has_phase:
            return np.array([]), np.array([]), np.array([])
        else:
            return np.array([]), np.array([])

def validate_frd_file(filepath):
    return self.validate_frd_data(self.parse_frd_file(filepath))

def validate_frd_data(frequencies, magnitudes, phases=None):
    """
    Validate FRD data
    
    Args:
        frequencies: Array of frequencies
        magnitudes: Array of magnitudes
        phases: Array of phases (optional)
        
    Returns:
        bool: True if data is valid
    """
    if len(frequencies) == 0 or len(magnitudes) == 0:
        return False
    
    if len(frequencies) != len(magnitudes):
        return False
    
    if phases is not None and len(phases) != len(frequencies):
        return False
    
    # Check if frequencies are monotonic (usually they should be)
    if not np.all(np.diff(frequencies) > 0):
        print("Warning: Frequencies are not strictly increasing")
    
    return True

def resample_frd_data(frequencies, magnitudes, phases=None, num_points=100):
    """
    Resample FRD data to specified number of points
    
    Args:
        frequencies: Original frequency array
        magnitudes: Original magnitude array
        phases: Original phase array (optional)
        num_points: Number of points for resampling
        
    Returns:
        tuple: (resampled_frequencies, resampled_magnitudes[, resampled_phases])
    """
    if len(frequencies) < 2:
        if phases is not None:
            return frequencies, magnitudes, phases
        else:
            return frequencies, magnitudes
    
    # Create log-spaced frequencies for resampling
    log_freq_min = np.log10(frequencies[0])
    log_freq_max = np.log10(frequencies[-1])
    resampled_freq = np.logspace(log_freq_min, log_freq_max, num_points)
    
    # Interpolate magnitudes
    resampled_mag = np.interp(np.log10(resampled_freq), 
                             np.log10(frequencies), 
                             magnitudes)
    
    if phases is not None:
        # For phase interpolation, we need to handle phase wrapping
        # First unwrap the phase
        unwrapped_phases = np.unwrap(phases, period=360)
        
        # Interpolate unwrapped phases
        resampled_phase_unwrapped = np.interp(np.log10(resampled_freq),
                                            np.log10(frequencies),
                                            unwrapped_phases)
        
        # Wrap back to -180 to 180 range
        resampled_phase = (resampled_phase_unwrapped + 180) % 360 - 180
        
        return resampled_freq, resampled_mag, resampled_phase
    else:
        return resampled_freq, resampled_mag

def magnitude_phase_to_complex(magnitudes_db, phases_deg):
    """
    Convert magnitude (dB) and phase (degrees) to complex numbers
    
    Args:
        magnitudes_db: Magnitude in dB
        phases_deg: Phase in degrees
        
    Returns:
        numpy.array: Complex frequency response
    """
    # Convert dB to linear magnitude
    linear_magnitudes = 10 ** (magnitudes_db / 20.0)
    
    # Convert degrees to radians
    phases_rad = np.radians(phases_deg)
    
    # Create complex response
    complex_response = linear_magnitudes * np.exp(1j * phases_rad)
    
    return complex_response

def complex_to_magnitude_phase(complex_response):
    """
    Convert complex numbers to magnitude (dB) and phase (degrees)
    
    Args:
        complex_response: Complex frequency response
        
    Returns:
        tuple: (magnitudes_db, phases_deg)
    """
    # Calculate magnitude in linear scale
    linear_magnitudes = np.abs(complex_response)
    
    # Convert to dB
    magnitudes_db = 20 * np.log10(linear_magnitudes)
    
    # Calculate phase in radians, then convert to degrees
    phases_rad = np.angle(complex_response)
    phases_deg = np.degrees(phases_rad)
    
    return magnitudes_db, phases_deg

def calculate_group_delay(frequencies, phases_deg):
    """
    Calculate group delay from phase data
    
    Args:
        frequencies: Frequency array in Hz
        phases_deg: Phase array in degrees
        
    Returns:
        numpy.array: Group delay in seconds
    """
    if len(frequencies) < 2:
        return np.zeros_like(frequencies)
    
    # Convert phase to radians
    phases_rad = np.radians(phases_deg)
    
    # Calculate negative derivative of phase with respect to angular frequency
    # d(phase)/d(omega) = d(phase)/d(f) * d(f)/d(omega) = d(phase)/d(f) * (1/(2π))
    # Group delay = -d(phase)/d(omega) = -d(phase)/d(f) * (1/(2π))
    
    # Calculate phase derivative with respect to frequency
    phase_derivative = np.gradient(phases_rad, frequencies)
    
    # Calculate group delay
    group_delay = -phase_derivative / (2 * np.pi)
    
    return group_delay

def write_frd_file(filename, frequencies, magnitudes, phases=None):
    # Ensure directory exists
    dir_path = os.path.dirname(filename)
    os.makedirs(dir_path, exist_ok=True)
    with open(filename, 'w') as f:
        # Write header
        if phases is not None:
            f.write("# pbrAudioRender")
            f.write("# Frequency Magnitude Phase")
            for f_idx in range(len(frequencies)):
                f.write(f"{frequencies[f_idx]} {magnitudes[f_idx]} {phases[f_idx]}\n")
        else:
            f.write("# pbrAudioRender")
            f.write("# Frequency Magnitude")
            for f_idx in range(len(frequencies)):
                f.write(f"{frequencies[f_idx]} {magnitudes[f_idx]}\n")
