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
from numpy import sqrt
from bpy.types import Node
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty, PointerProperty

from .baseND import AcousticWorldNode

classes = []

class pbrAudioWorldOutputNode(AcousticWorldNode):
    """Acoustic world output node"""
    bl_idname = 'pbrAudioWorldOutputNode'
    bl_label = "World Output"

    def sync_data(self, context):
        # input Sound Speed
        if self.inputs[0].is_linked and not self.inputs[0].default_value == self.inputs[0].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[0].default_value
           self.inputs[0].default_value = self.inputs[0].links[0].from_socket.default_value
        # input Impedence
        if self.inputs[1].is_linked and not self.inputs[1].default_value == self.inputs[1].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[1].default_value
           self.inputs[1].default_value = self.inputs[1].links[0].from_socket.default_value
        # input Environment
        if self.inputs[2].is_linked and not self.inputs[2].default_value == self.inputs[2].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[2].default_value
           self.inputs[2].default_value = self.inputs[2].links[0].from_socket.default_value

    pbraudio_type: StringProperty(default='WorldOutput')

    def init(self, context):
        self.inputs.new('pbrAudioWorldMaterialNodeSocket', "Sound Speed")
        self.inputs.new('pbrAudioWorldPropertyNodeSocket', "Impedence")
        self.inputs.new('pbrAudioWorldEnvironmentNodeSocket', "Environment")

    def draw_buttons_ext(self, context, layout):
        layout.label(text=f"Sound Speed: {self.inputs[0].default_value} m/s")
        layout.label(text=f"Impedence: {self.inputs[1].default_value} kg/m³")
        layout.label(text=f"Environment: {self.inputs[2].default_value}")

    def socket_value_update(context):
        self.sync_data(context)

classes.append(pbrAudioWorldOutputNode)

