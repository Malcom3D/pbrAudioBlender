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

class AcousticMaterialProperties(PropertyGroup):
    """Acoustic material properties that will be driven by nodes"""

    # Material name for identification
    name: StringProperty(
        description="Name of the acoustic material",
        default="Acoustic Material"
    )

    """Acoustic Shader properties"""
    sound_speed: FloatProperty(
        name="Sound Speed in m/s",
        default=1000.0,
        soft_min=0.0,
        soft_max=20000.0
    )

    young_modulus: FloatProperty(
        name="Young modulus in GPa",
        default=1.0,
        min=0.0,
        soft_max=1500.0
    )

    poisson_ratio: FloatProperty(
        name="Poisson Ratio",
        default=0.46,
        min=-1.0,
        max=0.5
    )

    density: FloatProperty(
        name="Density in kg/m³",
        default=800.0,
        min=0.0,
        soft_max=25000.0
    )

    damping: FloatProperty(
        name="Rayleigh Damping in %",
        default=5,
        min=0.0,
        max=100
    )

    friction: FloatProperty(
        name="Friction",
        default=0.0,
        min=0.0,
        soft_max=1.0
    )

    roughness: FloatProperty(
        name="Normalized Roughness",
        default=0.0,
        min=0.0,
        max=1.0
    )

    low_frequency: FloatProperty(
        name="Low Frequency",
        default=5.0,
        min=0.0,
        soft_max=1000.0
    )

    high_frequency: FloatProperty(
        name="High Frequency",
        default=24000.0,
        soft_min=10000.0,
        max=96000.0
    )

    """Acoustic Properties properties"""
    absorption: FloatProperty(
        name="Absorption",
        default=0.0,
        min=0.0,
        max=1.0
    )

    refraction: FloatProperty(
        name="Refraction",
        default=0.0,
        min=0.0,
        max=1.0
    )

    reflection: FloatProperty(
        name="Reflection",
        default=0.0,
        min=0.0,
        max=1.0
    )

    scattering: FloatProperty(
        name="Scattering",
        default=0.0,
        min=0.0,
        max=1.0
    )

classes.append(AcousticMaterialProperties)
