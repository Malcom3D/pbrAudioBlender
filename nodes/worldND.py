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
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty

from .baseND import AcousticWorldNode

classes = []

class pbrAudioPreviewNode(AcousticWorldNode):
    """Acoustic data value previewer node"""
    bl_idname = 'pbrAudioPreviewNode'
    bl_label = "Acoustic World Preview"

#    def sync_data(self, context):
    def sync_data(self):
        # input Value
        if self.inputs[0].is_linked and not self.inputs[0].default_value == self.inputs[0].links[0].from_socket.default_value:
           # Read the value from_socket.default_value and write to local self.inputs[0].default_value to be viewed
           self.inputs[0].default_value = self.inputs[0].links[0].from_socket.default_value

    def init(self, context):
        self.inputs.new('pbrAudioWorldParameterNodeSocket', "data")

    def draw_buttons(self, context, layout):
        self.sync_data()

    def draw_buttons_ext(self, context, layout):
        layout.label(text=f"Socket Value: {self.inputs[0].default_value}")

classes.append(pbrAudioPreviewNode)

class pbrAudioValueNode(AcousticWorldNode):
    """Acoustic data value output node"""
    bl_idname = 'pbrAudioValueNode'
    bl_label = "Acoustic World Preview"

    value: FloatProperty(
        name="value"
    )

#    def sync_data(self, context):
    def sync_data(self):
        # output Value
        if self.outputs[0].is_linked and not self.value == self.outputs[0].default_value:
           # the value of the slider is the output socket, write it's value to self.value to be readed from exporter
           self.value = self.outputs[0].default_value

    def init(self, context):
        self.outputs.new('pbrAudioWorldParameterNodeSocket', "data")

    def draw_buttons(self, context, layout):
        self.sync_data()

    def draw_buttons_ext(self, context, layout):
        layout.label(text=f"Value: {self.value}")
        layout.label(text=f"Socket Value: {self.outputs[0].default_value}")

    def update(self):
        self.sync_data()

classes.append(pbrAudioValueNode)

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

    def socket_value_update(context):
        self.sync_data(context)

classes.append(pbrAudioWorldOutputNode)

class pbrAudioWorldMaterialNode(AcousticWorldNode):
    """Acoustic sound speed properties node"""
    bl_idname = 'pbrAudioWorldMaterialNode'
    bl_label = "World medium Parameters"

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
        if self.inputs[0].is_linked and not self.density == self.inputs[1].default_value:
           # read the local self.inputs[0].default_value and write to self.density to be used for computation
           self.density = self.inputs[0].default_value
        else:
           # the value of the slider is the input socket, write it's value to self.density to be readed from exporter and used for computation
           self.density = self.inputs[0].default_value

        # output Sound Speed
        if self.outputs[0].is_linked and not self.outputs[0].default_value == self.pbraudio_sound_speed:
           # self.pbraudio_sound_speed is computed with compute_speed(). write it's value to output socket to be readed from to_node
           self.outputs[0].default_value = self.pbraudio_sound_speed

    def compute_speed_imp(self, context):
       self.compute_speed(self, context)
       self.compute_impedence(self, context)

    def compute_impedence(self, context):
        self.impedence = self.density*self.pbraudio_sound_speed

    def compute_speed(self, context):
        if self.medium_type == 'GAS':
           self.pbraudio_sound_speed = sqrt((self.C_p/self.C_v)*(self.R_0/self.M)*(self.pbraudio_temperature+273.15))
        elif self.medium_type == 'LIQUID':
           self.pbraudio_sound_speed = sqrt(self.K/self.density)
        elif self.medium_type == 'SOLID':
           self.pbraudio_sound_speed = sqrt(self.E/self.density)

    pbraudio_type: StringProperty(default='WorldMedium')

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
        name="Medium sound speed in m/s",
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
        name="Temperature in °C",
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

classes.append(pbrAudioWorldMaterialNode)

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

    pbraudio_impedence: FloatProperty(
        name="Medium impedence in Pa⋅s/m",
        default=413.3
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldPropertyNodeSocket', "Impedence")
        self.inputs.new('pbrAudioWorldMaterialNodeSocket', "Sound Speed in m/s")
        self.inputs.new('pbrAudioWorldParameterNodeSocket', "Density in kg/m³")
        self.outputs[0].default_value = self.pbraudio_impedence

    def draw_buttons(self, context, layout):
        pass

#        if self.outputs[0].is_linked:
#            for link in self.outputs[0].links:
#                if link.to_socket.pbraudio_type == 'pbrAudioWorldPropertyNodeSocket':
#                    self.pbraudio_impedence = self.outputs[0].default_value
#                else:
#                    nodetree = self.id_data
#                    nodetree.links.remove(link)

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

    pbraudio_density: FloatProperty(
        name="Medium Density in kg/m³",
        default=1.2041,
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldParameterNodeSocket', "Density")
        self.outputs[0].default_value = self.pbraudio_density

    def draw_buttons(self, context, layout):
        pass

#        if self.outputs[0].is_linked:
#            for link in self.outputs[0].links:
#                if link.to_socket.pbraudio_type == 'pbrAudioWorldParameterNodeSocket':
#                    self.pbraudio_density = self.outputs[0].default_value
#                else:
#                    nodetree = self.id_data
#                    nodetree.links.remove(link)

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

    pbraudio_temperature: FloatProperty(
        name="Temperature in °C",
        default=20,
        min=-273.15,
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldParameterNodeSocket', "Temperature in Celsius degree")
        self.outputs[0].default_value = self.pbraudio_temperature

    def draw_buttons(self, context, layout):
         pass

#        if self.outputs[0].is_linked:
#            for link in self.outputs[0].links:
#                if link.to_socket.pbraudio_type == 'pbrAudioWorldParameterNodeSocket':
#                    self.pbraudio_temperature = self.outputs[0].default_value
#                else:
#                    nodetree = self.id_data
#                    nodetree.links.remove(link)

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

    ambisonic_file: StringProperty(
        name="Audio File",
        description="Path to ambisonic file",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
    )
 
    sphere_radius: FloatProperty(
        name="Radius of field sphere",
        default=1.0
    )
 
    ambisonic_order: IntProperty(
        name="Channel number",
        default=3,
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldEnvironmentNodeSocket', "Environment")

    def draw_buttons(self, context, layout):
#        if self.outputs[0].is_linked:
#            for link in self.outputs[0].links:
#                if not link.to_socket.pbraudio_type == 'pbrAudioWorldEnvironmentNodeSocket':
#                    nodetree = self.id_data
#                    nodetree.links.remove(link)

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        layout.prop(self, "ambisonic_file")
        layout.prop(self, "ambisonic_order")
        layout.prop(self, "sphere_radius")

    def draw_label(self):
        return "Acoustic Environment"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioEnvironmentNode)