class pbrAudioWorldShaderNode(AcousticWorldNode):
    """Acoustic sound speed properties node"""
    bl_idname = 'pbrAudioWorldShaderNode'
    bl_label = "World medium shader parameters"

    def sync_data(self, context):
        # input Temperature
        if self.inputs[0].is_linked and not self.inputs[0].default_value == self.inputs[0].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[0].default_value
           self.inputs[0].default_value = self.inputs[0].links[0].from_socket.default_value
        if self.inputs[0].is_linked and not self.temperature == self.inputs[0].default_value:
           # read the local self.inputs[0].default_value and write to self.temperature to be used for computation
           self.temperature = self.inputs[0].default_value
        else:
           # the value of the slider is the input socket, write it's value to self.temperature to be readed from exporter and used for computation
           self.temperature = self.inputs[0].default_value
        # input Density
        if self.inputs[1].is_linked and not self.inputs[1].default_value == self.inputs[1].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[1].default_value
           self.inputs[1].default_value = self.inputs[1].links[0].from_socket.default_value
        if self.inputs[1].is_linked and not self.density == self.inputs[1].default_value:
           # read the local self.inputs[1].default_value and write to self.density to be used for computation
           self.density = self.inputs[1].default_value
        else:
           # the value of the slider is the input socket, write it's value to self.density to be readed from exporter and used for computation
           self.density = self.inputs[1].default_value

        # output Sound Speed
        if self.outputs[0].is_linked and not self.outputs[0].default_value == self.pbraudio_sound_speed:
           # self.pbraudio_sound_speed is computed with compute_speed(). write it's value to output socket to be readed from to_node
           self.outputs[0].default_value = self.pbraudio_sound_speed

    def compute_speed_imp(self, context):
       self.compute_speed(context)
       self.compute_impedence(context)

    def compute_impedence(self, context):
        self.impedence = self.density*self.pbraudio_sound_speed

    def compute_speed(self, context):
        if self.medium_type == 'GAS':
           self.pbraudio_sound_speed = sqrt((self.C_p/self.C_v)*(self.R_0/self.M)*(self.temperature+273.15))
        elif self.medium_type == 'LIQUID':
           self.pbraudio_sound_speed = sqrt(self.K/self.density)
        elif self.medium_type == 'SOLID':
           self.pbraudio_sound_speed = sqrt(self.E/self.density)

    pbraudio_type: StringProperty(default='WorldShader')

    medium_type: EnumProperty(
        name="Medium Type",
        items=[
            ('GAS', "Gas", "Gas medium"),
            ('LIQUID', "Liquid", "Liquid medium"),
            ('SOLID', "Solid", "Solid medium"),
        ],
        default='GAS'
    )

    C_p: FloatProperty(
        name="Specific heat @ constant pressure in kJ/kg·K",
        default=1.0,
        update=compute_speed
    )

    C_v: FloatProperty(
        name="Specific heat @ constant volume in kJ/kg·K",
        default=0.718,
        update=compute_speed
    )

    R_0: FloatProperty(
        name="Gas constant",
        default=8.31446261815324,
        update=compute_speed
    )

    M: FloatProperty(
        name="Molar mass",
        default=0.0289645,
        update=compute_speed
    )

    K: FloatProperty(
        name="Bulk modulus in GPa",
        default=2.2, #water, 0.142 for air
        update=compute_speed
    )

    E: FloatProperty(
        name="Young modulus in GPa",
        default=0.005,
        update=compute_speed
    )

    pbraudio_sound_speed: FloatProperty(
        name="sound_speed",
        description="Medium sound speed in m/s",
        default=343.21,
        update=compute_impedence
    )

    impedence: FloatProperty(
        name="Medium impedence in Pa⋅s/m",
        default=413.3
    )

    density: FloatProperty(
        name="Medium Density in kg/m³",
        default=1.2041,
        update=compute_speed_imp
    )

    temperature: FloatProperty(
        name="Temperature",
        description="Temperature in °C",
        default=20,
        min=-273.15,
        update=compute_speed_imp
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldMaterialNodeSocket', "Sound Speed in m/s")
        self.inputs.new('pbrAudioWorldParameterNodeSocket', "Temperature in °C")
        self.inputs.new('pbrAudioWorldParameterNodeSocket', "Density in kg/m³")

    def draw_buttons(self, context, layout):
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        layout.prop(self, "medium_type", text='Type')

        if self.medium_type == 'GAS':
            layout.prop(self, "C_p", text='Cp: Specific heat at constant pressure', slider=True)
            layout.prop(self, "C_v", text='Cv: Specific heat at constant volume', slider=True)
            layout.prop(self, "R_0", text='R0: Gas constant', slider=True)
            layout.prop(self, "M", text='M: Molar Mass', slider=True)
        if self.medium_type == 'LIQUID':
            layout.prop(self, "K", text='K: Bulk modulus', slider=True)
        if self.medium_type == 'SOLID':
            layout.prop(self, "E", text='E: Young\'s modulus', slider=True)

    def draw_label(self):
        return f"Acoustic World Material"

    def draw_buttons_ext(self, context, layout):
        layout.label(text=f"Sound Speed: {self.pbraudio_sound_speed} m/s")
        layout.label(text=f"Temperature: {self.temperature} °C")
        layout.label(text=f"Density: {self.density} kg/m³")

    def socket_value_update(context):
        self.sync_data(context)

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioWorldShaderNode)

class pbrAudioImpedenceNode(AcousticWorldNode):
    """Acoustic impedence properties node"""
    bl_idname = 'pbrAudioImpedenceNode'
    bl_label = "Acoustic Impedence Parameters"

    def sync_data(self, context):
        # input Sound Speed
        if self.inputs[0].is_linked and not self.inputs[0].default_value == self.inputs[0].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[0].default_value
           self.inputs[0].default_value = self.inputs[0].links[0].from_socket.default_value
        # input Density
        if self.inputs[1].is_linked and not self.inputs[1].default_value == self.inputs[1].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[1].default_value
           self.inputs[1].default_value = self.inputs[1].links[0].from_socket.default_value
        # output Impedence
        if self.outputs[0].is_linked and self.outputs[0].default_value == self.pbraudio_impedence:
           # self.pbraudio_impedence is computed with compute_impedence(). write it's value to output socket to be readed from to_node
           self.outputs[0].default_value = self.pbraudio_impedence

    def compute_impedence(self, context):
        sound_speed, density = (None for _ in range(2))
        if self.inputs[0].is_linked:
            sound_speed = self.inputs[0].default_value
        if self.inputs[1].is_linked:
            density = self.inputs[1].default_value
        if not sound_speed == None and not density == None:
            self.pbraudio_impedence = density*sound_speed

    pbraudio_type: StringProperty(default='WorldImpedence')

    pbraudio_impedence: FloatProperty(
        name="impedence",
        description="Medium impedence in Pa⋅s/m",
        default=413.3
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldPropertyNodeSocket', "Impedence")
        self.inputs.new('pbrAudioWorldMaterialNodeSocket', "Sound Speed in m/s")
        self.inputs.new('pbrAudioWorldParameterNodeSocket', "Density in kg/m³")
        self.outputs[0].default_value = self.pbraudio_impedence

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return f"Acoustic Impedence"

    def draw_buttons_ext(self, context, layout):
        layout.label(text=f"Impedence: {self.pbraudio_impedence} Pa⋅s/m")
        layout.label(text=f"Sound Speed: {self.inputs[0].default_value} m/s")
        layout.label(text=f"Density: {self.inputs[1].default_value} kg/m³")

    def socket_value_update(context):
        self.sync_data(context)

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioImpedenceNode)

