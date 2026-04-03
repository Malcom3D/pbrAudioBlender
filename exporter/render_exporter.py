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
import trimesh
import sys, os, json
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion

class RenderExporter:
    def __init__(self, scene: bpy.types.Scene, decimals: int = 18):
        np.set_printoptions(precision=decimals, floatmode='fixed', threshold=np.inf)
        self.decimals = decimals
        self.scene = bpy.context.scene
        self.scale_factor = 1.0  # Blender units to meters
        self.export_path = f"{scene.pbraudio.cache_path}/AcousticDomain"
        os.makedirs(self.export_path, exist_ok=True)

        system = {}
        system["sample_rate"] = self.scene.pbraudio.sample_rate
        system["bit_depth"] = self.scene.pbraudio.bit_depth.replace('BIT', '')
        system["file_format"] = self.scene.pbraudio.file_format
        system["fps"] = self.scene.render.fps
        system["fps_base"] = self.scene.render.fps_base
        system["subframes"] = 1
        system["cache_path"] = self.export_path

        self.config = {}
        self.config["system"] = system

        self.not_valid = []
        self.obj_idx = 0
        self.src_idx = 0
        self.output_idx = 0

    def domain_config(self):
        domain_config = {}
        # find world domain property
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                if hasattr(world.pbraudio, 'acoustic_domain'):
                    acoustic_domain = world.pbraudio.acoustic_domain
                    acoustic_domain['name'] = world.pbraudio.acoustic_domain.name

                    # find corner vertex of domain bounding box
                    domain_config['geometry'] = []
                    vertexs = acoustic_domain.bound_box
                    for idx in range(8):
                        domain_config['geometry'] += [[vertexs[idx][0], vertexs[idx][1], vertexs[idx][2]]]

                    # Get acoustic properties from material
                    domain_config['acoustic_shader'] = self.get_acoustic_properties_from_world()

        self.config["acoustic_domain"] = domain_config

    def wave_propagation(self):
        wave_config = {}
        # Wave propagator property
        wave_config['max_interactions'] = self.scene.pbraudiorender.max_interactions
        wave_config['bands_per_octave'] = self.scene.pbraudiorender.bands_per_octave
        wave_config['enable_interface'] = self.scene.pbraudiorender.enable_interface
        wave_config['enable_resonance'] = self.scene.pbraudiorender.enable_resonance
        wave_config['enable_termination'] = self.scene.pbraudiorender.enable_termination
        wave_config['use_dispersion_correction'] = self.scene.pbraudiorender.use_dispersion_correction
        if wave_config['use_dispersion_correction']:
            wave_config['dispersion_order'] = self.scene.pbraudiorender.use_dispersion_correction
        wave_config['use_extended_reaction'] = self.scene.pbraudiorender.use_extended_reaction
        if wave_config['use_extended_reaction']:
            wave_config['max_modal_reaction'] = self.scene.pbraudiorender.max_modal_reaction
        wave_config['use_complex_eigenray'] = self.scene.pbraudiorender.use_complex_eigenray
        if wave_config['use_complex_eigenray']:
            wave_config['max_complex_eigenray'] = self.scene.pbraudiorender.max_complex_eigenray

        self.config["wave_propagation"] = wave_config

    def interface_config(self):
        # Interface manager property
        interface_config = {}
        if self.scene.pbraudiorender.enable_interface:
            interface_config["enable_absorption"] = self.scene.pbraudiorender.enable_absorption
            interface_config["enable_reflection"] = self.scene.pbraudiorender.enable_reflection
            if interface_config["enable_reflection"]:
                interface_config["max_reflection"] = self.scene.pbraudiorender.max_reflection
            interface_config["enable_scattering"] = self.scene.pbraudiorender.enable_scattering
            if interface_config["enable_scattering"]:
                interface_config["max_scattering"] = self.scene.pbraudiorender.max_scattering
            interface_config["enable_refraction"] = self.scene.pbraudiorender.enable_refraction
            if interface_config["enable_refraction"]:
                interface_config["max_refraction"] = self.scene.pbraudiorender.max_refraction
            interface_config["enable_diffraction"] = self.scene.pbraudiorender.enable_diffraction
            if interface_config["enable_diffraction"]:
                interface_config["max_diffraction"] = self.scene.pbraudiorender.max_diffraction
            interface_config["min_impedance_ratio"] = self.scene.pbraudiorender.min_impedance_ratio
            interface_config["max_impedance_ratio"] = self.scene.pbraudiorender.max_impedance_ratio

        self.config["interface"] = interface_config

    def resonance_config(self):
        # Resonance manager property
        resonance_config = {}
        if self.scene.pbraudiorender.enable_resonance:
            resonance_config["max_resonance_structure"] = self.scene.pbraudiorender.max_resonance_structure
            resonance_config["resonance_threshold"] = self.scene.pbraudiorender.resonance_threshold
            resonance_config["enable_helmholtz"] = self.scene.pbraudiorender.enable_helmholtz
            if resonance_config["enable_helmholtz"]:
                resonance_config["min_cavity_volume"] = self.scene.pbraudiorender.min_cavity_volume
                resonance_config["max_resonance_room_modes"] = self.scene.pbraudiorender.max_resonance_room_modes
            resonance_config["enable_parallel_wall"] = self.scene.pbraudiorender.enable_parallel_wall
            if resonance_config["enable_parallel_wall"]:
                resonance_config["min_wall_distance"] = self.scene.pbraudiorender.min_wall_distance
                resonance_config["max_wall_distance"] = self.scene.pbraudiorender.max_wall_distance
            resonance_config["enable_tube"] = self.scene.pbraudiorender.enable_tube
            if resonance_config["enable_tube"]:
                resonance_config["min_tube_length"] = self.scene.pbraudiorender.min_tube_length
                resonance_config["min_tube_aspect_ratio"] = self.scene.pbraudiorender.min_tube_aspect_ratio

        self.config["resonance"] = resonance_config

    def termination_config(self):
        # Termination settings
        termination_config = {}
        if self.scene.pbraudiorender.enable_termination:
            termination_config["termination_type"] = self.scene.pbraudiorender.termination_type
            if termination_config["termination_type"] == 'SAMPLE_END':
                termination_config["samples_after"] = self.scene.pbraudiorender.samples_after
                termination_config["min_active_sources"] = self.scene.pbraudiorender.min_active_sources
            if termination_config["termination_type"] == 'REVERBERATION_TIME':
                termination_config["max_reverberation_time"] = self.scene.pbraudiorender.max_reverberation_time
            if termination_config["termination_type"] == 'ENERGY_THRESHOLD':
                termination_config["max_energy_threshold"] = self.scene.pbraudiorender.max_energy_threshold
                termination_config["min_energy_threshold"] = self.scene.pbraudiorender.min_energy_threshold
        else:
            termination_config["termination_type"] = 'FINAL_FRAME'

        self.config["termination"] = termination_config

    def get_from_previous(self, node):
        acoustic_dict = {}
        # get inputs
        links = node.inputs.keys()
        for link in links:
            if node.inputs[link].is_linked:
                previous_acoustic_dict = self.get_from_previous(node.inputs[link].links[0].from_node)
                pbraudio_node_type = previous_acoustic_dict['type']
                del previous_acoustic_dict['type']
                if pbraudio_node_type == 'WorldMedium':
                    acoustic_dict['acoustic_shader'] = previous_acoustic_dict
                elif pbraudio_node_type == 'AcousticShader':
                    acoustic_dict['acoustic_shader'] = previous_acoustic_dict
                elif pbraudio_node_type == 'AcousticProperties':
                    acoustic_dict['acoustic_properties'] = previous_acoustic_dict
