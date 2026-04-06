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
from bpy.types import Panel
from bpy.app.translations import contexts as i18n_contexts
from bpy.props import FloatProperty

classes = []

class DataButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'EMPTY')

class PBRAUDIO_PT_empty(Panel):
    bl_label = "Empty"
    bl_idname = 'PBRAUDIO_PT_empty'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    bl_translation_context = i18n_contexts.id_id

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'EMPTY' and not hasattr(context.active_object, 'pbraudio')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        ob = context.object

        layout.prop(ob, "empty_display_type", text="Display As")
        layout.prop(ob, "empty_display_size", text="Size")

        if ob.empty_display_type == 'IMAGE':
            col = layout.column(align=True)
            col.prop(ob, "empty_image_offset", text="Offset X", index=0)
            col.prop(ob, "empty_image_offset", text="Y", index=1)

            col = layout.column()
            depth_row = col.row()
            depth_row.enabled = not ob.show_in_front
            depth_row.prop(ob, "empty_image_depth", text="Depth", expand=True)
            col.row().prop(ob, "empty_image_side", text="Side", expand=True)

            col = layout.column(heading="Show In", align=True)
            col.prop(ob, "show_empty_image_orthographic", text="Orthographic")
            col.prop(ob, "show_empty_image_perspective", text="Perspective")
            col.prop(ob, "show_empty_image_only_axis_aligned", text="Only Axis Aligned")

            col = layout.column(align=False, heading="Opacity")
            col.use_property_decorate = False
            row = col.row(align=True)
            sub = row.row(align=True)
            sub.prop(ob, "use_empty_image_alpha", text="")
            sub = sub.row(align=True)
            sub.active = ob.use_empty_image_alpha
            sub.prop(ob, "color", text="", index=3, slider=True)
            row.prop_decorator(ob, "color", index=3)

classes.append(PBRAUDIO_PT_empty)

class PBRAUDIO_PT_data_panel(Panel):
    """Panel for pbrAudio sound I/O settings"""
    bl_label = 'Sound I/O'
    bl_idname = 'PBRAUDIO_PT_data_panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    width: FloatProperty(
        name="Width",
        description="Width of the planar source",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )

    height: FloatProperty(
        name="Height",
        description="Height of the planar source",
        default=0.5,
        min=0.01,
        max=100.0,
        unit='LENGTH'
    )
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO' and context.active_object.type == 'EMPTY' or context.active_object.type == 'CAMERA' and hasattr(context.active_object, 'pbraudio')

    def draw(self, context):
        layout = self.layout
        object = context.object
        snode = object.pbraudio

        if not object.pbraudio.output and object.type == 'EMPTY':
            # Object is a Sound Source
#            layout.prop(object.pbraudio, "source_type")
            layout.label(object.pbraudio.source_type)
            # use gizmo shape - text editor -> templates -> gizmo_custom_geometry
            if object.pbraudio.source and object.pbraudio.source_type == 'SPHERE':
#                object.empty_display_type = 'SPHERE'
                layout.prop(object, "empty_display_size")
            elif object.pbraudio.source and object.pbraudio.source_type == 'PLANE':
#                object.empty_display_type = 'CUBE'
                layout.prop(self, "width")
                layout.prop(self, "height")
                object.empty_display_size = max(self.width, self.height) / 2
                object.scale = (self.width / 2, self.height / 2, 0.01)
            layout.template_ID(snode, "source", new="sound.open_mono")
        else:
            # Object is a Sound Output
            layout.prop(object.pbraudio, "output_type")
            if object.pbraudio.output_type == 'AMBI':
                layout.prop(object.pbraudio, "ambisonic_order")

classes.append(PBRAUDIO_PT_data_panel)
