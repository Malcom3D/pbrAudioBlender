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
import bmesh
import numpy as np
import trimesh
import sys, os, json
from mathutils import Matrix, Vector
from bpy_extras.io_utils import axis_conversion

from ..utils import frd_io, environment_json
from ..utils.ambisonic_decoder import AmbisonicDecoder

class RenderExporter:
    def __init__(self, scene: bpy.types.Scene, decimals: int = 18):
        np.set_printoptions(precision=decimals, floatmode='fixed', threshold=np.inf)
        self.decimals = decimals
        self.scene = bpy.context.scene
        self.scale_factor = 1.0  # Blender units to meters
        render_path = scene.pbraudio.cache_path
        if render_path.startswith('//'):
            render_path = f"{bpy.path.abspath(render_path)}"
        os.makedirs(render_path, exist_ok=True)
        self.render_path = f"{render_path}/AcousticDomain"
        os.makedirs(self.render_path, exist_ok=True)

        system = {}
        system["sample_rate"] = self.scene.pbraudio.sample_rate
        system["bit_depth"] = self.scene.pbraudio.bit_depth.replace('BIT', '')
        system["file_format"] = self.scene.pbraudio.file_format
        system["fps"] = self.scene.render.fps
        system["fps_base"] = self.scene.render.fps_base
        system["subframes"] = 1
        system["cache_path"] = self.render_path
        bands_per_octave = self.scene.pbraudiorender.bands_per_octave
        if self.scene.pbraudiorender.enable_frequencies_range_set:
            system['freq_max'] = self.scene.pbraudiorender.higher_frequency
            system['freq_min'] = self.scene.pbraudiorender.lowest_frequency
        else:
            system['freq_max'] = self.scene.pbraudio.sample_rate / 2
            system['freq_min'] = 5

        self.objects = []
        self.sources = []
        self.outputs = []
        self.cameras = []
        self.environments = []
        self.config = {}
        self.config["system"] = system

        self.not_valid = []
        self.obj_idx = 0
        self.source_idx = 0
        self.output_idx = 0
        self.camera_idx = 0
        self.environment_idx = 0

    def domain_config(self):
        domain_config = {}
        # find world domain property
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                if hasattr(world.pbraudio, 'acoustic_domain'):
                    acoustic_domain = world.pbraudio.acoustic_domain
                    domain_config['name'] = acoustic_domain.name

                    # Get world matrix of the domain object
                    world_matrix = acoustic_domain.matrix_world
                
                    # find corner vertex of domain bounding box
                    domain_config['geometry'] = []
                    vertexs = acoustic_domain.bound_box
                    for idx in range(8):
                            domain_config['geometry'] += [[vertexs[idx][0], vertexs[idx][1], vertexs[idx][2]]]
