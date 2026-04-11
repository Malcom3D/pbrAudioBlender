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
from bpy.types import Panel, Operator
from bpy.app.translations import contexts as i18n_contexts
from bpy.props import FloatProperty

from ..utils.common import update_boundary_positions, get_acoustic_domain_bounds, is_point_inside_domain

classes = []

#class DataButtonsPanel:
#    bl_space_type = 'PROPERTIES'
#    bl_region_type = 'WINDOW'
#    bl_context = "data"
#
#    @classmethod
#    def poll(cls, context):
#        ob = context.object
#        return (ob and ob.type == 'EMPTY')

class PBRAUDIO_PT_empty(Panel):
    bl_label = "Empty"
    bl_idname = 'PBRAUDIO_PT_empty'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    bl_translation_context = i18n_contexts.id_id

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'EMPTY' and not context.active_object.type == 'CAMERA' and not context.active_object.pbraudio.source and not context.active_object.pbraudio.output

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

    @classmethod
    def poll(cls, context):
        return (context.scene.render.engine == 'PBRAUDIO' and context.active_object is not None and
               (context.active_object.type == 'EMPTY' or context.active_object.type == 'CAMERA') and
                hasattr(context.active_object, 'pbraudio') and (context.active_object.pbraudio.source or context.active_object.pbraudio.output or context.active_object.pbraudio.environment or context.active_object.type == 'CAMERA'))

    def draw(self, context):
        layout = self.layout
        object = context.object
        snode = object.pbraudio

        if object.type == 'CAMERA':
            layout.prop(object.pbraudio, "output")

        if object.pbraudio.source:
            # Object is a Sound Source
            layout.label(text="Source Settings:", icon='SPEAKER')
            layout.prop(object.pbraudio, "source_type")
            if object.pbraudio.source_type == 'SPHERE':
                layout.prop(object.pbraudio, "source_sphere_size")
#                bpy.ops.object.pbraudio_resize_source(size=object.pbraudio.source_sphere_size)
#                op.size = object.pbraudio.source_sphere_size
#                object.empty_display_size = object.pbraudio.source_sphere_size
            elif object.pbraudio.source_type == 'PLANE':
                layout.prop(object.pbraudio, "source_planar_width")
                layout.prop(object.pbraudio, "source_planar_height")
#                bpy.ops.object.pbraudio_resize_source(height=object.pbraudio.source_planar_height, width=object.pbraudio.source_planar_width)
#                op.height = object.pbraudio.source_planar_height
#                op.width = object.pbraudio.source_planar_width
#                object.empty_display_size = max(object.pbraudio.source_planar_width, object.pbraudio.source_planar_height) / 2
#                object.scale = (object.pbraudio.source_planar_width / 2, object.pbraudio.source_planar_height / 2, 0.01)
            layout.prop(snode, "source_file", text="Sound File")
            
        elif object.pbraudio.environment:
            # Object is a World Environment
#            box = layout.box()
#            box.label(text="Environment Settings:", icon='WORLD')
            layout.label(text="Environment Settings:", icon='ORIENTATION_GIMBAL')
            
#            # Environment properties
#            row = box.row()
#            row.prop(snode, "environment_size", text="Radius")
#            row.prop(snode, "environment_chanels", text="Channels")
            layout.prop(snode, "environment_size", text="Radius")
            layout.prop(snode, "environment_chanels", text="Channels")
            
            # File path
#            box.prop(snode, "environment_file", text="Sound File")
            layout.prop(snode, "environment_file", text="Ambisonic File")
            
#            # Boundary management
#            box.separator()
#            box.label(text="Boundary Management:", icon='ORIENTATION_GIMBAL')
            
#            # Show boundary count
#            if "pbraudio_boundary_empties" in object:
#                boundary_count = len(object["pbraudio_boundary_empties"])
#                box.label(text=f"Boundaries: {boundary_count}")
            
#            # Update button
#            row = box.row()
#            row.operator("object.pbraudio_update_environment_boundaries", 
#                        text="Update Boundaries", 
#                        icon='FILE_REFRESH')
#            layout.prop(snode, "environment_dynamic_boundaries_update", text="Dynamic Boundaries Update")
            row_update = layout.row()
            row_update.operator("object.pbraudio_update_environment_boundaries", text="Update Boundaries", icon='FILE_REFRESH')
#            if snode.environment_dynamic_boundaries_update:
#                row_update.enabled = False
            
            # Show warning if boundaries might be outside domain
#            from ..operators.soundOT import PBRAUDIO_OT_add_world_environment
#            op = PBRAUDIO_OT_add_world_environment()
#            op = bpy.ops.object.pbraudio_add_world_environment
#            min_co, max_co = op.get_acoustic_domain_bounds()
#            min_co, max_co = PBRAUDIO_OT_add_world_environment.get_acoustic_domain_bounds()
            min_co, max_co = get_acoustic_domain_bounds()
            
            if min_co is not None and max_co is not None:
                # Check if any boundary might be outside
                if "pbraudio_boundary_empties" in object:
                    boundary_names = object["pbraudio_boundary_empties"]
                    for name in boundary_names:
                        boundary_obj = bpy.data.objects.get(name)
