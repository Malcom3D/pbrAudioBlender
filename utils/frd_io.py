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
import numpy as np
from scipy.interpolate import CubicSpline

def parse_frd_file(filepath, has_phase=False, has_imaginary=False):
    """
    Parse FRD, CAL, CSV, or TXT file and return frequency, magnitude, phase arrays or real/imaginary parts.

    Args:
        filepath (str): Path to the data file.
        has_phase (bool): True if file contains magnitude and phase.
        has_imaginary (bool): True if file contains real and imaginary parts.

    Returns:
        tuple: Depending on flags, returns:
            - (frequencies, magnitudes, phases)
            - (frequencies, real_parts, imag_parts)
    """
    frequencies = []
    magnitudes = []
    phases = []
    real_parts = []
    imag_parts = []

    # Determine file extension
    ext = os.path.splitext(filepath)[1].lower()

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('!'):
                    continue
                # split by comma, space, or tab
                parts = [p.strip() for p in line.replace(',', ' ').split()]
                if len(parts) == 0:
                    continue

                try:
                    if has_imaginary:
                        # Expecting frequency, real, imag
                        if len(parts) >= 3:
                            freq = float(parts[0])
                            real = float(parts[1])
                            imag = float(parts[2])
                            frequencies.append(freq)
                            real_parts.append(real)
                            imag_parts.append(imag)
                    elif has_phase:
                        # Expecting frequency, magnitude, phase
                        if len(parts) >= 3:
                            freq = float(parts[0])
                            mag = float(parts[1])
                            phase = float(parts[2])
                            frequencies.append(freq)
                            magnitudes.append(mag)
                            phases.append(phase)
                    else:
                        # Expecting frequency, magnitude
                        if len(parts) >= 2:
                            freq = float(parts[0])
                            mag = float(parts[1])
                            frequencies.append(freq)
                            magnitudes.append(mag)
                except ValueError:
                    continue
        if has_imaginary:
            return np.array(frequencies), np.array(real_parts), np.array(imag_parts)
        else:
            return np.array(frequencies), np.array(magnitudes), np.array(phases)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return np.array([]), np.array([]), np.array([])

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

def resample_data(frequencies, magnitudes, phases=None, num_points=100, use_spline=True):
    """
    Resample data to num_points over the frequency range using cubic spline or linear interpolation.
    """
    if len(frequencies) < 2:
        # Not enough data to resample
        if phases is not None:
            return frequencies, magnitudes, phases
        else:
            return frequencies, magnitudes

    # Create log-spaced frequency points for resampling
    f_min = np.log10(frequencies[0]) if frequencies[0] > 0 else np.log10(max(frequencies[0], 1e-6))
    f_max = np.log10(frequencies[-1])
    resampled_freqs = np.logspace(f_min, f_max, num_points)

    # Interpolate magnitude
    mag_spline = CubicSpline(np.log10(frequencies), magnitudes) if use_spline else None
    if use_spline:
        resampled_magnitudes = mag_spline(np.log10(resampled_freqs))
    else:
        resampled_magnitudes = np.interp(np.log10(resampled_freqs), np.log10(frequencies), magnitudes)

    # Resample phase if available
    if phases is not None:
        # Unwrap phase to avoid discontinuities
        unwrapped_phase = np.unwrap(np.radians(phases))
        phase_spline = CubicSpline(np.log10(frequencies), unwrapped_phase) if use_spline else None
        if use_spline:
            resampled_phase_unwrapped = phase_spline(np.log10(resampled_freqs))
        else:
            resampled_phase_unwrapped = np.interp(np.log10(resampled_freqs), np.log10(frequencies), np.radians(phases))
        # Wrap phase back to degrees within -180 to 180
        resampled_phases_deg = (np.degrees(resampled_phase_unwrapped) + 180) % 360 - 180
        return resampled_freqs, resampled_magnitudes, resampled_phases_deg
    else:
        return resampled_freqs, resampled_magnitudes

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