#                        domain_config['geometry'] += [world_matrix @ Vector((vertexs[idx][0], vertexs[idx][1], vertexs[idx][2]))]
#                    # 1 5 7 3
#                    for idx in range(8):
#                        if not idx % 2 == 0:
#                            domain_config['geometry'] += [[vertexs[idx][0], vertexs[idx][1], vertexs[idx][2]]]
#                    # 0 4 6 2
#                    for idx in range(8):
#                        if idx % 2 == 0:
#                            domain_config['geometry'] += [[vertexs[idx][0], vertexs[idx][1], vertexs[idx][2]]]
#
#                # Get all 8 vertices in world space
#                domain_config['geometry'] = []
#                for corner in acoustic_domain.bound_box:
#                    # Transform local corner to world space
#                    world_corner = world_matrix @ Vector(corner)
#                    domain_config['geometry'].append([
#                        world_corner.x, 
#                        world_corner.y, 
#                        world_corner.z
#                    ])
                
                # Get acoustic properties from material
                domain_config['acoustic_shader'] = self.get_acoustic_properties_from_world()
                break

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

    def get_from_previous_material(self, node):
        scene = bpy.context.scene
        pbraudiorender = bpy.context.scene.pbraudiorender
        bands_per_octave = pbraudiorender.bands_per_octave
        if pbraudiorender.enable_frequencies_range_set:
            freq_max = pbraudiorender.higher_frequency
            freq_min = pbraudiorender.lowest_frequency
        else:
            freq_max = scene.pbraudio.sample_rate / 2
            freq_min = 5

        acoustic_dict = {}
        # get inputs
        inputs = node.inputs.keys()
        for in_idx in inputs:
            if node.inputs[in_idx].is_linked:
                previous_acoustic_dict = self.get_from_previous_material(node.inputs[in_idx].links[0].from_node)
                if previous_acoustic_dict['type'] == 'AcousticShader':
                    acoustic_dict = {**acoustic_dict, **previous_acoustic_dict}
                elif previous_acoustic_dict['type'] == 'AcousticProperties':
                    acoustic_dict['acoustic_properties'] = previous_acoustic_dict
                elif previous_acoustic_dict['type'] == 'FrequencyResponse':
                    quantity_type = 'magnitude'
                    if in_idx in ['absorption', 'refraction', 'reflection', 'scattering']:
                        quantity_type = 'coefficients'
                    desired_points, _ = frd_io.generate_bands(freq_min, freq_max, bands_per_octave)
                    freq_resp_file = previous_acoustic_dict['response_filepath']
                    if freq_resp_file.startswith('//'):
                        freq_resp_file = bpy.path.abspath(freq_resp_file)
                    if os.path.exists(freq_resp_file):
                        freqs, mags, phases = frd_io.parse_frd_file(freq_resp_file)
                        acoustic_dict[in_idx] = {"frequencies": freqs.tolist(), quantity_type: mags.tolist(), 'phases': phases.tolist()}

            elif not node.inputs[in_idx].is_linked:
                if node.pbraudio_type == 'AcousticProperties':
                    quantity_type = 'magnitude'
                    if in_idx in ['absorption', 'refraction', 'reflection', 'scattering']:
                        quantity_type = 'coefficients'
                    delta_f = (freq_max - freq_min)/4
                    freqs = [freq_min, freq_min + delta_f, freq_min + 2*delta_f, freq_max - delta_f, freq_max]
                    mag = node.inputs[in_idx].default_value
                    mags = [mag for _ in range(5)]
                    phases = []
                    acoustic_dict[in_idx] = {"frequencies": freqs, quantity_type: mags, 'phases': phases}

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

    def get_from_previous_empty(self, node):
        scene = bpy.context.scene
        pbraudiorender = bpy.context.scene.pbraudiorender
        bands_per_octave = pbraudiorender.bands_per_octave
        if pbraudiorender.enable_frequencies_range_set:
            freq_max = pbraudiorender.higher_frequency
            freq_min = pbraudiorender.lowest_frequency
        else:
            freq_max = scene.pbraudio.sample_rate / 2
            freq_min = 5

        acoustic_dict = {}
        acoustic_dict['type'] = node.pbraudio_type
        # get inputs
        links = node.inputs.keys()
        for link in links:
            if node.inputs[link].is_linked:
                previous_acoustic_dict = self.get_from_previous_empty(node.inputs[link].links[0].from_node)
