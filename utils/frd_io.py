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

import os
import math
import numpy as np
from scipy.interpolate import CubicSpline, SmoothSphereBivariateSpline, RectBivariateSpline
import warnings


def parse_frd_file(filepath, has_phase=False, has_imaginary=False):
    """
    Parse FRD file and return frequency, magnitude, and phase arrays.
    Supports default, .cal, .csv, and .txt formats.
    """
    if os.path.exists(filepath):
        if filepath.endswith('.cal'):
            return parse_cal_file(filepath)
        elif filepath.endswith('.csv'):
            return parse_csv_file(filepath)
        elif filepath.endswith('.txt'):
            return parse_txt_file(filepath)
        else:
            # Default parsing (assuming space-separated columns)
            return parse_default_file(filepath, has_phase, has_imaginary)
    else:
        print(f"[Errno 2] No such file or directory: {filepath}")

def parse_cal_file(filepath):
    """
    Parse .cal file assuming it has columns: frequency, magnitude, phase (degrees)
    """
    frequencies = []
    magnitudes = []
    phases = []

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
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
        return np.array(frequencies), np.array(magnitudes), np.array(phases)
    except Exception as e:
        print(f"Error parsing CAL file {filepath}: {e}")
        return np.array([]), np.array([]), np.array([])

def parse_csv_file(filepath):
    """
    Parse .csv file expecting columns: frequency, magnitude, phase
    """
    import csv
    frequencies = []
    magnitudes = []
    phases = []

    try:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    try:
                        freq = float(row[0])
                        mag = float(row[1])
                        phase = float(row[2])
                        frequencies.append(freq)
                        magnitudes.append(mag)
                        phases.append(phase)
                    except ValueError:
                        continue
        return np.array(frequencies), np.array(magnitudes), np.array(phases)
    except Exception as e:
        print(f"Error parsing CSV file {filepath}: {e}")
        return np.array([]), np.array([]), np.array([])

def parse_txt_file(filepath):
    """
    Parse .txt file assuming space-separated columns: frequency, magnitude, phase
    """
    frequencies = []
    magnitudes = []
    phases = []

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
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
        return np.array(frequencies), np.array(magnitudes), np.array(phases)
    except Exception as e:
        print(f"Error parsing TXT file {filepath}: {e}")
        return np.array([]), np.array([]), np.array([])

def parse_default_file(filepath, has_phase=False, has_imaginary=False):
    """
    Fallback parser assuming space-separated: freq, mag[, phase]
    """
    frequencies = []
    magnitudes = []
    phases = []

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if has_imaginary:
                    # Expect: freq, real, imaginary
                    if len(parts) >= 3:
                        try:
                            freq = float(parts[0])
                            real = float(parts[1])
                            imag = float(parts[2])
                            frequencies.append(freq)
                            # complex form
                            mag = np.abs(complex(real, imag))
                            phase = np.angle(complex(real, imag), deg=True)
                            magnitudes.append(mag)
                            phases.append(phase)
                        except ValueError:
                            continue
                elif has_phase:
                    # Expect: freq, mag, phase
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
                    # Expect: freq, mag
                    if len(parts) >= 2:
                        try:
                            freq = float(parts[0])
                            mag = float(parts[1])
                            frequencies.append(freq)
                            magnitudes.append(mag)
                        except ValueError:
                            continue
        return np.array(frequencies), np.array(magnitudes), np.array(phases)
    except Exception as e:
        print(f"Error parsing default file {filepath}: {e}")
        return np.array([]), np.array([]), np.array([])


def validate_frd_file(filepath):
    frequencies, magnitudes, phases = parse_frd_file(filepath)
    return validate_frd_data(frequencies, magnitudes, phases)

def validate_frd_data(frequencies, magnitudes, phases=None):
    """
    Validate the data arrays.
    """
    if frequencies.size == 0 or magnitudes.size == 0:
        return False
    if frequencies.shape[0] != magnitudes.shape[0]:
        return False
    if phases is not None and phases.size != 0 and phases.shape[0] != frequencies.shape[0]:
        return False
    if not np.all(np.diff(frequencies) > 0):
        print("Warning: Frequencies are not strictly increasing")
    return True

def compute_group_delay(frequencies, phases_deg):
    """
    Calculate group delay from phase data
    """
    if len(frequencies) < 2:
        return np.zeros_like(frequencies)
    # Convert phase from degrees to radians
    phases_rad = np.radians(phases_deg)
    # Calculate the derivative d(phase_rad)/d(omega), where omega=2*pi*f
    # Using np.gradient for numerical derivative
    dphase_df = np.gradient(phases_rad, frequencies)
    # Convert derivative with respect to frequency to derivative with respect to omega
    # d(phase_rad)/d(omega) = d(phase_rad)/d(f) * (1 / (2*pi))
    dphase_domega = dphase_df / (2 * np.pi)
    # Group delay is negative of this
    group_delay = -dphase_domega
    return group_delay

