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
import math
from bpy.types import PropertyGroup
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty, PointerProperty, BoolProperty

classes = []

class PBRAudioEngineProperties(PropertyGroup):
    def nyquist_limit(self, context):
        sample_rate = context.scene.pbraudio.sample_rate
        nyquist = sample_rate / 2
        if self.higher_frequency > nyquist:
            self.higher_frequency = nyquist

    """ Frequency Range Panel """
    enable_frequencies_range_set: BoolProperty(
        name="Frequency Range",
        description="Set the frequency range within the default medium",
    )

    lowest_frequency: FloatProperty(
        name="Lower Frequency",
        description="Limit minimum frequency to the lower frequency",
        default=20,
        min=1,
        max=20000,
    )

    higher_frequency: FloatProperty(
        name="Max Impedence Ratio",
        description="Limit maximum frequency to the higher frequency",
        default=20000,
        min=1,
        update=nyquist_limit
    )

    """ Sampling Panel """
    number_of_rays: IntProperty(
        name="Number of rays",
        description="Number of rays to be emitted per entity",
        default=1024,
        min=1,
        max=65536
    )

    direction_seed: IntProperty(
        name="Direction Seed",
        description="Rays direction seed",
        default=1,
        min=1,
        max=65536
    )

    max_interactions: IntProperty(
        name="Max Interactions",
        description="Maximum number of rays interactions",
        default=8192,
        min=1,
        max=65536
    )

    bands_per_octave: IntProperty(
        name="Bands for Octave",
        description="Number of bands for octave",
        default=8,
        min=0,
        max=256
    )

    use_dispersion_correction: BoolProperty(
        name="Dispersion Correction",
        description="Handle medium variations in speed factors like temperature and wind",
        default=False,
    )

    dispersion_order: IntProperty(
        name="Dispersion Order",
        description="Dispersion  correction order",
        default=2,
        min=0,
        max=256
    )

    use_extended_reaction: BoolProperty(
        name="Extended Reaction",
        description="Handle resonances of boundary structures from transmission absorption",
        default=False,
    )

    max_modal_reaction: IntProperty(
        name="Max Mode Reaction",
        description="Maximum number of resonant modal mode for extended reaction",
        default=3,
        min=0,
        max=256
    )

    use_complex_eigenray: BoolProperty(
        name="Complex Eigenray",
        description="Handle infrasound ray tracing",
        default=False,
    )

    max_complex_eigenray: IntProperty(
        name="Max Eigenray",
        description="Maximum number of eigenray",
        default=3,
        min=0,
        max=256
    )

    """ Adaptive mesh refinement Panel """
    enable_adr: BoolProperty(
        name="ADR",
        description="Enable adaptive mesh refinement",
        default=False,
    )

    adr_threshold: FloatProperty(
        name="ADR Threshold",
        description="Adaptive mesh refinement distance threshold in meters",
        default=30.0
    )

    """ Interface Panel """
    enable_interface: BoolProperty(
        name="Interface",
        description="Enable boundary interface with rays",
        default=False,
    )

    enable_absorption: BoolProperty(
        name="Absorption",
        description="Handle absorption at boundary and in medium",
        default=False,
    )

    enable_reflection: BoolProperty(
        name="Reflection",
        description="Handle reflection with boundary",
        default=False,
    )

    max_reflection: IntProperty(
        name="Max Reflection",
        description="Maximum number of rays bouces for reflection",
        default=8,
        min=1,
        max=2048
    )

    enable_scattering: BoolProperty(
        name="Scattering",
        description="Handle scattering at boundary and in medium",
        default=False,
    )

    max_scattering: IntProperty(
        name="Max Scattering",
        description="Maximum number of scattering rays",
        default=8,
        min=1,
        max=2048
    )

    enable_refraction: BoolProperty(
        name="Refraction",
        description="Handle refraction at boundary",
        default=False,
    )

    max_refraction: IntProperty(
        name="Max Refraction",
        description="Maximum number of recursive rays for refraction",
        default=8,
        min=1,
        max=2048
    )

    enable_diffraction: BoolProperty(
        name="Diffraction",
        description="Handle diffraction at boundary and in medium",
        default=False,
    )

    max_diffraction: IntProperty(
        name="Max Diffraction",
        description="Maximum number of rays for diffraction",
        default=8,
        min=1,
        max=2048
    )

    min_impedance_ratio: FloatProperty(
        name="Min Impedence Ratio",
        description="Minimum impedence ratio at boundaries between two materials",
        default=0.1,
        min=0.01,
        max=100,
    )

    max_impedance_ratio: FloatProperty(
        name="Max Impedence Ratio",
        description="Maximum impedence ratio at boundaries between two materials",
        default=10.0,
        min=0.01,
        max=100,
    )

    """ Resonance Panel """
    enable_resonance: BoolProperty(
        name="Resonant Structures",
        description="Enable resonant structures",
        default=False,
    )

    max_resonance_structure: IntProperty(
        name="Max Structures",
        description="Maximum number of resonance structures",
        default=5,
        min=1,
        max=8192,
    )

    decay_time_constant: FloatProperty(
        name="Decay Constant",
        description="Pressure attenuation in amplitude over time",
        default=0.99,
        min=0.01,
        max=1,
    )

    resonance_threshold: FloatProperty(
        name="Low Threshold",
        description="Low threshold for resonance vibration on structures",
        default=0.1,
        min=0.01,
        max=1,
    )

    enable_helmholtz: BoolProperty(
        name="Helmholtz",
        description="Handle Helmholtz resonator",
        default=False,
    )

    min_cavity_volume: FloatProperty(
        name="Min Volume",
        description="Minimum volume of Helmholtz resonator",
        default=0.1,
        min=0.01,
        max=1,
    )

    max_resonance_room_modes: IntProperty(
        name="Max Room Modes",
        description="Maximum number of resonance room modes for room sized Helmholtz resonator",
        default=5,
        min=1,
        max=2048,
    )

    enable_parallel_wall: BoolProperty(
        name="Parallel Wall",
        description="Handle parallel wall structure resonance",
        default=False,
    )

    min_wall_distance: FloatProperty(
        name="Min Distance",
        description="Minimum distance between parallel wall",
        default=0.5,
        min=0.01,
        max=100,
    )

    max_wall_distance: FloatProperty(
        name="Min Distance",
        description="Minimum distance between parallel wall",
        default=20.0,
        min=0.01,
        max=100,
    )

    enable_tube: BoolProperty(
        name="Tube Resonance",
        description="Handle tube like structure resonance",
        default=False,
    )

    min_tube_length: FloatProperty(
        name="Min Length",
        description="Minimum tube length of tube resonator",
        default=0.3,
        min=0.01,
        max=100.0,
    )

    min_tube_aspect_ratio: FloatProperty(
        name="Min Shape Ratio",
        description="Minimum tube shape aspect ratio",
        default=3.0,
        min=0.01,
        max=100.0,
    )

    """ Termination Panel """
    enable_termination: BoolProperty(
        name="Termination",
        description="Enable termination",
        default=False,
    )

    termination_type: EnumProperty(
        name="Type",
        description="Termination Type",
        items=[
            ('FINAL_FRAME', "Final Frame", "Terminate at the Final Frame of the rendering range"),
            ('SAMPLE_END', "Sample End", "Terminate after a number of samples after end of last (minimum) active sources"),
            ('REVERBERATION_TIME', "Reverberation Time", "Terminate after a number of seconds from the end of last active source"),
            ('ENERGY_THRESHOLD', "Energy Threshold", "Terminate if the pressure goes beyond a energy range"),
        ],
        default='FINAL_FRAME'
    )

    samples_after: IntProperty(
        name="Samples After",
        description="Number of samples after end of last (minimum) active sources",
        default=100,
        min=1,
        max=1024000,
    )

    min_active_sources: IntProperty(
        name="Min Sources",
        description="Minimim number of active sources",
        default=1,
        min=1,
        max=2048,
    )

    max_reverberation_time: FloatProperty(
        name="Max Time Limit",
        description="Maximum time in seconds of reverberation before termination",
        default=2.0,
        min=0.0,
        max=3600,
    )

    max_energy_threshold: FloatProperty(
        name="Max Threshold",
        description="Maximum energy value of pressure value beyond which terminate",
        default=1e6,
    )

    min_energy_threshold: FloatProperty(
        name="Min Threshold",
        description="Minimum energy value of pressure value beyond which terminate",
        default=1e-6,
    )

classes.append(PBRAudioEngineProperties)