#                print('previous_acoustic_dict: ', previous_acoustic_dict)
                if not len(previous_acoustic_dict) == 0:
                    if previous_acoustic_dict['type'] == 'SpatialFrequencyResponse':
                        # ToDo add azimuth and elevation
                        pass
                    elif previous_acoustic_dict['type'] == 'FrequencyResponse':
                        freq_resp_file = previous_acoustic_dict['response_filepath']
                        if os.path.exists(freq_resp_file):
                            freqs, mags, phases = frd_io.parse_frd_file(freq_resp_file)
                            acoustic_dict['spatial_freq_response'] = {"azimuth": [0], "elevation": [0], "frequencies": freqs.tolist(), 'magnitude': mags.tolist(), 'phases': phases.tolist()}

            elif not node.inputs[link].is_linked:
                if node.pbraudio_type == 'SoundOutput':
                    quantity_type = 'magnitude'
                    delta_f = (freq_max - freq_min)/4
                    freqs = [freq_min, freq_min + delta_f, freq_min + 2*delta_f, freq_max - delta_f, freq_max]
                    mag = node.inputs[link].default_value
                    mags = [mag for _ in range(5)]
                    phases = []
                    acoustic_dict['spatial_freq_response'] = {"azimuth": [0], "elevation": [0], "frequencies": freqs, quantity_type: mags, 'phases': phases}


        for property in node.bl_rna.properties.keys():
            if property.startswith('pbraudio_'):
                node_property = "node." + property
                acoustic_value = eval(node_property)
                acoustic_dict[property.replace('pbraudio_', '')] = acoustic_value

        return acoustic_dict

    def get_from_previous_world(self, node):
        acoustic_dict = {}
        # get inputs
        links = node.inputs.keys()
        for link in links:
            if node.inputs[link].is_linked:
                previous_acoustic_dict = self.get_from_previous_world(node.inputs[link].links[0].from_node)
                if previous_acoustic_dict['type'] == 'WorldShader':
                    acoustic_dict['sound_speed'] = previous_acoustic_dict['sound_speed']
                    acoustic_dict['density'] = previous_acoustic_dict['density']
                    acoustic_dict['temperature'] = previous_acoustic_dict['temperature']
                elif previous_acoustic_dict['type'] == 'WorldImpedence':
                    acoustic_dict['impedence'] = previous_acoustic_dict['impedence']
                elif previous_acoustic_dict['type'] == 'WorldDensity':
                    acoustic_dict['density'] = previous_acoustic_dict['density']
                elif previous_acoustic_dict['type'] == 'WorldTemperature':
                    acoustic_dict['temperature'] = previous_acoustic_dict['temperature']
                elif previous_acoustic_dict['type'] == 'WorldEnvironment':
                    acoustic_dict[link] = previous_acoustic_dict
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

        # ADD DEFAULT VALUE IF DOMAIN HAVE NO MATERIAL
        acoustic_shader = {}
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio'):
                if hasattr(world.pbraudio, 'nodetree'):
                    nodetree = world.pbraudio.nodetree
                    for key in nodetree.nodes.keys():
                        if nodetree.nodes[key].pbraudio_type == 'WorldOutput':
                            output_node = nodetree.nodes[key]
                            acoustic_shader = self.get_from_previous_world(output_node)

        return acoustic_shader

    def get_acoustic_properties_from_material(self, obj):
        """Get acoustic properties from the acoustic material node chain"""

        # ADD DEFAULT VALUE IF OBJECT HAVE NO MATERIAL
        acoustic_shader = {}
        nodetree = obj.pbraudio.nodetree
        if hasattr(nodetree, 'nodes'):
            for key in nodetree.nodes.keys():
                if nodetree.nodes[key].pbraudio_type == 'MaterialOutput':
                    output_node = nodetree.nodes[key]
                    acoustic_shader = self.get_from_previous_material(output_node)
                    
        return acoustic_shader

    def get_acoustic_properties_from_empty(self, empty):
        """Get audio properties from the acoustic node chain"""

        # ADD DEFAULT VALUE IF OBJECT HAVE NO MATERIAL
        acoustic_shader = {}
        nodetree = empty.pbraudio.nodetree
        if hasattr(nodetree, 'nodes'):
            for key in nodetree.nodes.keys():
                if nodetree.nodes[key].pbraudio_type == 'SoundOutput':
                    output_node = nodetree.nodes[key]
                    acoustic_shader = self.get_from_previous_empty(output_node)

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

    def export_pose_empty(self, empty, frame_number):
        """Export source, output and camera empty data for a single frame"""
        # Set current frame
        bpy.context.scene.frame_set(frame_number)

        world_matrix = self.get_world_matrix(empty)

        # Get center position and rotation
        location = list([world_matrix.translation.x * self.scale_factor, world_matrix.translation.y * self.scale_factor, world_matrix.translation.z * self.scale_factor])

        # Extract rotation matrix (3x3)
        rotation = list([empty.rotation_euler.x, empty.rotation_euler.y, empty.rotation_euler.z])

        return {
            'location': location,
            'rotation': rotation
        }

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

    def is_point_inside_domain(self, point, vertices):
        """
        Check if a point is inside the acoustic domain using barycentric coordinates.
    
        Args:
            point: Vector - The point to test
            vertices: list of 8 Vectors - The vertices of the parallelepiped in order:
                      [v0, v1, v2, v3, v4, v5, v6, v7]
                      Where:
                      v0-v3: bottom face (counter-clockwise)
                      v4-v7: top face (counter-clockwise, directly above v0-v3)
    
        Returns:
            bool: True if point is inside the parallelepiped
        """
        # Create basis vectors from the parallelepiped edges
        u = vertices[1] - vertices[0]  # edge from v0 to v1
        v = vertices[3] - vertices[0]  # edge from v0 to v3
        w = vertices[4] - vertices[0]  # edge from v0 to v4 (height)
    
        # Create transformation matrix
        M = Matrix([u, v, w]).transposed()
    
        # Check if matrix is invertible
        if M.determinant() == 0:
            print("Warning: AcousticDomain vertices are coplanar or degenerate")
            return False
    
        # Calculate inverse matrix
        M_inv = M.inverted()
    
        # Transform point to parallelepipediped's coordinate system
        p_local = M_inv @ (point - vertices[0])
    
        # Check if point is inside unit cube in local coordinates
        return (0 <= p_local.x <= 1 and 
                0 <= p_local.y <= 1 and 
                0 <= p_local.z <= 1)

    def find_empty_in_domain(self, domain_vertices, empty_type):
        """
        Find all output, source or camera empty objects inside the acoustic domain.
        Args:
            domain_vertices: list of 8 Vectors - vertices of the acoustic domain
        Returns:
            list: Source objects inside/intersecting the acoustic domain
        """ 
        if empty_type == 'output':
            # Get all sources objects in the scene
            empty_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'EMPTY' and obj.pbraudio.output]
        elif empty_type == 'source':
            # Get all sources objects in the scene
            empty_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'EMPTY' and obj.pbraudio.source]
        elif empty_type == 'camera':
            # Get all sources objects in the scene
            empty_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA' and obj.pbraudio.output]
        elif empty_type == 'environment':
            # Get all environment objects in the scene
            empty_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'EMPTY' and obj.pbraudio.environment]

        empty_inside = []

        for empty in empty_objects:
            # Get world coordinates of empty object location
            world_location = empty.matrix_world.translation

            # Check if empty.location are inside
            if self.is_point_inside_domain(world_location, domain_vertices):
                empty_inside += [empty]
        return empty_inside

    def find_objs_in_domain(self, domain_vertices, check_partial=True):
        """
        Find all mesh objects inside or intersecting the acoustic domain.
    
        Args:
            domain_vertices: list of 8 Vectors - vertices of the parallelepiped
            check_partial: bool - If True, include objects partially inside.
                                  If False, only include objects fully inside.
    
        Returns:
            list: Objects inside/intersecting the parallelepiped
        """
        objects_inside = []
    
        # Get all mesh objects in the scene
        mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

        for obj in mesh_objects:
            # Skip the domain object itself
            if obj.name == self.config["acoustic_domain"]["name"]:
                continue
            # Get world coordinates of object vertices
            mesh = obj.data
            world_matrix = obj.matrix_world
    
            # Get all vertices in world space
            world_vertices = [world_matrix @ vert.co for vert in mesh.vertices]
    
            if check_partial:
                # Check if ANY vertex is inside (partial inclusion)
                for vert in world_vertices:
                    if self.is_point_inside_domain(vert, domain_vertices):
                        objects_inside.append(obj)
                        break
            else:
                # Check if ALL vertices are inside (full inclusion)
                all_inside = True
                for vert in world_vertices:
                    if not self.is_point_inside_domain(vert, domain_vertices):
                        all_inside = False
                        break
                if all_inside:
                    objects_inside.append(obj)

        return objects_inside
        
    def export_frame_obj(self, obj, frame_number):
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

    def export_animation_empty(self, empty, empty_idx, start_frame=None, end_frame=None):
        """Export animation sequence"""

        empty.select_set(True)
        name = empty.name_full.replace('.', '_')
    
        os.makedirs(f"{self.render_path}/data/pose", exist_ok=True)
        os.makedirs(f"{self.render_path}/data/{name}", exist_ok=True)
        scene = bpy.context.scene

        frame_data = {}
        location, rotation = ([] for _ in range(2))
        total_frames = 0
        for frame in range(start_frame, end_frame + 1):
            scene.frame_float = frame