class pbrAudioDensityNode(AcousticWorldNode):
    """Acoustic density properties node"""
    bl_idname = 'pbrAudioDensityNode'
    bl_label = "Acoustic Density Parameters"

    def sync_data(self, context):
        # output Density
        if self.outputs[0].is_linked and not self.pbraudio_density == self.outputs[0].default_value:
           # the value of the slider is the output socket, write it's value to self.pbraudio_density to be readed from exporter
           self.pbraudio_density = self.outputs[0].default_value

    pbraudio_type: StringProperty(default='WorldDensity')

    pbraudio_density: FloatProperty(
        name="density",
        description="Medium Density in kg/m³",
        default=1.2041,
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldParameterNodeSocket', "Density")
        self.outputs[0].default_value = self.pbraudio_density

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Density"

    def draw_buttons_ext(self, context, layout):
        self.sync_data(context)
        layout.label(text=f"Density: {self.pbraudio_density} kg/m³")

    def socket_value_update(context):
        self.sync_data(context)

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioDensityNode)

class pbrAudioTemperatureNode(AcousticWorldNode):
    """Acoustic temperature properties node"""
    bl_idname = 'pbrAudioTemperatureNode'
    bl_label = "Acoustic Temperature Parameters"

    def sync_data(self, context):
        # output Temperature
        if self.outputs[0].is_linked and not self.outputs[0].default_value == self.pbraudio_temperature:
           # the value of the slider is the output socket, write it's value to self.pbraudio_temperature to be readed from exporter
           self.pbraudio_temperature = self.outputs[0].default_value

    pbraudio_type: StringProperty(default='WorldTemperature')

    pbraudio_temperature: FloatProperty(
        name="temperature",
        description="Temperature in °C",
        default=20,
        min=-273.15,
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldParameterNodeSocket', "Temperature in Celsius degree")
        self.outputs[0].default_value = self.pbraudio_temperature

    def draw_buttons(self, context, layout):
         pass

    def draw_label(self):
        return "Temperature"

    def draw_buttons_ext(self, context, layout):
        layout.label(text=f"Temperature: {self.pbraudio_temperature} °C")

    def socket_value_update(context):
        self.sync_data(context)

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioTemperatureNode)

class pbrAudioEnvironmentNode(AcousticWorldNode):
    """pbrAudio environment node"""
    bl_idname = 'pbrAudioEnvironmentNode'
    bl_label = "Environment"

    def sync_data(self, context):
        # output Temperature
        if self.outputs[0].is_linked and not self.outputs[0].default_value == self.pbraudio_field_datafile:
           # the value of the self.pbraudio_field_datafile is computed, write it's value to self.outputs[0].default_value to be readed from exporter
           self.outputs[0].default_value = self.pbraudio_field_datafile

    pbraudio_field_datafile: StringProperty(
        name="Field Data File",
        description="Path to json file with field data for the ambisonic 3D decoder (sphere field)",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
    )

    ambisonic_file: StringProperty(
        name="Ambisonic File",
        description="Path to ambisonic file",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
    )

    selected_object: PointerProperty(
        name="Selected Object",
        description="Select an object for environment reference",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type in {'EMPTY'}# and obj.pbraudio.environment
    )

    pbraudio_type: StringProperty(default='WorldEnvironment')

    def init(self, context):
        self.outputs.new('pbrAudioWorldEnvironmentNodeSocket', "Environment")

    def draw_buttons(self, context, layout):
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        layout.prop(self, "ambisonic_file")
        layout.prop(self, "selected_object", text="Environment Object")
    def draw_label(self):
        return "Acoustic Environment"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioEnvironmentNode)
