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
#    def compute_speed_imp(self, context):
#       self.compute_speed(self, context)
#       self.compute_impedence(self, context)

#    def compute_speed(self, context):
#       if self.type == 'GAS':
#          self.sound_speed = sqrt((self.C_p/self.C_v)*(self.R_0/self.M)*(self.temperature+273.15))
#       elif self.type == 'LIQUID':
#          self.sound_speed = sqrt(self.K/self.density)
#       elif self.type == 'SOLID':
#          self.sound_speed = sqrt(self.E/self.density)
#
#       if self.outputs['Sound Speed'].is_linked:
#          self.outputs['Sound Speed'].sound_speed = self.sound_speed
#
#    def compute_impedence(self, context):
#        self.impedence = self.density*self.sound_speed

    """ Sampling Panel """
    max_interaction: IntProperty(
        name="Maximum number of rays interactions",
        default=8192,
        min=1,
        max=65536
    )

    steps_per_octave: IntProperty(
        name="Number of bands for octave",
        default=8,
        min=0,
        max=256
    )

    use_dispersion_correction: BoolProperty(
        name="Handle medium variations in speed factors like temperature and wind",
        default=False,
    )

    dispersion_order: IntProperty(
        name="Enable resonant structures",
        default=2,
        min=0,
        max=256
    )

    use_extended_reaction: BoolProperty(
        name="Handle resonances of boundary structures from transmission absorption",
        default=False,
    )

    max_modal_reaction: IntProperty(
        name="Maximum number of resonant modal mode for extended reaction",
        default=3,
        min=0,
        max=256
    )

    """ Interface Panel """
    enable_interface: BoolProperty(
        name="Enable boundary interface with rays",
        default=False,
    )

    enable_absorption: BoolProperty(
        name="Handle absorption at boundary and in medium",
        default=False,
    )

    enable_reflection: BoolProperty(
        name="Handle reflection with boundary",
        default=False,
    )

    max_reflection: IntProperty(
        name="Maximum number of rays bouces for reflection",
        default=8,
        min=1,
        max=2048
    )

    enable_scattering: BoolProperty(
        name="Handle absorption at boundary and in medium",
        default=False,
    )

    max_scattering: IntProperty(
        name="Maximum number of recursive rays for refraction",
        default=8,
        min=1,
        max=2048
    )

    enable_refraction: BoolProperty(
        name="Handle absorption at boundary and in medium",
        default=False,
    )

    max_refraction: IntProperty(
        name="Maximum number of recursive rays for refraction",
        default=8,
        min=1,
        max=2048
    )

    enable_diffraction: BoolProperty(
        name="Handle diffraction at boundary and in medium",
        default=False,
    )

    max_diffraction: IntProperty(
        name="Maximum number of rays for diffraction",
        default=8,
        min=1,
        max=2048
    )

    min_impedance_ratio: FloatProperty(
        name="Minimum impedence ratio at boundaries between two materials",
        default=0.1,
        min=0.01,
        max=100,
    )

    max_impedance_ratio: FloatProperty(
        name="Maximum impedence ratio at boundaries between two materials",
        default=10.0,
        min=0.01,
        max=100,
    )

    """ Resonance Panel """
    enable_resonance: BoolProperty(
        name="Enable resonant structures",
        default=False,
    )

    max_resonance_structure: IntProperty(
        name="Maximum number of resonance structures",
        default=5,
        min=1,
        max=8192,
    )

    decay_time_constant: FloatProperty(
        name="Pressure attenuation in amplitude over time",
        default=0.99,
        min=0.01,
        max=1,
    )

    resonance_threshold: FloatProperty(
        name="Low threshold for resonance vibration",
        default=0.1,
        min=0.01,
        max=1,
    )

    enable_helmholtz: BoolProperty(
        name="Handle Helmholtz resonator",
        default=False,
    )

    min_cavity_volume: FloatProperty(
        name="Minimum volume of Helmholtz resonator",
        default=0.1,
        min=0.01,
        max=1,
    )

    max_resonance_room_modes: IntProperty(
        name="Maximum number of resonance room modes for room sized Helmholtz resonator",
        default=5,
        min=1,
        max=2048,
    )

    enable_parallel_wall: BoolProperty(
        name="Handle parallel wall structure resonance",
        default=False,
    )

    min_wall_distance: FloatProperty(
        name="Minimum distance between parallel wall",
        default=0.5,
        min=0.01,
        max=100,
    )

    max_wall_distance: FloatProperty(
        name="Minimum distance between parallel wall",
        default=20.0,
        min=0.01,
        max=100,
    )

    enable_tube: BoolProperty(
        name="Handle tube like structure resonance",
        default=False,
    )

    min_tube_length: FloatProperty(
        name="Minimum tube length of tube resonator",
        default=0.3,
        min=0.01,
        max=100.0,
    )

    min_tube_aspect_ratio: FloatProperty(
        name="Minimum tube shape aspect ratio",
        default=3.0,
        min=0.01,
        max=100.0,
    )

    """ Termination Panel """
    enable_termination: BoolProperty(
        name="Enable resonant structures",
        default=False,
    )

    termination_type: EnumProperty(
        name="Termination Type",
        items=[
            ('FINAL_FRAME', "Final Frame", "Terminate at the Final Frame of the rendering range"),
            ('SAMPLE_END', "Sample End", "Terminate after a number of samples after end of last (minimum) active sources"),
            ('REVERBERATION_TIME', "Reverberation Time", "Terminate after a number of seconds from the end of last active source"),
            ('ENERGY_THRESHOLD', "Energy Threshold", "Terminate if the pressure goes beyond a energy range"),
        ],
        default='FINAL_FRAME'
    )

    samples_after: IntProperty(
        name="Number of samples after end of last (minimum) active sources",
        default=100,
        min=1,
        max=1024000,
    )

    min_active_sources: IntProperty(
        name="Minimim number of active sources",
        default=1,
        min=1,
        max=2048,
    )

    max_reverberation_time: FloatProperty(
        name="Maximum time in seconds of reverberation before termination",
        default=2.0,
        min=0.0,
        max=3600,
    )

    max_energy_threshold: FloatProperty(
        name="Maximum energy value of pressure value beyond which terminate",
        default=1e6,
    )

    min_energy_threshold: FloatProperty(
        name="Minimum energy value of pressure value beyond which terminate",
        default=1e-6,
    )

classes.append(PBRAudioEngineProperties)
