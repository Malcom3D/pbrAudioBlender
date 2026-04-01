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
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, FloatProperty, StringProperty

classes = []

#class AcousticMaterialProperties(PropertyGroup):
#    """Acoustic material properties that will be driven by nodes"""
#
#    def set_sound_speed(self, value):
#        if value <= self.sound_speed_min:
#            self.sound_speed = self.sound_speed_min
#        elif self.sound_speed_max <= value:
#            self.sound_speed = self.sound_speed_max
#        else:
#            self.sound_speed = value
#
#    def set_young_modulus(self, value):
#        if value <= self.young_modulus_min:
#            self.young_modulus = self.young_modulus_min
#        elif self.young_modulus_max <= value:
#            self.young_modulus = self.young_modulus_max
#        else:
#            self.young_modulus = value
#
#    def set_poisson_ratio(self, value):
#        if value <= self.poisson_ratio_min:
#            self.poisson_ratio = self.poisson_ratio_min
#        elif self.poisson_ratio_max <= value:
#            self.poisson_ratio = self.poisson_ratio_max
#        else:
#            self.poisson_ratio = value
#
#    def set_density(self, value):
#        if value <= self.density_min:
#            self.density = self.density_min
#        elif self.density_max <= value:
#            self.density = self.density_max
#        else:
#            self.density = value
#
#    def set_damping(self, value):
#        if value <= self.damping_min:
#            self.damping = self.damping_min
#        elif self.damping_max <= value:
#            self.damping = self.damping_max
#        else:
#            self.damping = value
#
#    def set_friction(self, value):
#        if value <= self.friction_min:
#            self.friction = self.friction_min
#        elif self.friction_max <= value:
#            self.friction = self.friction_max
#        else:
#            self.friction = value
#
#    def set_roughness(self, value):
#        if value <= self.roughness_min:
#            self.roughness = self.roughness_min
#        elif self.roughness_max <= value:
#            self.roughness = self.roughness_max
#        else:
#            self.roughness = value
#
#    def set_low_frequency(self, value):
#        if value <= self.low_frequency_min:
#            self.low_frequency = self.low_frequency_min
#        elif self.low_frequency_max <= value:
#            self.low_frequency = self.low_frequency_max
#        else:
#            self.low_frequency = value
#
#    def set_high_frequency(self, value):
#        if value <= self.high_frequency_min:
#            self.high_frequency = self.high_frequency_min
#        elif self.high_frequency_max <= value:
#            self.high_frequency = self.high_frequency_max
#        else:
#            self.high_frequency = value
#
#    # Material name for identification
#    name: StringProperty(
#        description="Name of the acoustic material",
#        default="Acoustic Material"
#    )
#
#    """Acoustic Shader properties"""
#    sound_speed: FloatProperty(
#        name="Sound Speed in m/s",
#        default=1000.0,
#        set=set_sound_speed
#    )
#
#    sound_speed_min: FloatProperty(
#        name="Minimum Sound Speed in m/s",
#        default=0.0
#    )
#
#    sound_speed_max: FloatProperty(
#        name="Maximum Sound Speed in m/s",
#        default=25000.0
#    )
#
#    young_modulus: FloatProperty(
#        name="Young modulus in GPa",
#        default=1.0,
#        set=set_young_modulus
#    )
#
#    young_modulus_min: FloatProperty(
#        name="Minimum Young modulus in GPa",
#        default=0.0
#    )
#
#    young_modulus_max: FloatProperty(
#        name="Maximum Young modulus in GPa",
#        default=1500.0
#    )
#
#    poisson_ratio: FloatProperty(
#        name="Poisson Ratio",
#        default=0.46,
#        set=set_poisson_ratio
#    )
#
#    poisson_ratio_min:FloatProperty(
#        name="Minimum Poisson Ratio",
#        default=-1.0
#    )
#
#    poisson_ratio_max:FloatProperty(
#        name="Maximum Poisson Ratio",
#        default=-1.0
#    )
#
#    density: FloatProperty(
#        name="Density in kg/m³",
#        default=800.0,
#        set=set_density
#    )
#
#    density_min: FloatProperty(
#        name="Minimum Density in kg/m³",
#        default=0.0
#    )
#
#    density_max: FloatProperty(
#        name="Maximum Density in kg/m³",
#        default=25000.0
#    )
#
#    damping: FloatProperty(
#        name="Rayleigh Damping in %",
#        default=5,
#        set=set_damping
#    )
#
#    damping_min: FloatProperty(
#        name="Minimum Rayleigh Damping in %",
#        default=0.0
#    )
#
#    damping_max: FloatProperty(
#        name="Maximum Rayleigh Damping in %",
#        default=100
#    )
#
#    friction: FloatProperty(
#        name="Friction",
#        default=0.0,
#        set=set_friction
#    )
#
#    friction_min: FloatProperty(
#        name="Minimum Friction",
#        default=0.0
#    )
#
#    friction_max: FloatProperty(
#        name="Maximum Friction",
#        default=1.0
#    )
#
#    roughness: FloatProperty(
#        name="Normalized Roughness",
#        default=0.0,
#        set=set_roughness
#    )
#
#    roughness_min: FloatProperty(
#        name="Minimum Normalized Roughness",
#        default=0.0
#    )
#
#    roughness_max: FloatProperty(
#        name="Maximum Normalized Roughness",
#        default=1.0
#    )
#
#    low_frequency: FloatProperty(
#        name="Low Frequency",
#        default=5.0,
#        set=set_low_frequency
#    )
#
#    low_frequency_min: FloatProperty(
#        name="Minimum Low Frequency",
#        default=0.0
#    )
#
#    low_frequency_max: FloatProperty(
#        name="Maximum Low Frequency",
#        default=1000.0
#    )
#
#    high_frequency: FloatProperty(
#        name="High Frequency",
#        default=24000.0,
#        set=set_high_frequency
#    )
#
#    high_frequency_min: FloatProperty(
#        name="Minimum High Frequency",
#        default=10000.0
#    )
#
#    high_frequency_max: FloatProperty(
#        name="Minimum High Frequency",
#        default=96000.0
#    )
#
#    """Acoustic Properties properties"""
#    absorption: FloatProperty(
#        name="Absorption",
#        default=0.0,
#        min=0.0,
#        max=1.0
#    )
#
#    refraction: FloatProperty(
#        name="Refraction",
#        default=0.0,
#        min=0.0,
#        max=1.0
#    )
#
#    reflection: FloatProperty(
#        name="Reflection",
#        default=0.0,
#        min=0.0,
#        max=1.0
#    )
#
#    scattering: FloatProperty(
#        name="Scattering",
#        default=0.0,
#        min=0.0,
#        max=1.0
#    )
#
#classes.append(AcousticMaterialProperties)
