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

import os
import sys
import json
import bpy
import numpy as np
import trimesh
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion

from ..utils import frd_io

class CollisionExporter:
    def __init__(self, scene: bpy.types.Scene, decimals: int = 18):
        np.set_printoptions(precision=decimals, floatmode='fixed', threshold=np.inf)
        self.decimals = decimals
        self.scale_factor = 1.0  # Blender units to meters
        collision_collection = scene.pbraudio.collision_collection.name_full
        export_path = f"{scene.pbraudio.cache_path}"
        if export_path.startswith('//'):
            export_path = f"{bpy.path.abspath(export_path)}"
        os.makedirs(export_path, exist_ok=True)
        self.export_path = f"{export_path}/{scene.pbraudio.collision_collection.name_full}"
        os.makedirs(self.export_path, exist_ok=True)
        system = {}
        system["sample_rate"] = scene.pbraudio.sample_rate
        system["bit_depth"] = scene.pbraudio.bit_depth.replace('BIT', '')
        system["file_format"] = scene.pbraudio.file_format
        system["fps"] = scene.render.fps
        system["fps_base"] = scene.render.fps_base
        system["subframes"] = 1
        system["modal_modes"] = scene.pbraudio.modal_modes
        system["collision_margin"] = scene.pbraudio.collision_margin
        system["cache_path"] = self.export_path
        self.config = {}
        self.config["system"] = system

        self.objects = []
        self.not_valid = []
        self.obj_idx = 0

    def get_from_previous(self, node):
        scene = bpy.context.scene
        pbraudiorender = bpy.context.scene.pbraudiorender
        bands_per_octave = pbraudiorender.bands_per_octave 
        if pbraudiorender.enable_frequencies_range_set:
            freq_min = pbraudiorender.lowest_frequency
            freq_max = pbraudiorender.higher_frequency
        else:
            freq_min = 5
            freq_max = scene.pbraudio.sample_rate / 2

        acoustic_dict = {}
        # get inputs
        inputs = node.inputs.keys()
        for in_idx in inputs:
            if node.inputs[in_idx].is_linked:
                previous_acoustic_dict = self.get_from_previous(node.inputs[in_idx].links[0].from_node)
                if previous_acoustic_dict['type'] == 'AcousticShader':
                    acoustic_dict = {**acoustic_dict, **previous_acoustic_dict}
#                elif previous_acoustic_dict['type'] == 'AcousticProperties':
#                    acoustic_dict['acoustic_properties'] = previous_acoustic_dict
#                elif previous_acoustic_dict['type'] == 'FrequencyResponse':
#                    quantity_type = 'magnitude'
#                    if in_idx in ['absorption', 'refraction', 'reflection', 'scattering']:
#                        quantity_type = 'coefficients'
#                    desired_points, _ = frd_io.generate_bands(freq_min, freq_max, bands_per_octave)
#                    freq_resp_file = previous_acoustic_dict['response_filepath']
#                    if os.path.exists(freq_resp_file):
#                        freqs, mags, phases = frd_io.parse_frd_file(freq_resp_file)
#                        acoustic_dict[in_idx] = {"frequencies": freqs.tolist(), quantity_type: mags.tolist(), 'phases': phases.tolist()}
#
#            elif not node.inputs[in_idx].is_linked:
#                if node.pbraudio_type == 'AcousticProperties':
#                    quantity_type = 'magnitude'
#                    if in_idx in ['absorption', 'refraction', 'reflection', 'scattering']:
#                        quantity_type = 'coefficients'
#                    delta_f = (freq_max - freq_min)/4
#                    freqs = [freq_min, freq_min + delta_f, freq_min + 2*delta_f, freq_max - delta_f, freq_max]
#                    mag = node.inputs[in_idx].default_value
#                    mags = [mag for _ in range(5)]
#                    phases = []
#                    acoustic_dict[in_idx] = {"frequencies": freqs, quantity_type: mags, 'phases': phases}

        for property in node.bl_rna.properties.keys():
            if property.startswith('pbraudio_'):
                node_property = "node." + property
                acoustic_value = eval(node_property)
                if 'young_modulus' in property:
                    acoustic_value *= 1E9
                elif 'damping' in property:
                    acoustic_value *= 0.01
                acoustic_dict[property.replace('pbraudio_', '')] = acoustic_value

        return acoustic_dict

    def get_acoustic_properties_from_material(self, obj):
        """Get acoustic properties from the acoustic material node chain"""

        # ADD DEFAULT VALUE IF OBJECT HAVE NO MATERIAL
        acoustic_shader = {}

        nodetree = obj.pbraudio.nodetree
        for key in nodetree.nodes.keys():
            if nodetree.nodes[key].pbraudio_type == 'MaterialOutput':
                output_node = nodetree.nodes[key]
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
#        mesh = obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        
        # Triangulate if needed
        if len(mesh.polygons) > 0 and any(len(p.vertices) > 3 for p in mesh.polygons):
            self.triangulate_mesh(mesh)
        
        # Get world matrix
        world_matrix = self.get_world_matrix(eval_obj)