#                        if boundary_obj and not op.is_point_inside_domain(boundary_obj.location):
#                        if boundary_obj and not PBRAUDIO_OT_add_world_environment.is_point_inside_domain(boundary_obj.location):
                        if boundary_obj and not is_point_inside_domain(boundary_obj.location):
#                            box.label(text="Some boundaries outside domain!", icon='ERROR')
                            layout.label(text="Some boundaries outside domain!", icon='ERROR')
                            break
           
        elif object.pbraudio.output:
            # Object is a Sound Output
            layout.label(text="Output Settings:", icon='LIGHT_SPOT')
            layout.prop(object.pbraudio, "output_type")
            if object.pbraudio.output_type == 'AMBI':
                layout.prop(object.pbraudio, "ambisonic_order")
                layout.prop(object.pbraudio, "spatial_arrangement_file", text="Mics Spatial Arrangement File")
            elif object.pbraudio.output_type == 'MONO':
                layout.prop(object.pbraudio, "mono_mic_type")
                layout.prop(object.pbraudio, "output_cal_file", text="Microphone Calibration File")
            layout.prop(object.pbraudio, "output_size")

classes.append(PBRAUDIO_PT_data_panel)

#class PBRAUDIO_PT_data_panel(Panel):
#    """Panel for pbrAudio sound I/O settings"""
#    bl_label = 'Sound I/O'
#    bl_idname = 'PBRAUDIO_PT_data_panel'
#    bl_space_type = 'PROPERTIES'
#    bl_region_type = 'WINDOW'
#    bl_context = 'data'
#
#    width: FloatProperty(
#        name="Width",
#        description="Width of the planar source",
#        default=0.5,
#        min=0.01,
#        max=100.0,
#        unit='LENGTH'
#    )
#
#    height: FloatProperty(
#        name="Height",
#        description="Height of the planar source",
#        default=0.5,
#        min=0.01,
#        max=100.0,
#        unit='LENGTH'
#    )
#    @classmethod
#    def poll(cls, context):
#        return context.scene.render.engine == 'PBRAUDIO' and context.active_object.type == 'EMPTY' or context.active_object.type == 'CAMERA' and hasattr(context.active_object, 'pbraudio') and context.active_object.pbraudio.source and context.active_object.pbraudio.output
#
#    def draw(self, context):
#        layout = self.layout
#        object = context.object
#        snode = object.pbraudio
#
#        if object.pbraudio.source and object.type == 'EMPTY':
#            # Object is a Sound Source
#            layout.prop(object.pbraudio, "source_type")
#            # use gizmo shape - text editor -> templates -> gizmo_custom_geometry
#            if object.pbraudio.source and object.pbraudio.source_type == 'SPHERE':
#                # run operator to switch from PLANE to SPHERE
###                object.empty_display_type = 'SPHERE'
#                layout.prop(object, "empty_display_size")
#            elif object.pbraudio.source and object.pbraudio.source_type == 'PLANE':
##                # run operator to switch from SPHERE to PLANE
##                object.empty_display_type = 'CUBE'
#                layout.prop(self, "width")
#                layout.prop(self, "height")
#                object.empty_display_size = max(self.width, self.height) / 2
#                object.scale = (self.width / 2, self.height / 2, 0.01)
#            layout.template_ID(snode, "source_file", new="sound.open_mono")
#        elif object.pbraudio.environment and object.type == 'EMPTY':
#            layout.prop(object.pbraudio, "environment_size")
#            layout.prop(object.pbraudio, "environment_chanels")
#            layout.prop(object.pbraudio, "environment_file")
#        elif object.pbraudio.output and object.type == 'EMPTY':
#            # Object is a Sound Output
#            layout.prop(object.pbraudio, "output_type")
#            if object.pbraudio.output_type == 'AMBI':
#                layout.prop(object.pbraudio, "ambisonic_order")
#
#classes.append(PBRAUDIO_PT_data_panel)

class PBRAUDIO_OT_update_environment_boundaries(Operator):
    """Update environment boundaries"""
    bl_idname = "object.pbraudio_update_environment_boundaries"
    bl_label = "Update Boundaries"
    bl_description = "Update boundary positions for environment"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        if obj and obj.pbraudio.environment:
            # Get boundary empties
            if "pbraudio_boundary_empties" in obj:
                boundary_names = obj["pbraudio_boundary_empties"]
                boundary_empties = []
                
                for name in boundary_names:
                    boundary_obj = bpy.data.objects.get(name)
                    if boundary_obj:
                        boundary_empties.append(boundary_obj)
                
                if boundary_empties:
                    # Import and use the update function
#                    from ..operators.soundOT import PBRAUDIO_OT_add_world_environment
#                    op = PBRAUDIO_OT_add_world_environment
#                    op = bpy.ops.object.pbraudio_add_world_environment
                    radius = obj.pbraudio.environment_size
#                    op.update_boundary_positions(obj, boundary_empties, radius)
#                    PBRAUDIO_OT_add_world_environment.update_boundary_positions(obj, boundary_empties, radius)
                    update_boundary_positions(obj, boundary_empties, radius)
                    
                    self.report({'INFO'}, f"Updated {len(boundary_empties)} boundaries")
        
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_update_environment_boundaries)
