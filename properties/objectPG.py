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
    def update_connected_value(self, context):
        object = context.object
        items = object.pbraudio_connected.values()
        if len(items) > 0:
            for item in items:
                connected = bpy.data.objects[item.connected_object]
                for connected_item in connected.pbraudio_connected.values():
                    if object.name == connected_item.connected_object:
                        if not connected_item.connected_value == item.connected_value:
                            connected_item.connected_value = item.connected_value

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
        subtype='FACTOR',
        update=update_connected_value
    )
classes.append(PBRAudioConnectedObjectList)

class PBRAudioObjectProperties(PropertyGroup):
    def disable_ground(self, context):
        object = context.object
        collection = object.users_collection[0]
        for obj in collection.objects.values():
            if not obj == object:
                if hasattr(obj.pbraudio, 'ground_disable'):
                    obj.pbraudio.ground_disable = object.pbraudio.ground

    def poll_selected_connected_object(self, object):
        return object.type == 'MESH' and not self.name == object.name

    """pbrAudio Material nodetree"""
    nodetree: PointerProperty(
        name="NodeTree",
        type=materialsNT.AcousticMaterialNodeTree
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

    ground: BoolProperty(
        name="Define as Ground",
        description="Enable GroundSound Synth",
        default=False,
        update=disable_ground
    )

    ground_disable: BoolProperty(
        default=False
    )

    """Connected Object selection properties for pbrAudio"""
    selected_connected_object: PointerProperty(
        name="selected_connected_object",
        type=bpy.types.Object,
        poll=poll_selected_connected_object
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