#        world_matrix = self.get_world_matrix(obj)
                
        # Get center position and rotation
        location = list([world_matrix.translation.x * self.scale_factor, world_matrix.translation.y * self.scale_factor, world_matrix.translation.z * self.scale_factor])

        # Extract rotation matrix (3x3)
        rotation = list([eval_obj.rotation_euler.x, eval_obj.rotation_euler.y, eval_obj.rotation_euler.z])
#        rotation = list([obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z])
        
        # Extract fracture data
        fractured = False
        if hasattr(obj.animation_data, 'action'):
            action_name = obj.animation_data.action.name
            for action in bpy.data.actions[action_name].fcurves.values():
                if 'fractured' in action.data_path:
                    for keyframe in action.keyframe_points:
                        if keyframe.co[1] == 1:
                            fractured = keyframe.co[0]

        # Clean up
        eval_obj.to_mesh_clear()
#        obj.to_mesh_clear()
        
        return {
            'location': location,
            'rotation': rotation,
            'fractured': fractured
        }
    
    def export_frame(self, obj, frame_number):
        """Export mesh data for a single frame"""
        # Set current frame
        bpy.context.scene.frame_set(frame_number)
        
        # Get evaluated object (for modifiers and animation)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
#        mesh = obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        
        # Triangulate if needed
        if len(mesh.polygons) > 0 and any(len(p.vertices) > 3 for p in mesh.polygons):
            self.triangulate_mesh(mesh)
        
        # Get world matrix
        world_matrix = self.get_world_matrix(eval_obj)
#        world_matrix = self.get_world_matrix(obj)
        
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
#        obj.to_mesh_clear()
        
        # Round to specified decimals
        if self.decimals is not None:
            vertices = np.round(vertices, self.decimals)
            normals = np.round(normals, self.decimals)

        name = obj.name_full.replace('.', '_')
        quest_mesh = trimesh.Trimesh(vertices=vertices, vertex_normals=normals, faces=faces)
        if not quest_mesh.is_watertight or not quest_mesh.is_volume and self.to_add(name):
            self.not_valid.append(name)