#                elif pbraudio_node_type == 'CoefficientResponse':     ########### Not implemented: return 2 list? frequencies + coefficients?
#                    acoustic_dict[link] = previous_acoustic_dict     ########### Not implemented
#                #TBD: freq_response, calibration_file, spatial_freq_response, spatial_freq_response_file, spatial_arrangement_file

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

    def get_acoustic_properties_from_world(self):
        """Get acoustic properties from the acoustic world node chain"""

        # ADD DEFAULT VALUE IF OBJECT HAVE NO MATERIAL
        acoustic_shader = []
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                if hasattr(world.pbraudio, 'nodetree'):
                nodetree = world.pbraudio.nodetree
                for key in nodetree.nodes.keys():
                    if nodetree.nodes[key].pbraudio_type == 'WorldOutput'
                        output_node = nodetree.nodes[key]
                        acoustic_shader = self.get_from_previous(output_node)

        return acoustic_shader

    def get_acoustic_properties_from_material(self, obj):
        """Get acoustic properties from the acoustic material node chain"""

        # ADD DEFAULT VALUE IF OBJECT HAVE NO MATERIAL
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
            print('watertight: ', quest_mesh.is_watertight)
            print('volume: ', quest_mesh.is_volume)
            self.not_valid.append(name)
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

            for frame in range(start_frame, end_frame + 1):
                scene.frame_float = frame
                bpy.context.view_layer.update()
#                print(f"Exporting {obj.name} frame {frame} in {self.export_path}/data/{name}...")
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

        print(f"to_add: {self.to_add(name)} object: {name} not_valid: {self.not_valid}")

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
