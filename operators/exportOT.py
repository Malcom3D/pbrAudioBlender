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
import os
import json
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ExportHelper

from ..exporter.collision_exporter import CollisionExporter

classes = []

class PBRAUDIO_OT_export_collision_data(Operator, ExportHelper):
    """Export collision data using CollisionExporter"""
    bl_idname = "export.pbraudio_collision_data"
    bl_label = "Export Collision Data"
    bl_description = "Export collision data for sound synthesis using CollisionExporter"
    bl_options = {'REGISTER', 'UNDO'}
    
    # ExportHelper properties
    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    # Export options
    export_frames: BoolProperty(
        name="Export All Frames",
        description="Export all frames from start to end",
        default=True,
    )
    
    start_frame: IntProperty(
        name="Start Frame",
        description="First frame to export",
        default=1,
        min=0,
    )
    
    end_frame: IntProperty(
        name="End Frame",
        description="Last frame to export",
        default=250,
        min=0,
    )
    
    export_pose_only: BoolProperty(
        name="Export Pose Only",
        description="Export only pose data (no mesh geometry)",
        default=False,
    )
    
    export_mesh_data: BoolProperty(
        name="Export Mesh Data",
        description="Export mesh geometry data",
        default=True,
    )
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        # Export options
        box = layout.box()
        box.label(text="Export Options", icon='EXPORT')
        box.prop(self, "export_frames")
        
        if self.export_frames:
            col = box.column(align=True)
            col.prop(self, "start_frame")
            col.prop(self, "end_frame")
        
        box.separator()
        box.prop(self, "export_pose_only")
        box.prop(self, "export_mesh_data")
        
        # Show warning if no collection selected
        scene = context.scene
        if not scene.pbraudio.collision_collection:
            box = layout.box()
            box.label(text="Warning: No collision collection selected!", icon='ERROR')
            box.label(text="Select a collection in Scene > PbrAudio Collision")
    
    def execute(self, context):
        scene = context.scene
        
        # Check if collision collection is selected
        if not scene.pbraudio.collision_collection:
            self.report({'ERROR'}, "No collision collection selected in Scene properties")
            return {'CANCELLED'}
        
        # Get export parameters
        decimals = 18
        
        if self.export_frames:
            start_frame = self.start_frame
            end_frame = self.end_frame
        else:
            start_frame = scene.frame_current
            end_frame = start_frame
        
        try:
            # Create exporter
            self.report({'INFO'}, "Creating CollisionExporter...")
            exporter = CollisionExporter(scene=scene, decimals=decimals)
            
            # Export each object in the collision collection
            collection = scene.pbraudio.collision_collection
            total_objects = len(collection.objects)
            
            self.report({'INFO'}, f"Exporting {total_objects} objects from collection '{collection.name}'...")
            
            for i, obj in enumerate(collection.objects):
                # Update progress
                progress = (i + 1) / total_objects
                self.report({'INFO'}, f"Exporting {obj.name} ({i+1}/{total_objects})...")
                
                # Export animation for this object
                exporter.export_animation(obj, start_frame, end_frame)
                
                # Update Blender's progress bar
                context.window_manager.progress_update(progress)
            
            # Save configuration to the specified file
            config_path = self.filepath
            
            # If no specific path, use the default cache path
            if not config_path:
                cache_path = scene.pbraudio.cache_path
                if cache_path.startswith('//'):
                    cache_path = bpy.path.abspath(cache_path)
                config_path = os.path.join(cache_path, collection.name_full, "config.json")
            
            # Save the configuration
            exporter.save_config()
            
            # Also save a copy to the specified export path if different
            if self.filepath and self.filepath != config_path:
                # Copy the config file
                import shutil
                shutil.copy2(config_path, self.filepath)
                self.report({'INFO'}, f"ConfigurationConfiguration saved to: {self.filepath}")
            
            self.report({'INFO'}, f"Successfully exported {total_objects} objects")
            self.report({'INFO'}, f"Data saved to: {exporter.export_path}")
            
            # Clear progress
            context.window_manager.progress_end()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            import traceback
            traceback.print_exc()
            context.window_manager.progress_end()
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Set default filename based on collection name
        scene = context.scene
        if scene.pbraudio.collision_collection:
            collection_name = scene.pbraudio.collision_collection.name
            self.filepath = f"{collection_name}_collision_data.json"
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

classes.append(PBRAUDIO_OT_export_collision_data)