#            print('watertight: ', quest_mesh.is_watertight)
#            print('volume: ', quest_mesh.is_volume)
#            print(f"Warming: {obj.name} is not manifold/watertight.")
#            print(f"Warming: trying to fix {obj.name} manifold/watertight.")
#            quest_mesh.fill_holes()
#            if not quest_mesh.is_watertight and not quest_mesh.is_volume:
#                print(f"ERROR: cannot fix manifold/watertight of {obj.name}.")
#                print(f"ERROR: please try with Select -> Select All by trait -> Non Manifold, and then Mesh -> Merge -> By Distance.")
#                self.not_valid.append(obj.name_full.replace('.', '_'))

        return {
            'vertices': vertices,
            'normals': normals,
            'faces': faces,
        }

    def to_add(self, name):
        # do not add if obj.name is in self.not_valid
        to_be_added = True
        for nv_idx in range(len(self.not_valid)):
            if name == self.not_valid[nv_idx]:
                to_be_added = False
        return to_be_added
    
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
        fractured = False
        location, rotation = ([] for _ in range(2))
        total_frames = 0
        for frame in range(start_frame, end_frame + 1):
            scene.frame_float = frame
            bpy.context.view_layer.update()
            frame_result = self.export_pose(obj, frame)
            location.append(frame_result['location'])
            rotation.append(frame_result['rotation'])

            if not frame_result['fractured'] == False:
                fractured = frame_result['fractured']

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
#            print(f"Exporting pose for {obj.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location, rotation=rotation)

            print(f"Exporting {obj.name} in {self.export_path}/data/{name}...")
            for frame in range(start_frame, end_frame + 1):
                scene.frame_float = frame
                bpy.context.view_layer.update()
                frame_result = self.export_frame(obj, frame)
            
                # Store each component separately for easy access
                frame_data['vertices'] = frame_result['vertices']
                frame_data['normals'] = frame_result['normals']
                frame_data['faces'] = frame_result['faces']

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

        object["resonance"] = obj.pbraudio.resonance
        object["resonance_modes"] = obj.pbraudio.resonance_modes

        connected = []
        if obj.pbraudio.connected:
            for item in obj.pbraudio_connected.values():
                connected.append([item.connected_object.replace('.', '_'), item.connected_value/10])
        if len(connected) == 0:
            connected = False
        object["connected"] = connected

        object['is_shard'] = False
        object['fractured'] = fractured
        shard = []
        if not fractured == False:
            for item in obj.pbraudio_shard.values():
                shard.append(item.shard_object.replace('.', '_'))
        if len(shard) == 0:
            shard = False
        object["shard"] = shard

        # Get acoustic properties from material
        acoustic_shader = self.get_acoustic_properties_from_material(obj)

        object["acoustic_shader"] = acoustic_shader

#        print(f"to_add: {self.to_add(name)} object: {name} not_valid: {self.not_valid}")

        if self.to_add(name):
            self.objects.append(object)
            self.obj_idx += 1
        obj.select_set(False)            

    def save_config(self):
        # remove invalid objects and replace object name with idx in connected
        for obj_idx in range(len(self.objects)):
            connected = self.objects[obj_idx]["connected"]
            if not isinstance(connected, bool):
                for not_valid in self.not_valid:
                    for conn_idx in range(len(connected)):
                        if not_valid == connected[conn_idx][0]:
                            connected.remove(not_valid)
                            break
                for conn_idx in range(len(connected)):
                    name = connected[conn_idx][0]
                    for item in self.objects:
                        if item["name"] == name:
                            connected[conn_idx][0] = item["idx"]

        # remove invalid objects and replace object name with idx in shard
        for obj_idx in range(len(self.objects)):
            shard = self.objects[obj_idx]["shard"]
            if not isinstance(shard, bool):
                for not_valid in self.not_valid:
                    for shard_idx in range(len(shard)):
                        if not_valid == shard[shard_idx]:
                            shard.remove(not_valid)
                            break
                for shard_idx in range(len(shard)):
                    name = shard[shard_idx]
                    for item in self.objects:
                        if item["name"] == name:
                            shard[shard_idx] = item["idx"]
                            # write fracture frame to is_shard
                            item["is_shard"] = self.objects[obj_idx]["fractured"]

        # add objects to config
        self.config["objects"] = self.objects

        # create config file
        config_file = f"{self.export_path}/config.json"
        js = json.dumps(self.config, indent=2, separators=(',', ': '))
        with open(config_file, 'w+') as json_file:
            json_file.write(js)