#            bpy.context.view_layer.update()
            frame_result = self.export_pose_empty(empty, frame)
            location.append(frame_result['location'])
            rotation.append(frame_result['rotation'])

        location = np.round(np.array(location), self.decimals)
        rotation = np.round(np.array(rotation), self.decimals)
#        print('name: ', name, 'location: ', location, 'rotation: ', rotation)
        output_pose = os.path.join(self.render_path, f"data/pose/{name}.npz")

        empty_config = {}
        empty_config["name"] = name
        empty_config["idx"] = empty_idx
        empty_config["pose_path"] = f"{self.render_path}/data/pose"

        # verify is not static
        if not np.all(location == location[0]) or not np.all(rotation == rotation[0]):
            empty_config["static"] = False
            print(f"{empty.name} is not static...")
            print(f"Exporting pose for {empty.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location, rotation=rotation)
        else:
            empty_config["static"] = True
            print(f"{empty.name} is static...")
            print(f"Exporting pose for {empty.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location[0], rotation=rotation[0])
            print(f"Exporting {empty.name} in {self.render_path}/data/{name}...")

        # Find pbraudio empty type
        if empty.pbraudio.output:
            if empty.pbraudio.output_type == 'AMBI':
                empty_config['type'] = empty.pbraudio.output_type
                empty_config['order'] = empty.pbraudio.ambisonic_order
                empty_config['spatial_arrangement_file'] = empty.pbraudio.spatial_arrangement_file
                if empty.pbraudio.spatial_arrangement_file.startswith('//'):
                    empty_config['spatial_arrangement_file'] = bpy.path.abspath(empty.pbraudio.spatial_arrangement_file)
            elif empty.pbraudio.output_type == 'MONO':
                empty_config['type'] = empty.pbraudio.output_type
                empty_config['micophone_type'] = empty.pbraudio.mono_mic_type
                empty_config['calibration_file'] = empty.pbraudio.output_cal_file
                if empty.pbraudio.output_cal_file.startswith('//'):
                    empty_config['calibration_file'] = bpy.path.abspath(empty.pbraudio.output_cal_file)
            empty_config['size'] = empty.pbraudio.output_size
        elif empty.pbraudio.source:
            if empty.pbraudio.source_type == 'PLANE':
                empty_config['type'] = empty.pbraudio.source_type
                empty_config['size'] = [empty.pbraudio.source_planar_height, empty.pbraudio.source_planar_width]
            if empty.pbraudio.source_type == 'SPHERE':
                empty_config['type'] = empty.pbraudio.source_type
                empty_config['size'] = empty.pbraudio.source_sphere_size
            empty_config['audio_file'] = empty.pbraudio.source_file
            if empty.pbraudio.source_file.startswith('//'):
                empty_config['audio_file'] = bpy.path.abspath(empty.pbraudio.source_file)

        acoustic_shader = self.get_acoustic_properties_from_empty(empty)
        if not len(acoustic_shader) == 0 and hasattr(acoustic_shader, 'spatial_freq_response'):
            empty_config["spatial_freq_response"] = acoustic_shader['spatial_freq_response']

        empty.select_set(False)

        return empty_config

    def export_animation_obj(self, obj, start_frame=None, end_frame=None):
        """Export animation sequence"""

        obj.select_set(True)
        name = obj.name_full.replace('.', '_')
        
        os.makedirs(f"{self.render_path}/data/pose", exist_ok=True)
        os.makedirs(f"{self.render_path}/data/{name}", exist_ok=True)
        scene = bpy.context.scene

        frame_data = {}
        fractured = False
        location, rotation = ([] for _ in range(2))
        total_frames = 0
        for frame in range(start_frame, end_frame + 1):
            scene.frame_float = frame
#            bpy.context.view_layer.update()
            frame_result = self.export_pose(obj, frame)
            location.append(frame_result['location'])
            rotation.append(frame_result['rotation'])

            if not frame_result['fractured'] == False:
                fractured = frame_result['fractured']

        location = np.round(np.array(location), self.decimals)
        rotation = np.round(np.array(rotation), self.decimals)
        output_pose = os.path.join(self.render_path, f"data/pose/{name}.npz")

        object = {}
        object["idx"] = self.obj_idx
        object["name"] = name
        object["obj_path"] = f"{self.render_path}/data/{name}"
        object["pose_path"] = f"{self.render_path}/data/pose"

        # verify is not static
        if not np.all(location == location[0]) or not np.all(rotation == rotation[0]):
            object["static"] = False
            print(f"{obj.name} is not static...")
#            print(f"Exporting pose for {obj.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location, rotation=rotation)

            for frame in range(start_frame, end_frame + 1):
                scene.frame_float = frame
#                bpy.context.view_layer.update()
                print(f"Exporting {obj.name} frame {frame} in {self.render_path}/data/{name}...")
                frame_result = self.export_frame_obj(obj, frame)
            
                # Store each component separately for easy access
                frame_data['vertices'] = frame_result['vertices']
                frame_data['normals'] = frame_result['normals']
                frame_data['faces'] = frame_result['faces']

                # Save to npz
                output_file = os.path.join(self.render_path, f"data/{name}/{name}_{frame:05d}.npz")
                np.savez_compressed(output_file, **frame_data)
        else:
            object["static"] = True
            print(f"{obj.name} is static...")
            print(f"Exporting pose for {obj.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location[0], rotation=rotation[0])            
            print(f"Exporting {obj.name} in {self.render_path}/data/{name}...")
            frame_result = self.export_frame_obj(obj, start_frame)

            # Store each component separately for easy access
            frame_data[f'vertices'] = frame_result['vertices']
            frame_data[f'normals'] = frame_result['normals']
            frame_data[f'faces'] = frame_result['faces']

            # Save to npz
            output_file = os.path.join(self.render_path, f"data/{name}/{name}.npz")
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
        if not obj.name == self.config["acoustic_domain"]["name"]:
            acoustic_shader = self.get_acoustic_properties_from_material(obj)

            object["acoustic_shader"] = acoustic_shader

            print(f"to_add: {self.to_add(name)} object: {name} not_valid: {self.not_valid}")

            if self.to_add(name):
                self.objects.append(object)
                self.obj_idx += 1
            obj.select_set(False)            

    def export_animation(self, start_frame=None, end_frame=None):
        if start_frame is None:
            start_frame = self.scene.frame_current
        if end_frame is None:
            end_frame = start_frame

        self.domain_config()
        for world in bpy.data.worlds.values():
            acoustic_domain = world.pbraudio.acoustic_domain
            world_matrix = acoustic_domain.matrix_world
        domain_vertices = self.config["acoustic_domain"].get('geometry', [])
        domain_vectors = [world_matrix @ Vector(v) for v in domain_vertices]
        objects = self.find_objs_in_domain(domain_vertices=domain_vectors)
        for obj in objects:
            self.export_animation_obj(obj, start_frame, end_frame)

        # Get sources and environment
        environments = self.find_empty_in_domain(domain_vertices=domain_vectors, empty_type='environment')
        boundaries_empties = []
        if not len(environments) == 0:
            boundaries_empties = []
            for environment in environments:
                if not environment.pbraudio.environment_file == "":
                    # Save environment data as json
                    json_config_path = environment_json.save_environment_json(environment, self.render_path)
                    # Decode boundary empty audio chanel from saved json
                    ambisonic_decoder = AmbisonicDecoder(json_config_path=json_config_path)
                    ambisonic_decoder.save_decoded_files()
                # find all children boundary empty
#                boundary_empties = environment.children
#                for boundary_empty in boundary_empties:
#                    boundary_empty.hide_select = False
#            boundaries_empties += boundary_empties
        sources = self.find_empty_in_domain(domain_vertices=domain_vectors, empty_type='source')

        to_be_hided = False
        for source in sources:
            if source.pbraudio.source:
                if source.hide_select == True:
                    to_be_hided = True
                    source.hide_select = False
                self.sources += [self.export_animation_empty(source, self.source_idx, start_frame, end_frame)]
#                exported_source = [self.export_animation_empty(source, self.source_idx, start_frame, end_frame)]
#                self.sources += exported_source
                self.source_idx += 1
                if to_be_hided == True:
                    to_be_hided = False
                    source.hide_select = True
        self.config["sources"] = self.sources
#        if not len(boundaries_empties) == 0:
#            for boundary_empty in boundaries_empties:
#                boundary_empty.hide_select = True

        outputs = self.find_empty_in_domain(domain_vertices=domain_vectors, empty_type='output')
        for output in outputs:
            if output.pbraudio.output:
                self.output_idx += 1
                self.outputs += [self.export_animation_empty(output, self.output_idx, start_frame, end_frame)]
        self.config["outputs"] = self.outputs

        cameras = self.find_empty_in_domain(domain_vertices=domain_vectors, empty_type='camera')
        for camera in cameras:
            if camera.pbraudio.output:
                self.camera_idx += 1
                self.cameras += [self.export_animation_empty(camera, self.camera_idx, start_frame, end_frame)]
        self.config["cameras"] = self.cameras

        self.wave_propagation()
        self.interface_config()
        self.resonance_config()
        self.termination_config()
        self.save_config()

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
        config_file = f"{self.render_path}/config.json"
        js = json.dumps(self.config, indent=2, separators=(',', ': '))
        with open(config_file, 'w+') as json_file:
            json_file.write(js)