def resample_frd(frequencies, magnitudes, phases=None, num_points=100):
    """
    Resample frequency response data to 'num_points' over log-spaced frequencies
    using cubic spline interpolation.
    """
    if len(frequencies) < 2:
        # Not enough points to resample
        return frequencies, magnitudes, phases

    # Logarithmic space of frequencies
    log_f_min = np.log10(frequencies[0])
    log_f_max = np.log10(frequencies[-1])
    resampled_freqs = np.logspace(log_f_min, log_f_max, num_points)

    # Interpolate magnitude
    mag_spline = CubicSpline(np.log10(frequencies), magnitudes)
    resampled_magnitudes = mag_spline(np.log10(resampled_freqs))

    if phases is not None:
        # Unwrap phases to avoid jumps
        unwrapped_phases = np.unwrap(np.radians(phases))
        phase_spline = CubicSpline(np.log10(frequencies), unwrapped_phases)
        resampled_phases_unwrapped = phase_spline(np.log10(resampled_freqs))
        # Wrap phases to [-180, 180] 
        resampled_phases_deg = (np.degrees(resampled_phases_unwrapped) + 180) % 360 - 180
        return resampled_freqs, resampled_magnitudes, resampled_phases_deg
    else:
        return resampled_freqs, resampled_magnitudes, None

def interpolate_spatial_response(target_azimuth, target_elevation, spatial_points, responses, method='BILINEAR'):
    """
    Interpolate frequency response at a target direction from spatial points.
    
    Parameters:
        target_azimuth (float): Target azimuth in degrees
        target_elevation (float): Target elevation in degrees
        spatial_points (list): List of (azimuth, elevation) tuples in degrees
        responses (list): List of corresponding frequency response data (freq, mag, phase)
        method (str): Interpolation method ('NEAREST', 'BILINEAR', 'SPHERICAL')
    
    Returns:
        tuple: Interpolated (frequencies, magnitudes, phases)
    """
    if not spatial_points or not responses:
        return None
    
    # Convert to numpy arrays for easier manipulation
    spatial_points = np.array(spatial_points)
    
    # Check if all responses have the same frequency points
    base_freq = responses[0][0]
    for freq, _, _ in responses:
        if not np.array_equal(freq, base_freq):
            raise ValueError("All responses must have the same frequency points")
    
    if method == 'NEAREST':
        # Find nearest point using Euclidean distance
        distances = np.sqrt(
            (spatial_points[:, 0] - target_azimuth) ** 2 + 
            (spatial_points[:, 1] - target_elevation) ** 2
        )
        nearest_idx = np.argmin(distances)
        return responses[nearest_idx]
    
    elif method == 'BILINEAR':
        # Extract unique azimuth and elevation values
        azimuths = np.unique(spatial_points[:, 0])
        elevations = np.unique(spatial_points[:, 1])
        
        # Check if points form a regular grid
        if len(azimuths) * len(elevations) != len(spatial_points):
            warnings.warn("Points do not form a regular grid. Using nearest neighbor for BILINEAR.")
            return interpolate_spatial_response(
                target_azimuth, target_elevation, 
                spatial_points, responses, method='NEAREST'
            )
        
        # Create meshgrid for the regular grid
        az_grid, el_grid = np.meshgrid(azimuths, elevations, indexing='ij')
        
        # Initialize arrays for interpolated magnitude and phase
        n_freq = len(base_freq)
        interp_mag = np.zeros(n_freq)
        interp_phase = np.zeros(n_freq)
        
        # For each frequency, create a 2D interpolation
        for freq_idx in range(n_freq):
            # Extract magnitude and phase values at this frequency
            mag_grid = np.zeros_like(az_grid)
            phase_grid = np.zeros_like(az_grid)
            
            # Fill the grids
            for i, (az, el) in enumerate(spatial_points):
                az_idx = np.where(azimuths == az)[0][0]
                el_idx = np.where(elevations == el)[0][0]
                mag_grid[az_idx, el_idx] = responses[i][1][freq_idx]
                phase_grid[az_idx, el_idx] = responses[i][2][freq_idx]
            
            # Create cubic interpolation splines
            mag_spline = RectBivariateSpline(azimuths, elevations, mag_grid, kx=3, ky=3)
            phase_spline = RectBivariateSpline(azimuths, elevations, phase_grid, kx=3, ky=3)
            
            # Interpolate at target point
            interp_mag[freq_idx] = mag_spline(target_azimuth, target_elevation)[0, 0]
            interp_phase[freq_idx] = phase_spline(target_azimuth, target_elevation)[0, 0]
        
        return (base_freq, interp_mag, interp_phase)
    
    elif method == 'SPHERICAL':
        # Convert to radians for spherical coordinates
        # Note: SmoothSphereBivariateSpline expects colatitude (π/2 - elevation) and longitude (azimuth)
        # in radians, with colatitude in [0, π] and longitude in [0, 2π]
        
        # Convert to radians and adjust ranges
        azimuths_rad = np.radians(spatial_points[:, 0])
        elevations_rad = np.radians(spatial_points[:, 1])
        
        # Convert to colatitude (π/2 - elevation)
        colatitudes = np.pi/2 - elevations_rad
        
        # Ensure azimuths are in [0, 2π]
        azimuths_rad = np.mod(azimuths_rad, 2*np.pi)
        
        # Check for duplicate points
        unique_points = np.unique(np.column_stack([colatitudes, azimuths_rad]), axis=0)
        if len(unique_points) < len(colatitudes):
            warnings.warn("Duplicate spherical points detected. Using nearest neighbor.")
            return interpolate_spatial_response(
                target_azimuth, target_elevation, 
                spatial_points, responses, method='NEAREST'
            )
        
        # Convert target point
        target_az_rad = np.radians(target_azimuth) % (2*np.pi)
        target_el_rad = np.radians(target_elevation)
        target_colat = np.pi/2 - target_el_rad
        
        # Initialize arrays for interpolated magnitude and phase
        n_freq = len(base_freq)
        interp_mag = np.zeros(n_freq)
        interp_phase = np.zeros(n_freq)
        
        # For each frequency, create a spherical interpolation
        for freq_idx in range(n_freq):
            # Extract magnitude and phase values at this frequency
            mag_values = np.array([resp[1][freq_idx] for resp in responses])
            phase_values = np.array([resp[2][freq_idx] for resp in responses])
            
            try:
                # Create spherical spline for magnitude
                mag_spline = SmoothSphereBivariateSpline(
                    colatitudes, azimuths_rad, mag_values, 
                    s=len(colatitudes)  # Smoothing parameter
                )
                
                # Create spherical spline for phase
                phase_spline = SmoothSphereBivariateSpline(
                    colatitudes, azimuths_rad, phase_values,
                    s=len(colatitudes)  # Smoothing parameter
                )
                
                # Interpolate at target point
                interp_mag[freq_idx] = mag_spline(target_colat, target_az_rad)[0]
                interp_phase[freq_idx] = phase_spline(target_colat, target_az_rad)[0]
                
            except Exception as e:
                warnings.warn(f"Spherical interpolation failed: {e}. Using nearest neighbor.")
                return interpolate_spatial_response(
                    target_azimuth, target_elevation, 
                    spatial_points, responses, method='NEAREST'
                )
        
        return (base_freq, interp_mag, interp_phase)
    
    else:
        raise ValueError(f"Unknown interpolation method: {method}")

