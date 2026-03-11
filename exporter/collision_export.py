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
import numpy as np
import os, json
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion

class MeshToNumpyExporter:
    def __init__(self, scene: bpy.types.Scene, decimals: int = 18):
        np.set_printoptions(precision=decimals, floatmode='fixed', threshold=np.inf)
        self.decimals = decimals
        self.scale_factor = 1.0  # Blender units to meters
        collision_collection = scene.pbraudio.collision_collection.name_full
        self.export_path = f"{scene.pbraudio.cache_path}/{scene.pbraudio.collision_collection.name_full}"
        os.makedirs(self.export_path, exist_ok=True)
        system = {}
        system["sample_rate"] = scene.pbraudio.sample_rate
        system["bit_depth"] = scene.pbraudio.bit_depth.replace('BIT', '')
        system["fps"] = scene.render.fps
        system["fps_base"] = scene.render.fps_base
        system["subframes"] = 1
        system["collision_margin"] = scene.pbraudio.collision_margin
        system["cache_path"] = self.export_path
        self.config = {}
        self.config["system"] = system

        self.objects = []
        self.obj_idx = 0

    def get_from_previous(self, node):
        acoustic_dict = {}
        # get inputs
        links = node.inputs.keys()
        for link in links:
            if node.inputs[link].is_linked:
                previous_acoustic_dict = self.get_from_previous(node.inputs[link].links[0].from_node)
                for key in previous_acoustic_dict.keys():
                    acoustic_dict[key] = previous_acoustic_dict[key]

        for property in node.bl_rna.properties.keys():
            if property.startswith('pbraudio_'):
                node_property = "node." + property
                acoustic_value = eval(node_property)
                if 'young_modulus' in property:
                    acoustic_value *= 1E9
                elif 'poisson_ratio' in property:
                    acoustic_value *= 0.01
 
                acoustic_dict[property.replace('pbraudio_', '')] = acoustic_value

        return acoustic_dict

    def get_acoustic_properties_from_material(self, obj):
        """Get acoustic properties from the acoustic material node chain"""

        nodetree = obj.pbraudio.nodetree
        output_node = nodetree.nodes['Material Output']

        acoustic_shader = self.get_from_previous(output_node)
                    
        return acoustic_shader

    def triangulate_mesh(self, mesh):
        """Triangulate the mesh using bmesh"""
        import bmesh
        
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        bm.free()
        mesh.corner_normals
        
    def get_world_matrix(self, obj):
        """Get world matrix including rotation and location"""
        return obj.matrix_world

    def export_pose(self, obj, frame_number):
        """Export mesh data for a single frame"""
        # Set current frame
        bpy.context.scene.frame_set(frame_number)
        
        # Get evaluated object (for modifiers and animation)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        
        # Triangulate if needed
        if len(mesh.polygons) > 0 and any(len(p.vertices) > 3 for p in mesh.polygons):
            self.triangulate_mesh(mesh)
        
        # Get world matrix
        world_matrix = self.get_world_matrix(eval_obj)
                
        # Get center position and rotation
        location = list([world_matrix.translation.x * self.scale_factor, world_matrix.translation.y * self.scale_factor, world_matrix.translation.z * self.scale_factor])

        # Extract rotation matrix (3x3)
        rotation = list([eval_obj.rotation_euler.x, eval_obj.rotation_euler.y, eval_obj.rotation_euler.z])
        
        # Clean up
        eval_obj.to_mesh_clear()
        
        return {
            'location': location,
            'rotation': rotation,
        }
    
    def export_frame(self, obj, frame_number):
        """Export mesh data for a single frame"""
        # Set current frame
        bpy.context.scene.frame_set(frame_number)
        
        # Get evaluated object (for modifiers and animation)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        
        # Triangulate if needed
        if len(mesh.polygons) > 0 and any(len(p.vertices) > 3 for p in mesh.polygons):
            self.triangulate_mesh(mesh)
        
        # Get world matrix
        world_matrix = self.get_world_matrix(eval_obj)
        
        # Get vertices in world coordinates (meters)
        vertices = np.zeros((len(mesh.vertices), 3), dtype=np.float32)
        for i, vert in enumerate(mesh.vertices):
            world_co = world_matrix @ vert.co
            vertices[i] = [world_co.x * self.scale_factor, 
                          world_co.y * self.scale_factor, 
                          world_co.z * self.scale_factor]
        
        # Get vertex normals in world space
        normals = np.zeros((len(mesh.vertices), 3), dtype=np.float32)
        mesh.corner_normals
        for i, vert in enumerate(mesh.vertices):
            normals[i] = world_matrix.to_3x3() @ vert.normal

        # Get faces (triangles)
        faces = []
        for poly in mesh.polygons:
            if len(poly.vertices) == 3:
                faces.append(poly.vertices)
            elif len(poly.vertices) > 3:
                # Should already be triangulated, but handle just in case
                for i in range(1, len(poly.vertices) - 1):
                    faces.append([poly.vertices[0], poly.vertices[i], poly.vertices[i + 1]])
        
        faces = np.array(faces, dtype=np.int32) if faces else np.zeros((0, 3), dtype=np.int32)

        # Clean up
        eval_obj.to_mesh_clear()
        
        # Round to specified decimals
        if self.decimals is not None:
            vertices = np.round(vertices, self.decimals)
            normals = np.round(normals, self.decimals)

        return {
            'vertices': vertices,
            'normals': normals,
            'faces': faces,
        }
    
    def export_animation(self, obj, start_frame=None, end_frame=None):
        """Export animation sequence"""

        obj.select_set(True)
        name = obj.name_full.replace('.', '_')
        
        os.makedirs(f"{self.export_path}/data/pose", exist_ok=True)
        os.makedirs(f"{self.export_path}/data/{name}", exist_ok=True)
        scene = bpy.context.scene

        if start_frame is None:
            start_frame = scene.frame_current
        if end_frame is None:
            end_frame = start_frame
        
        frame_data = {}
        location, rotation = ([] for _ in range(2))
        total_frames = 0
        for frame in range(start_frame, end_frame + 1):
            scene.frame_float = frame
            bpy.context.view_layer.update()
            frame_result = self.export_pose(obj, frame)
            location.append(frame_result['location'])
            rotation.append(frame_result['rotation'])

        location = np.round(np.array(location), self.decimals)
        rotation = np.round(np.array(rotation), self.decimals)
        output_pose = os.path.join(self.export_path, f"data/pose/{name}.npz")

        object = {}
        object["idx"] = self.obj_idx
        object["name"] = name
        object["obj_path"] = f"{self.export_path}/data/{name}"
        object["pose_path"] = f"{self.export_path}/data/pose"

        # verify is not static
        if not np.all(location == location[0]) or not np.all(rotation == rotation[0]):
            object["static"] = False
            print(f"{obj.name} is not static...")
            print(f"Exporting pose for {obj.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location, rotation=rotation)

            for frame in range(start_frame, end_frame + 1):
                scene.frame_float = frame
                bpy.context.view_layer.update()
                print(f"Exporting {obj.name} frame {frame} in {self.export_path}/data/{name}...")
                frame_result = self.export_frame(obj, frame)
            
                # Store each component separately for easy access
                frame_data[f'vertices'] = frame_result['vertices']
                frame_data[f'normals'] = frame_result['normals']
                frame_data[f'faces'] = frame_result['faces']

                # Save to npz
                output_file = os.path.join(self.export_path, f"data/{name}/{name}_{frame:05d}.npz")
                np.savez_compressed(output_file, **frame_data)
        else:
            object["static"] = True
            print(f"{obj.name} is static...")
            print(f"Exporting pose for {obj.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location[0], rotation=rotation[0])            
            print(f"Exporting {obj.name} in {self.export_path}/data/{name}...")
            frame_result = self.export_frame(obj, start_frame)

            # Store each component separately for easy access
            frame_data[f'vertices'] = frame_result['vertices']
            frame_data[f'normals'] = frame_result['normals']
            frame_data[f'faces'] = frame_result['faces']

            # Save to npz
            output_file = os.path.join(self.export_path, f"data/{name}/{name}.npz")
            np.savez_compressed(output_file, **frame_data)

        object["stochastic_variation"] = obj.pbraudio.stochastic_variation
        object["ground"] = obj.pbraudio.ground

        connected = []
        for item in obj.pbraudio_connected.values():
            connected.append([item.connected_object.replace('.', '_'), item.connected_value/10])
        if len(connected) == 0:
            connected = False
        object["connected"] = connected

        # Get acoustic properties from material
        acoustic_shader = self.get_acoustic_properties_from_material(obj)

        object["acoustic_shader"] = acoustic_shader

        self.objects.append(object)
        self.obj_idx += 1

        obj.select_set(False)            


    def save_config(self):
        # replace object name with idx in connected
        for obj_idx in range(len(self.objects)):
            connected = self.objects[obj_idx]["connected"]
            if not isinstance(connected, bool):
                for conn_idx in range(len(connected)):
                    name = connected[conn_idx][0]
                    for item in self.objects:
                        if item["name"] == name:
                            connected[conn_idx][0] = item["idx"]

        # add objects to config
        self.config["objects"] = self.objects

        # create config file
        config_file = f"{self.export_path}/config.json"
        js = json.dumps(self.config, indent=2, separators=(',', ': '))
        with open(config_file, 'w+') as json_file:
            json_file.write(js)
