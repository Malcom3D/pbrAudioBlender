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
from bpy.props import BoolProperty, PointerProperty, EnumProperty, FloatProperty, StringProperty, IntProperty

from ..nodetrees import acousticNT

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

class PBRAudioShardObjectList(PropertyGroup):
    """Shard Object properties"""
    shard_object: StringProperty(
        name="Shard Object Name",
        description="Name of the shard object"
    )
classes.append(PBRAudioShardObjectList)

class PBRAudioObjectProperties(PropertyGroup):
    def disable_ground(self, context):
        object = context.object
        collection = object.users_collection[0]
        for obj in collection.objects.values():
            if not obj == object:
                if hasattr(obj.pbraudio, 'ground_disable'):
                    obj.pbraudio.ground_disable = object.pbraudio.ground

    def enable_resonance(self, context):
        object = context.object
        if hasattr(object, 'connected'):
            object.connected = False

    def enable_connected(self, context):
        object = context.object
        if hasattr(object, 'resonance'):
            object.resonance = False

    def poll_selected_connected_object(self, object):
        return object.type == 'MESH' and not self.name == object.name

    def poll_selected_shard_object(self, object):
        if object.type == 'MESH' and not self.name == object.name:
            for shard_obj in object.pbraudio_shard.values():
                if object.name == shard_obj.shard_object:
                    return False
            return True
        else:
            return False

    """pbrAudio Material nodetree"""
    nodetree: PointerProperty(
        name="NodeTree",
        type=materialsNT.AcousticNodeTree
    )

    stochastic_variation: BoolProperty(
        name="Stochastic Variation",
        description="Add stochastic variation based on material properties",
        default=False,
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

    """Object Resonance"""
    resonance: BoolProperty(
        name="Enable object resonance",
        description="Enable Object Resonance Synth",
        default=False,
        update=enable_resonance
    )

    resonance_modes: IntProperty(
        name="Resonance Modal Modes",
        description="Int value between 0 and 100",
        default=5,
        min=1,
        max=100
    )

    connected: BoolProperty(
        name="Object is connected to other",
        description="Synth Object as Connected",
        default=False,
        update=enable_connected
    )

    """Connected Object selection properties for pbrAudio"""
    selected_connected_object: PointerProperty(
        name="selected_connected_object",
        type=bpy.types.Object,
        poll=poll_selected_connected_object
    )

    """Fractured Object properties for pbrAudio"""
    fractured: BoolProperty(
        name="Object is fractured",
        description="Enable fractureSound Synth",
        default=False
    )

    """Shards of Object selection properties for pbrAudio"""
    selected_shard_object: PointerProperty(
        name="selected_shard_object",
        type=bpy.types.Object,
        poll=poll_selected_shard_object
    )

    """Source properties for pbrAudio"""
    source: BoolProperty(
        name="pbraudio_source",
        description="Object is sound source",
        default=False
    )

    source_file: PointerProperty(
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

    """Environment properties for pbrAudio"""
    environment: BoolProperty(
        name="pbraudio_environment",
        description="Object is enviroment sound",
        default=False
    )

    environment_file: StringProperty(
        name="EnvironmetSource",
        description="Select the sound for the source",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default='',
    )

    environment_chanels: IntProperty(
        name="Number of Environment Chanels",
        description="Int value between 0 and 100",
        default=1,
    )

    environment_size: FloatProperty(
        name="Environment Size",
        description="Environment Sphere Size",
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