def write_frd_file(filename, frequencies, magnitudes, phases_deg=None, data_from=None):
    """
    Write the frequency response data to a file.
    """
    if not data_from == None:
        data_from = " from " + data_from
    lines = []
    lines.append(f"! pbrAudioRender-0.2.1.x\n")
    lines.append(f"! pbrAudio FRD Data\n")
    lines.append(f"!\n")
    lines.append(f"! frd_io exporter version 0.0.7\n")
    lines.append(f"! Frequency Response Data (FRD){data_from}\n")
    lines.append(f"!\n")
    lines.append(f"! Format: Frequency(Hz)  Magnitude(dB)  Phase(degrees)\n")
    lines.append(f"!\n")

    for i in range(len(frequencies)):
        f = frequencies[i]
        mag = magnitudes[i]
        if phases_deg is not None:
            phase = phases_deg[i]
            lines.append(f"{f} {mag} {phase}\n")
        else:
            lines.append(f"{f} {mag}\n")
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.writelines(lines)

def generate_bands(freq_min, freq_max, bands_per_octave):
    """
    Generate frequency bands from freq_min to frq_max with bands_per_octave bands per octave.

    Parameters:
        freq_min (float): Minimum frequency in Hz.
        freq_max (float): Maximum frequency in Hz.
        bands_per_octave (int): Number of bands per octave.

    Returns:
        Tuple[total number of bands, list of tuples]:
            total number of bands: The number of bands per octave for the number of computed number of octaves in the range
            list of tuples: Each tuple contains (lower_bound, upper_bound) of a band.
    """
    # Calculate the number of octaves in the range
    octaves = math.log2(freq_max / freq_min)
    total_bands = int(math.ceil(octaves * bands_per_octave))
    
    bands = []
    for i in range(total_bands):
        # Calculate the lower and upper bounds of each band
        lower_freq = freq_min * (2 ** (i / bands_per_octave))
        upper_freq = freq_min * (2 ** ((i + 1) / bands_per_octave))
        # Ensure the upper bound does not exceed freq_max
        if upper_freq > freq_max:
            upper_freq = freq_max
        # Append the band edges
        bands.append((lower_freq, upper_freq))
        # Stop if we've reached or exceeded freq_max
        if upper_freq >= freq_max:
            break
    return total_bands, bands
