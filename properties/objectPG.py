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
from bpy.props import BoolProperty, PointerProperty, EnumProperty, FloatProperty, StringProperty

from ..nodetrees import materialsNT

classes = []

class PBRAudioConnectedObjectList(PropertyGroup):
    """Connected Object properties"""
    connected_object: StringProperty(
        name="Connected Object Name",
        description="Name of the connected object"
    )

    connected_value: FloatProperty(
        name="Connected value",
        description="Float value between 0 and 1",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
classes.append(PBRAudioConnectedObjectList)

class PBRAudioObjectProperties(PropertyGroup):
    def toggle_ground(self, context):
        object = context.object
        collection = object.users_collection[0]
        for obj in collection.objects.values():
            if hasattr(obj.pbraudio, 'ground_toggle'):
                obj.pbraudio.ground_toggle = True

    """pbrAudio Material nodetree"""
    nodetree: PointerProperty(
        name="NodeTree",
        type=materialsNT.AudioMaterialNodeTree
    )

    """Acoustic Shader properties"""
    sound_speed: FloatProperty(
        name="Sound Speed",
        default=0.0
    )

    young_modulus: FloatProperty(
        name="Young modulus",
        default=0.0
    )

    poisson_ratio: FloatProperty(
        name="Poisson Ratio",
        default=0.0
    )

    density: FloatProperty(
        name="Density",
        default=0.0
    )

    damping: FloatProperty(
        name="Damping",
        default=0.0
    )

    friction: FloatProperty(
        name="Friction",
        default=0.0
    )

    roughness: FloatProperty(
        name="Roughness",
        default=0.0
    )

    low_frequency: FloatProperty(
        name="Low Frequency",
        default=1.0
    )

    high_frequency: FloatProperty(
        name="High Frequency",
        default=24000.0
    )

    """Acoustic Properties properties"""
    absorption: FloatProperty(
        name="Absorption",
        default=0.0
    )

    refraction: FloatProperty(
        name="Refraction",
        default=0.0
    )

    reflection: FloatProperty(
        name="Reflection",
        default=0.0
    )

    scattering: FloatProperty(
        name="Scattering",
        default=0.0
    )

    ground: BoolProperty(
        name="Define as Ground",
        description="Enable GroundSound Synth",
        default=False,
        update=toggle_ground
    )

    ground_toggle: BoolProperty(
        default=False
    )

    """Source properties for pbrAudio"""
    source: PointerProperty(
        name="SoundSource",
        type=bpy.types.Sound,
        description="Select the sound for the source"
    )

    source_type: EnumProperty(
        name="Type",
        items=[
            ('SPHERE', "Spheric", "Spheric wave sound source"),
            ('PLANE', "Plane", "Plane wave sound source"),
        ],
        default='SPHERE'
    )

    """Output properties for pbrAudio"""
    output: BoolProperty(
        name="SoundOutput",
        description="Select the sound for the source",
        default=False
    )

    output_type: EnumProperty(
        name="Type",
        items=[
            ('MONO', "Mono", "Mono sound output"),
            ('AMBI', "Ambisonic", "Ambisonic sound output"),
        ],
        default='MONO'
    )

    ambisonic_order: EnumProperty(
        name="Order",
        items=[
            ('1', "First", "First order"),
            ('2', "Second", "Second order"),
            ('3', "Third", "Third order"),
        ],
        default='1'
    )

classes.append(PBRAudioObjectProperties)
