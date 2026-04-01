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

classes = []

class pbrAudioWorldOutputNode(Node):
    """Acoustic world output node"""
    bl_idname = 'pbrAudioWorldOutputNode'
    bl_label = "World Output"

    def init(self, context):
        self.inputs.new('pbrAudioWorldOutputNodeSocket', "Sound Speed")
        self.inputs.new('pbrAudioWorldOutputNodeSocket', "Impedence")
        self.inputs.new('pbrAudioWorldEnvironmentNodeSocket', "Environment")

classes.append(pbrAudioWorldOutputNode)

class pbrAudioWorldMediumNode(Node):
    """Acoustic sound speed properties node"""
    bl_idname = 'pbrAudioWorldMediumNode'
    bl_label = "World medium Parameters"

    def compute_speed_imp(self, context):
       self.compute_speed(self, context)
       self.compute_impedence(self, context)

    def compute_impedence(self, context):
        self.impedence = self.density*self.sound_speed

    def compute_speed(self, context):
       for world in bpy.data.worlds.values():
          if hasattr(world, 'pbraudio'):
             pbraudio = world.pbraudio

       if self.type == 'GAS':
          self.pbraudio_sound_speed = sqrt((self.C_p/self.C_v)*(self.R_0/self.M)*(self.pbraudio_temperature+273.15))
       elif self.type == 'LIQUID':
          self.pbraudio_sound_speed = sqrt(self.K/self.pbraudio_density)
       elif self.type == 'SOLID':
          self.pbraudio_sound_speed = sqrt(self.E/self.pbraudio_density)

       if self.outputs['Sound Speed'].is_linked:
          self.outputs['Sound Speed'].sound_speed = self.pbraudio_sound_speed

    type: EnumProperty(
        name="Medium Type",
        items=[
            ('GAS', "Gas", "Gas medium"),
            ('LIQUID', "Liquid", "Liquid medium"),
            ('SOLID', "Solid", "Solid medium"),
        ],
        default='GAS'
    )

    C_p: FloatProperty(
        name="Specific heat at constant pressure",
        default=7.0,
        update=compute_speed
    )

    C_v: FloatProperty(
        name="Specific heat at constant volume",
        default=5.0,
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
        name="Bulk modulus",
        default=0.0,
        update=compute_speed
    )

    E: FloatProperty(
        name="Young modulus",
        default=0.0,
        update=compute_speed
    )

    pbraudio_sound_speed: FloatProperty(
        name="Medium sound speed",
        default=0.0,
        update=compute_impedence
    )

    pbraudio_impedence: FloatProperty(
        name="Medium impedence",
        default=0.0
    )

    pbraudio_density: FloatProperty(
        name="Medium Density",
        default=1.2041,
        min=0.1,
        max=5.0,
        update=compute_speed_imp
    )

    pbraudio_temperature: FloatProperty(
        name="Temperature in Celsius degree",
        default=20,
        min=-273.15,
        update=compute_speed_imp
    )

    def init(self, context):
        self.outputs.new('pbrAudioWorldPropertyNodeSocket', "Sound Speed")
        self.inputs.new('pbrAudioWorldPropertyNodeSocket', "Temperature in Celsius degree")
        self.inputs.new('pbrAudioWorldPropertyNodeSocket', "Density")

    def draw_buttons(self, context, layout):
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        layout.prop(self, "type", text='Type')

        if pbraudio.type == 'GAS':
            layout.prop(self, "pbraudio_C_p", text='Cp: Specific heat at constant pressure', slider=True)
            layout.prop(self, "pbraudio_C_v", text='Cv: Specific heat at constant volume', slider=True)
            layout.prop(self, "pbraudio_R_0", text='R0: Gas constant', slider=True)
            layout.prop(self, "pbraudio_M", text='M: Molar Mass', slider=True)
        if pbraudio.type == 'LIQUID':
            layout.prop(self, "pbraudio_K", text='K: Bulk modulus', slider=True)
        if pbraudio.type == 'SOLID':
            layout.prop(self, "pbraudio_E", text='E: Young\'s modulus', slider=True)

    def draw_label(self):
        return "Acoustic Medium"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioWorldMediumNode)

class pbrAudioImpedenceNode(Node):
    """Acoustic impedence properties node"""
    bl_idname = 'pbrAudioImpedenceNode'
    bl_label = "Acoustic Impedence Parameters"

    def init(self, context):
        self.outputs.new('pbrAudioWorldParameterNodeSocket', "Impedence")
        self.inputs.new('pbrAudioWorldPropertyNodeSocket', "Sound Speed")
        self.inputs.new('pbrAudioWorldPropertyNodeSocket', "Density")

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Acoustic Impedence"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioImpedenceNode)

class pbrAudioDensityNode(Node):
    """Acoustic density properties node"""
    bl_idname = 'pbrAudioDensityNode'
    bl_label = "Acoustic Density Parameters"

    def init(self, context):
        self.outputs.new('pbrAudioWorldPropertyNodeSocket', "Density")

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Density"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioDensityNode)

class pbrAudioTemperatureNode(Node):
    """Acoustic temperature properties node"""
    bl_idname = 'pbrAudioTemperatureNode'
    bl_label = "Acoustic Temperature Parameters"

    def init(self, context):
        self.outputs.new('pbrAudioWorldPropertyNodeSocket', "Temperature in Celsius degree")

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Temperature"

    def update(self):
        pass

    def free(self):
        pass

classes.append(pbrAudioTemperatureNode)

class pbrAudioEnvironmentNode(Node):
    """pbrAudio environment node"""
    bl_idname = 'pbrAudioEnvironmentNode'
    bl_label = "Environment"

    ambisonic_file: StringProperty(
        name="Audio File",
        description="Path to ambisonic file",
        subtype='FILE_PATH' 
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
        self.outputs.new('pbrAudioWorldEnvironmentNodeSocket', text='Environment')

    def draw_buttons(self, context, layout):
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
