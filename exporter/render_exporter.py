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
import os
import json
import ast
from mathutils import Matrix, Vector
from ..utils import frd_io

class RenderExporter:
    """Main exporter for acoustic rendering scenes"""
    
    def __init__(self, depsgraph: bpy.types.Depsgraph, scene: bpy.types.Scene, decimals: int = 18):
        np.set_printoptions(precision=decimals, floatmode='fixed', threshold=np.inf)
        self.decimals = decimals
        self.scene = scene
        self.depsgraph = depsgraph
        self.scale_factor = 1.0  # Blender units to meters
        
        # Setup paths
        self.setup_paths()
        
        # Initialize data structures
        self.config = {}
        self.objects = []
        self.sources = []
        self.outputs = []
        self.environments = []
        self.not_valid = []
        
        # Counters
        self.obj_idx = 0
        self.source_idx = 0
        self.output_idx = 0
        self.environment_idx = 0
        
        # Build configuration
        self.build_config()
    
    def setup_paths(self):
        """Setup export directories"""
        render_path = self.scene.pbraudio.cache_path
        if render_path.startswith('//'):
            render_path = bpy.path.abspath(render_path)
        
        os.makedirs(render_path, exist_ok=True)
        self.render_path = os.path.join(render_path, "AcousticDomain")
        os.makedirs(self.render_path, exist_ok=True)
    
    def build_config(self):
        """Build complete configuration"""
        self.config["system"] = self.get_system_config()
        self.config["acoustic_domain"] = self.get_domain_config()
        self.config["wave_propagation"] = self.get_wave_propagation_config()
        self.config["interface"] = self.get_interface_config()
        self.config["resonance"] = self.get_resonance_config()
        self.config["termination"] = self.get_termination_config()
    
    def get_system_config(self):
        """Get system configuration"""
        system = {
            "sample_rate": self.scene.pbraudio.sample_rate,
            "bit_depth": self.scene.pbraudio.bit_depth.replace('BIT', ''),
            "file_format": self.scene.pbraudio.file_format,
            "fps": self.scene.render.fps,
            "fps_base": self.scene.render.fps_base,
            "subframes": 1,
            "start_frame": self.scene.frame_start,
            "end_frame": self.scene.frame_end,
            "cache_path": self.render_path
        }

        system['bands_per_octave'] = self.scene.pbraudiorender.bands_per_octave

        # Frequency range
        if self.scene.pbraudiorender.enable_frequencies_range_set:
            system['lowest_frequency'] = self.scene.pbraudiorender.lowest_frequency
            system['higher_frequency'] = self.scene.pbraudiorender.higher_frequency
        else:
            system['lowest_frequency'] = 5
            system['higher_frequency'] = self.scene.pbraudio.sample_rate / 2

        # Adaptive mesh refinement
        if self.scene.pbraudiorender.enable_adr:
            system['adr_threshold'] = self.scene.pbraudiorender.adr_threshold

        return system
    
    def get_domain_config(self):
        """Get acoustic domain configuration"""
        domain_config = {}
        
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio') and hasattr(world.pbraudio, 'acoustic_domain'):
                acoustic_domain = world.pbraudio.acoustic_domain
                domain_config['name'] = acoustic_domain.name
                
                # Get domain geometry (bounding box vertices)
                domain_config['geometry'] = self.get_domain_geometry(acoustic_domain)
                
                # Get acoustic properties
                domain_config['acoustic_shader'] = self.get_acoustic_properties_from_world()
                break
        
        return domain_config
    
    def get_domain_geometry(self, domain_obj):
        """Extract domain geometry vertices"""
        vertices = []
        for vertex in domain_obj.bound_box:
            vertices.append([vertex[0], vertex[1], vertex[2]])
        return vertices
    
    def get_wave_propagation_config(self):
        """Get wave propagation configuration"""
        wave_config = {
            'max_interactions': self.scene.pbraudiorender.max_interactions,
            'enable_interface': self.scene.pbraudiorender.enable_interface,
            'enable_resonance': self.scene.pbraudiorender.enable_resonance,
            'enable_termination': self.scene.pbraudiorender.enable_termination,
            'use_dispersion_correction': self.scene.pbraudiorender.use_dispersion_correction,
            'use_extended_reaction': self.scene.pbraudiorender.use_extended_reaction,
            'use_complex_eigenray': self.scene.pbraudiorender.use_complex_eigenray
        }
        
        if wave_config['use_dispersion_correction']:
            wave_config['dispersion_order'] = self.scene.pbraudiorender.dispersion_order
            
        if wave_config['use_extended_reaction']:
            wave_config['max_modal_reaction'] = self.scene.pbraudiorender.max_modal_reaction
            
        if wave_config['use_complex_eigenray']:
            wave_config['max_complex_eigenray'] = self.scene.pbraudiorender.max_complex_eigenray
            
        return wave_config
    
    def get_interface_config(self):
        """Get interface configuration"""
        interface_config = {}
        
        if self.scene.pbraudiorender.enable_interface:
            props = self.scene.pbraudiorender
            interface_config.update({
                "enable_absorption": props.enable_absorption,
                "enable_reflection": props.enable_reflection,
                "enable_scattering": props.enable_scattering,
                "enable_refraction": props.enable_refraction,
                "enable_diffraction": props.enable_diffraction,
                "min_impedance_ratio": props.min_impedance_ratio,
                "max_impedance_ratio": props.max_impedance_ratio
            })
            
            if props.enable_reflection:
                interface_config["max_reflection"] = props.max_reflection
            if props.enable_scattering:
                interface_config["max_scattering"] = props.max_scattering
            if props.enable_refraction:
                interface_config["max_refraction"] = props.max_refraction
            if props.enable_diffraction:
                interface_config["max_diffraction"] = props.max_diffraction
                
        return interface_config
    
    def get_resonance_config(self):
        """Get resonance configuration"""
        resonance_config = {}
        
        if self.scene.pbraudiorender.enable_resonance:
            props = self.scene.pbraudiorender
            resonance_config.update({
                "max_resonance_structure": props.max_resonance_structure,
                "resonance_threshold": props.resonance_threshold,
                "enable_helmholtz": props.enable_helmholtz,
                "enable_parallel_wall": props.enable_parallel_wall,
                "enable_tube": props.enable_tube
            })
            
            if props.enable_helmholtz:
                resonance_config.update({
                    "min_cavity_volume": props.min_cavity_volume,
                    "max_resonance_room_modes": props.max_resonance_room_modes
                })
                
            if props.enable_parallel_wall:
                resonance_config.update({
                    "min_wall_distance": props.min_wall_distance,
                    "max_wall_distance": props.max_wall_distance
                })
                
            if props.enable_tube:
                resonance_config.update({
                    "min_tube_length": props.min_tube_length,
                    "min_tube_aspect_ratio": props.min_tube_aspect_ratio
                })
                
        return resonance_config
    
    def get_termination_config(self):
        """Get termination configuration"""
        termination_config = {}
        
        if self.scene.pbraudiorender.enable_termination:
            props = self.scene.pbraudiorender
            termination_config["termination_type"] = props.termination_type
            
            if props.termination_type == 'SAMPLE_END':
                termination_config.update({
                    "samples_after": props.samples_after,
                    "min_active_sources": props.min_active_sources
                })
            elif props.termination_type == 'REVERBERATION_TIME':
                termination_config["max_reverberation_time"] = props.max_reverberation_time
            elif props.termination_type == 'ENERGY_THRESHOLD':
                termination_config.update({
                    "max_energy_threshold": props.max_energy_threshold,
                    "min_energy_threshold": props.min_energy_threshold
                })
        else:
            termination_config["termination_type"] = 'FINAL_FRAME'
            
        return termination_config
    
    def get_acoustic_properties_from_world(self):
        """Get acoustic properties from world node tree"""
        acoustic_shader = {}
        
        for world in bpy.data.worlds.values():
            if hasattr(world, 'pbraudio') and hasattr(world.pbraudio, 'nodetree'):
                nodetree = world.pbraudio.nodetree
                for node in nodetree.nodes.values():
                    if node.pbraudio_type == 'WorldOutput':
                        acoustic_shader = self.traverse_node_tree(node, 'world')
                        break
        
        return acoustic_shader
    
    def get_acoustic_properties_from_material(self, obj):
        """Get acoustic properties from material node tree"""
        acoustic_shader = {}
        
        if hasattr(obj.pbraudio, 'nodetree'):
            nodetree = obj.pbraudio.nodetree
            for node in nodetree.nodes.values():
                if node.pbraudio_type == 'MaterialOutput':
                    acoustic_shader = self.traverse_node_tree(node, 'material')
                    break
                    
        return acoustic_shader
    
    def get_acoustic_properties_from_empty(self, empty):
        """Get audio properties from empty node tree"""
        acoustic_shader = {}
        
        if hasattr(empty.pbraudio, 'nodetree'):
            nodetree = empty.pbraudio.nodetree
            for node in nodetree.nodes.values():
                if node.pbraudio_type == 'SoundOutput':
                    acoustic_shader = self.traverse_node_tree(node, 'empty')
                    break
        
        return acoustic_shader
    
    def traverse_node_tree(self, node, node_type):
        """Traverse node tree to extract properties"""
        acoustic_dict = {'type': node.pbraudio_type}
        
        # Handle inputs
        for input_socket in node.inputs:
            if input_socket.is_linked:
                linked_node = input_socket.links[0].from_node
                linked_data = self.traverse_node_tree(linked_node, node_type)
                
                if node_type == 'world':
                    self.merge_world_properties(acoustic_dict, linked_data, input_socket.name)
                elif node_type == 'material':
                    self.merge_material_properties(acoustic_dict, linked_data, input_socket.name)
                elif node_type == 'empty':
                    self.merge_empty_properties(acoustic_dict, linked_data, input_socket.name)
        
        # Extract node properties
        self.extract_node_properties(node, acoustic_dict)
        
        return acoustic_dict
    
    def merge_world_properties(self, target_dict, source_dict, socket_name):
        """Merge world node properties"""
        if source_dict['type'] == 'WorldShader':
            target_dict.update({
                'sound_speed': source_dict.get('sound_speed'),
                'density': source_dict.get('density'),
                'temperature': source_dict.get('temperature')
            })
        elif source_dict['type'] == 'WorldImpedence':
            target_dict['impedence'] = source_dict.get('impedence')
        elif source_dict['type'] == 'WorldDensity':
            target_dict['density'] = source_dict.get('density')
        elif source_dict['type'] == 'WorldTemperature':
            target_dict['temperature'] = source_dict.get('temperature')
        elif source_dict['type'] == 'WorldEnvironment':
            target_dict[socket_name] = source_dict
    
    def merge_material_properties(self, target_dict, source_dict, socket_name):
        """Merge material node properties"""
        if source_dict['type'] == 'AcousticShader':
            target_dict.update(source_dict)
        elif source_dict['type'] == 'AcousticProperties':
            target_dict['acoustic_properties'] = source_dict
        elif source_dict['type'] == 'FrequencyResponse':
            self.add_frequency_response(target_dict, source_dict, socket_name)
        elif source_dict['type'] == 'SpatialFrequencyResponse':
            # TODO: Add azimuth and elevation handling
            pass
    
    def merge_empty_properties(self, target_dict, source_dict, socket_name):
        """Merge empty node properties"""
        if source_dict['type'] == 'FrequencyResponse':
            self.add_frequency_response(target_dict, source_dict, socket_name)
        elif source_dict['type'] == 'SpatialFrequencyResponse':
            # TODO: Add azimuth and elevation handling
            pass
    
    def add_frequency_response(self, target_dict, source_dict, socket_name):
        """Add frequency response data"""
        freq_resp_file = source_dict.get('response_filepath', '')
        if os.path.exists(freq_resp_file):
            freqs, mags, phases = frd_io.parse_frd_file(freq_resp_file)
            
            # Determine quantity type based on socket name
            quantity_type = 'magnitude'
            if socket_name in ['absorption', 'refraction', 'reflection', 'scattering']:
                quantity_type = 'coefficients'
            
            target_dict[socket_name] = {
                "frequencies": freqs.tolist(),
                quantity_type: mags.tolist(),
                'phases': phases.tolist()
            }
    
    def extract_node_properties(self, node, target_dict):
        """Extract properties from node"""
        for prop_name in node.bl_rna.properties.keys():
            if prop_name.startswith('pbraudio_'):
                prop_value = getattr(node, prop_name)
                
                # Apply unit conversions
                if 'young_modulus' in prop_name:
                    prop_value *= 1e9
                elif 'damping' in prop_name:
                    prop_value *= 0.01
                
                target_dict[prop_name.replace('pbraudio_', '')] = prop_value
    
    def is_point_inside_domain(self, point, domain_vertices):
        """
        Check if a point is inside the acoustic domain using barycentric coordinates.
        
        Args:
            point: Vector - The point to test
            domain_vertices: list of 8 Vectors - The vertices of the parallelepiped
            
        Returns:
            bool: True if point is inside the parallelepiped
        """
        if len(domain_vertices) != 8:
            return False
            
        # Create basis vectors from the parallelepiped edges
        v0 = Vector(domain_vertices[0])
        v1 = Vector(domain_vertices[1])
        v3 = Vector(domain_vertices[3])
        v4 = Vector(domain_vertices[4])
        
        u = v1 - v0  # edge from v0 to v1
        v = v3 - v0  # edge from v0 to v3
        w = v4 - v0  # edge from v0 to v4 (height)
        
        # Create transformation matrix
        M = Matrix([u, v, w]).transposed()
        
        # Check if matrix is invertible
        if M.determinant() == 0:
            print("Warning: AcousticDomain vertices are coplanar or degenerate")
            return False
        
        # Calculate inverse matrix
        M_inv = M.inverted()
        
        # Transform point to parallelepiped's coordinate system
        p_local = M_inv @ (Vector(point) - v0)
        
        # Check if point is inside unit cube in local coordinates
        return (0 <= p_local.x <= 1 and 
                0 <= p_local.y <= 1 and 
                0 <= p_local.z <= 1)
    
    def find_objects_in_domain(self, domain_vertices, obj_type='mesh', check_partial=True):
        """
        Find objects inside or intersecting the acoustic domain.
        
        Args:
            domain_vertices: list of 8 Vectors - vertices of the acoustic domain
            obj_type: str - Type of objects to find ('mesh', 'source', 'output', 'environment')
            check_partial: bool - If True, include objects partially inside
            
        Returns:
            list: Objects inside/intersecting the domain
        """
        objects_inside = []
        
        if obj_type == 'mesh':
            objects = [obj for obj in self.depsgraph.objects if obj.type == 'MESH']
        elif obj_type == 'source':
            objects = [obj for obj in self.depsgraph.objects if obj.type == 'EMPTY' and obj.pbraudio.source]
        elif obj_type == 'output':
            objects = [obj for obj in self.depsgraph.objects if obj.type in ['EMPTY', 'CAMERA'] and obj.pbraudio.output]
        elif obj_type == 'environment':
            objects = [obj for obj in self.depsgraph.objects if obj.type == 'EMPTY' and obj.pbraudio.environment]
        else:
            return objects_inside

        domain_name = self.config["acoustic_domain"].get("name", "")
        
        for obj in objects:
            # Skip the domain object itself
            if obj.name == domain_name:
                continue
                
            if obj_type == 'mesh':
                if self.is_mesh_inside_domain(obj, domain_vertices, check_partial):
                    objects_inside.append(obj)
            else:
                # For empties, check only the location
                world_location = obj.matrix_world.translation
                if self.is_point_inside_domain(world_location, domain_vertices):
                    objects_inside.append(obj)
        
        return objects_inside

    def is_mesh_intersecting_domain(self, obj, domain_vertices):
        """
        Check if mesh intersects the acoustic domain using triangle-AABB intersection.
        This handles cases where no vertices are inside but triangles intersect the domain.
        
        Args:
            obj: bpy.types.Object - Mesh object to check
            domain_vertices: list of 8 Vectors - vertices of the acoustic domain
        
        Returns:
            bool: True if mesh intersects the domain
        """
        if len(domain_vertices) != 8:
            return False
    
        # Get domain bounding box in world coordinates
        domain_verts_world = [Vector(v) for v in domain_vertices]
    
        # Calculate domain AABB (Axis-Aligned Bounding Box)
        domain_min = Vector((
            min(v.x for v in domain_verts_world),
            min(v.y for v in domain_verts_world),
            min(v.z for v in domain_verts_world)
        ))
        domain_max = Vector((
            max(v.x for v in domain_verts_world),
            max(v.y for v in domain_verts_world),
            max(v.z for v in domain_verts_world)
        ))
    
        # Get evaluated mesh
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
    
        # Triangulate if needed
        self.triangulate_mesh(mesh)
    
        world_matrix = eval_obj.matrix_world
    
        # Check each triangle for intersection with domain AABB
        for poly in mesh.polygons:
            if len(poly.vertices) != 3:
                continue
            
            # Get triangle vertices in world space
            tri_verts = []
            for vert_idx in poly.vertices:
                vert = mesh.vertices[vert_idx]
                world_co = world_matrix @ vert.co
                tri_verts.append(world_co)
        
            # Check triangle-AABB intersection
            if self.triangle_aabb_intersection(tri_verts, domain_min, domain_max):
                eval_obj.to_mesh_clear()
                return True
    
        eval_obj.to_mesh_clear()
        return False

    def triangle_aabb_intersection(self, triangle, aabb_min, aabb_max):
        """
        Check if triangle intersects with Axis-Aligned Bounding Box.
        Using separating axis theorem (SAT) for triangle-AABB intersection.
    
        Args:
            triangle: list of 3 Vectors - triangle vertices
            aabb_min: Vector - AABB minimum point
            aabb_max: Vector - AABB maximum point
        
        Returns:
            bool: True if triangle intersects AABB
        """
        # Convert to numpy arrays for easier calculations
        import numpy as np
    
        # Triangle vertices
        v0 = np.array(triangle[0])
        v1 = np.array(triangle[1])
        v2 = np.array(triangle[2])
    
        # AABB center and half extents
        aabb_center = (aabb_min + aabb_max) * 0.5
        aabb_half_extents = (aabb_max - aabb_min) * 0.5
        center = np.array(aabb_center)
        half_extents = np.array(aabb_half_extents)
    
        # Translate triangle to AABB's coordinate system
        v0 = v0 - center
        v1 = v1 - center
        v2 = v2 - center
    
        # Triangle edges
        f0 = v1 - v0
        f1 = v2 - v1
        f2 = v0 - v2
    
        # Test axes: a00, a01, a02 (x, y, z axes)
        axes = [
            np.array([1, 0, 0]),
            np.array([0, 1, 0]),
            np.array([0, 0, 1])
        ]
    
        # Test against AABB axes (x, y, z)
        for axis in axes:
            # Project triangle vertices onto axis
            p0 = np.dot(v0, axis)
            p1 = np.dot(v1, axis)
            p2 = np.dot(v2, axis)
        
            # Find min and max of triangle projection
            r = half_extents[abs(axis).argmax()]  # Half extent along this axis
            triangle_min = min(p0, p1, p2)
            triangle_max = max(p0, p1, p2)
        
            # Check for separation
            if triangle_max < -r or triangle_min > r:
                return False
    
        # Test against triangle normal axis
        triangle_normal = np.cross(f0, f1)
        axis = triangle_normal
    
        # Project AABB onto triangle normal
        aabb_projection = np.abs(np.dot(half_extents, np.abs(axis)))
    
        # Project triangle onto triangle normal
        p0 = np.dot(v0, axis)
        p1 = np.dot(v1, axis)
        p2 = np.dot(v2, axis)
    
        triangle_min = min(p0, p1, p2)
        triangle_max = max(p0, p1, p2)
    
        # Check for separation
        if triangle_max < -aabb_projection or triangle_min > aabb_projection:
            return False
    
        # Test against edge cross product axes (9 axes)
        edges = [f0, f1, f2]
        aabb_axes = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]
    
        for edge in edges:
            for aabb_axis in aabb_axes:
                axis = np.cross(edge, aabb_axis)
                if np.linalg.norm(axis) < 1e-6:
                    continue  # Parallel, already tested
            
                # Normalize axis
                axis = axis / np.linalg.norm(axis)
            
                # Project AABB onto axis
                aabb_projection = np.abs(np.dot(half_extents, np.abs(axis)))
            
                # Project triangle onto axis
                p0 = np.dot(v0, axis)
                p1 = np.dot(v1, axis)
                p2 = np.dot(v2, axis)
            
                triangle_min = min(p0, p1, p2)
                triangle_max = max(p0, p1, p2)
            
                # Check for separation
                if triangle_max < -aabb_projection or triangle_min > aabb_projection:
                    return False
    
        return True

    def is_mesh_inside_domain(self, obj, domain_vertices, check_partial):
        """Check if mesh is inside domain"""
        mesh = obj.data
        world_matrix = obj.matrix_world
        
        # Get all vertices in world space
        world_vertices = [world_matrix @ vert.co for vert in mesh.vertices]
        
        if check_partial:
            # Check if ANY vertex is inside (partial inclusion)
            for vert in world_vertices:
                if self.is_point_inside_domain(vert, domain_vertices):
                    return True
            # If no vertices inside, check for triangle intersections
            return self.is_mesh_intersecting_domain(obj, domain_vertices)
        else:
            # Check if ALL vertices are inside (full inclusion)
            for vert in world_vertices:
                if not self.is_point_inside_domain(vert, domain_vertices):
                    return False
            return True
    
    def export_scene(self, start_frame=None, end_frame=None):
        """Export complete scene"""
        if start_frame is None:
            start_frame = self.scene.frame_start
        if end_frame is None:
            end_frame = self.scene.frame_end
        
        # Get domain vertices
        domain_vertices = self.config["acoustic_domain"].get("geometry", [])
        
        # Find and export objects
        self.export_meshes(domain_vertices, start_frame, end_frame)
        self.export_sources(domain_vertices, start_frame, end_frame)
        self.export_outputs(domain_vertices, start_frame, end_frame)
        self.export_environments(domain_vertices, start_frame, end_frame)
        
        # Update configuration with exported objects
        self.update_config_with_objects()
        
#        # Save configuration
#        self.save_config()
    
    def export_meshes(self, domain_vertices, start_frame, end_frame):
        """Export mesh objects"""
        mesh_objects = self.find_objects_in_domain(domain_vertices, 'mesh', check_partial=True)
        
        for obj in mesh_objects:
            self.export_mesh_animation(obj, start_frame, end_frame)
    
    def export_sources(self, domain_vertices, start_frame, end_frame):
        """Export source objects"""
        source_objects = self.find_objects_in_domain(domain_vertices, 'source')
        
        for source in source_objects:
            self.export_empty_animation(source, start_frame, end_frame, 'source')
    
    def export_outputs(self, domain_vertices, start_frame, end_frame):
        """Export output objects"""
        output_objects = self.find_objects_in_domain(domain_vertices, 'output')
        
        for output in output_objects:
            self.export_empty_animation(output, start_frame, end_frame, 'output')
    
    def export_environments(self, domain_vertices, start_frame, end_frame):
        """Export environment objects"""
        env_objects = self.find_objects_in_domain(domain_vertices, 'environment')
        
        for env in env_objects:
            self.export_empty_animation(env, start_frame, end_frame, 'environment')
    
    def export_mesh_animation(self, obj, start_frame, end_frame):
        """Export mesh animation sequence"""
        name = obj.name_full.replace('.', '_')
        
        # Create directories
        pose_dir = os.path.join(self.render_path, "data", "pose")
        obj_dir = os.path.join(self.render_path, "data", name)
        os.makedirs(pose_dir, exist_ok=True)
        os.makedirs(obj_dir, exist_ok=True)
        
        # Export pose data
        pose_data = self.export_mesh_pose(obj, start_frame, end_frame)
        pose_file = os.path.join(pose_dir, f"{name}.npz")
        
        # Check if object is static
        is_static = self.is_object_static(pose_data['locations'], pose_data['rotations'])
        
        # Save pose data
        if is_static:
            np.savez_compressed(pose_file, 
                               location=pose_data['locations'][0], 
                               rotation=pose_data['rotations'][0])
        else:
            np.savez_compressed(pose_file, 
                               location=pose_data['locations'], 
                               rotation=pose_data['rotations'])
        
        # Export mesh frames
        self.export_mesh_frames(obj, start_frame, end_frame, obj_dir, name, is_static)
        
        # Create object configuration
        obj_config = self.create_mesh_config(obj, name, is_static, pose_data)
        
        # Validate mesh
        if not self.validate_mesh(obj, name):
            self.not_valid.append(name)
            return
        
        if name not in self.not_valid:
            self.objects.append(obj_config)
            self.obj_idx += 1
    
    def export_mesh_pose(self, obj, start_frame, end_frame):
        """Export mesh pose data for animation range"""
        locations = []
        rotations = []
        fractured_frame = False
        
        for frame in range(start_frame, end_frame + 1):
            self.scene.frame_set(frame)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            
            pose = self.get_object_pose(obj, depsgraph)
            locations.append(pose['location'])
            rotations.append(pose['rotation'])
            
            if pose['fractured']:
                fractured_frame = pose['fractured']
        
        return {
            'locations': np.round(np.array(locations), self.decimals),
            'rotations': np.round(np.array(rotations), self.decimals),
            'fractured': fractured_frame
        }
    
    def get_object_pose(self, obj, depsgraph):
        """Get object pose at current frame"""
        eval_obj = obj.evaluated_get(depsgraph)
        world_matrix = eval_obj.matrix_world
        
        location = [
            world_matrix.translation.x * self.scale_factor,
            world_matrix.translation.y * self.scale_factor,
            world_matrix.translation.z * self.scale_factor
        ]
        
        rotation = [
            eval_obj.rotation_euler.x,
            eval_obj.rotation_euler.y,
            eval_obj.rotation_euler.z
        ]
        
        # Check for fracture animation
        fractured = self.get_fracture_frame(obj)
        
        return {
            'location': location,
            'rotation': rotation,
            'fractured': fractured
        }
    
    def get_fracture_frame(self, obj):
        """Get fracture frame from animation data"""
        if hasattr(obj.animation_data, 'action'):
            action_name = obj.animation_data.action.name
            for fcurve in bpy.data.actions[action_name].fcurves.values():
                if 'fractured' in fcurve.data_path:
                    for keyframe in fcurve.keyframe_points:
                        if keyframe.co[1] == 1:
                            return keyframe.co[0]
        return False
    
    def is_object_static(self, locations, rotations):
        """Check if object is static (no movement)"""
        return (np.all(locations == locations[0]) and 
                np.all(rotations == rotations[0]))
    
    def export_mesh_frames(self, obj, start_frame, end_frame, obj_dir, name, is_static):
        """Export mesh frames"""
        if is_static:
            # Export single frame for static object
            self.scene.frame_set(start_frame)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            mesh_data = self.export_mesh_frame(obj, depsgraph)
            
            output_file = os.path.join(obj_dir, f"{name}.npz")
            np.savez_compressed(output_file, **mesh_data)
        else:
            # Export all frames for animated object
            for frame in range(start_frame, end_frame + 1):
                self.scene.frame_set(frame)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                mesh_data = self.export_mesh_frame(obj, depsgraph)
                
                output_file = os.path.join(obj_dir, f"{name}_{frame:05d}.npz")
                np.savez_compressed(output_file, **mesh_data)
    
    def export_mesh_frame(self, obj, depsgraph):
        """Export single mesh frame"""
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        
        # Triangulate if needed
        self.triangulate_mesh(mesh)
        
        # Get mesh data
        vertices, normals, faces = self.get_mesh_data(eval_obj, mesh)
        
        # Clean up
        eval_obj.to_mesh_clear()
        
        # Round to specified decimals
        vertices = np.round(vertices, self.decimals)
        normals = np.round(normals, self.decimals)
        
        return {
            'vertices': vertices,
            'normals': normals,
            'faces': faces
        }
    
    def triangulate_mesh(self, mesh):
        """Triangulate mesh using bmesh"""
        if len(mesh.polygons) > 0 and any(len(p.vertices) > 3 for p in mesh.polygons):
            import bmesh
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(mesh)
            bm.free()
            mesh.corner_normals
    
    def get_mesh_data(self, obj, mesh):
        """Extract mesh data (vertices, normals, faces)"""
        world_matrix = obj.matrix_world
        
        # Vertices in world coordinates
        vertices = np.zeros((len(mesh.vertices), 3), dtype=np.float32)
        for i, vert in enumerate(mesh.vertices):
            world_co = world_matrix @ vert.co
            vertices[i] = [
                world_co.x * self.scale_factor,
                world_co.y * self.scale_factor,
                world_co.z * self.scale_factor
            ]
        
        # Vertex normals in world space
        normals = np.zeros((len(mesh.vertices), 3), dtype=np.float32)
        mesh.corner_normals
        for i, vert in enumerate(mesh.vertices):
            normals[i] = world_matrix.to_3x3() @ vert.normal
        
        # Faces (triangles)
        faces = []
        for poly in mesh.polygons:
            if len(poly.vertices) == 3:
                faces.append(poly.vertices)
            elif len(poly.vertices) > 3:
                # Should already be triangulated, but handle just in case
                for i in range(1, len(poly.vertices) - 1):
                    faces.append([poly.vertices[0], poly.vertices[i], poly.vertices[i + 1]])
        
        faces = np.array(faces, dtype=np.int32) if faces else np.zeros((0, 3), dtype=np.int32)
        
        return vertices, normals, faces
    
    def validate_mesh(self, obj, name):
        """Validate mesh is watertight and has volume"""
        # Export a sample frame to check
        self.scene.frame_set(self.scene.frame_start)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh_data = self.export_mesh_frame(obj, depsgraph)
        
        quest_mesh = trimesh.Trimesh(
            vertices=mesh_data['vertices'],
            vertex_normals=mesh_data['normals'],
            faces=mesh_data['faces']
        )
        
        is_valid = quest_mesh.is_watertight and quest_mesh.is_volume
        
        if not is_valid:
            print(f"Mesh {name} is not valid: watertight={quest_mesh.is_watertight}, volume={quest_mesh.is_volume}")
        
        return is_valid
    
    def create_mesh_config(self, obj, name, is_static, pose_data):
        """Create mesh object configuration"""
        obj_config = {
            "idx": self.obj_idx,
            "name": name,
            "obj_path": os.path.join(self.render_path, "data", name),
            "pose_path": os.path.join(self.render_path, "data", "pose"),
            "static": is_static,
            "stochastic_variation": obj.pbraudio.stochastic_variation,
            "ground": obj.pbraudio.ground,
            "resonance": obj.pbraudio.resonance,
            "resonance_modes": obj.pbraudio.resonance_modes,
            "connected": self.get_connected_objects(obj),
            "is_shard": False,
            "fractured": pose_data['fractured'],
            "shard": self.get_shard_objects(obj),
            "acoustic_shader": self.get_acoustic_properties_from_material(obj)
        }
        
        return obj_config
    
    def get_connected_objects(self, obj):
        """Get connected objects list"""
        connected = []
        if obj.pbraudio.connected:
            for item in obj.pbraudio__connected.values():
                connected.append([
                    item.connected_object.replace('.', '_'),
                    item.connected_value / 10
                ])
        return connected if connected else False
    
    def get_shard_objects(self, obj):
        """Get shard objects list"""
        shard = []
        if obj.pbraudio_shard:
            for item in obj.pbraudio_shard.values():
                shard.append(item.shard_object.replace('.', '_'))
        return shard if shard else False
    
    def export_empty_animation(self, empty, start_frame, end_frame, empty_type):
        """Export empty object animation"""
        name = empty.name_full.replace('.', '_')
        
        # Create pose directory
        pose_dir = os.path.join(self.render_path, "data", "pose")
        os.makedirs(pose_dir, exist_ok=True)
        
        # Export pose data
        pose_data = self.export_empty_pose(empty, start_frame, end_frame)
        pose_file = os.path.join(pose_dir, f"{name}.npz")
        
        # Check if empty is static
        is_static = self.is_object_static(pose_data['locations'], pose_data['rotations'])
        
        # Save pose data
        if is_static:
            np.savez_compressed(pose_file, 
                               location=pose_data['locations'][0], 
                               rotation=pose_data['rotations'][0])
        else:
            np.savez_compressed(pose_file, 
                               location=pose_data['locations'], 
                               rotation=pose_data['rotations'])
        
        # Create empty configuration
        empty_config = self.create_empty_config(empty, name, is_static, empty_type)
        
        # Add to appropriate list
        if empty_type == 'source':
            empty_config["idx"] = self.source_idx
            self.sources.append(empty_config)
            self.source_idx += 1
        elif empty_type == 'output':
            empty_config["idx"] = self.output_idx
            self.outputs.append(empty_config)
            self.output_idx += 1
        elif empty_type == 'environment':
            empty_config["idx"] = self.environment_idx
            self.environments.append(empty_config)
            self.environment_idx += 1
    
    def export_empty_pose(self, empty, start_frame, end_frame):
        """Export empty pose data for animation range"""
        locations = []
        rotations = []
        
        for frame in range(start_frame, end_frame + 1):
            self.scene.frame_set(frame)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            
            pose = self.get_empty_pose(empty, depsgraph)
            locations.append(pose['location'])
            rotations.append(pose['rotation'])
        
        return {
            'locations': np.round(np.array(locations), self.decimals),
            'rotations': np.round(np.array(rotations), self.decimals)
        }
    
    
    def get_empty_pose(self, empty, depsgraph):
        """Get empty pose at current frame"""
        eval_empty = empty.evaluated_get(depsgraph)
        world_matrix = eval_empty.matrix_world
        
        location = [
            world_matrix.translation.x * self.scale_factor,
            world_matrix.translation.y * self.scale_factor,
            world_matrix.translation.z * self.scale_factor
        ]
        
        rotation = [
            eval_empty.rotation_euler.x,
            eval_empty.rotation_euler.y,
            eval_empty.rotation_euler.z
        ]
        
        return {'location': location, 'rotation': rotation}
    
    def create_empty_config(self, empty, name, is_static, empty_type):
        """Create empty object configuration"""
        config = {
            "name": name,
            "static": is_static,
            "pose_path": os.path.join(self.render_path, "data", "pose")
        }
        
        if empty.pbraudio.source:
            config.update(self.get_source_config(empty))
        elif empty.pbraudio.output:
            config.update(self.get_output_config(empty))
        
        # Add acoustic properties if not a boundary
        if not empty.pbraudio.environment_boundary and not empty.pbraudio.environment:
            acoustic_shader = self.get_acoustic_properties_from_empty(empty)
#            if 'spatial_freq_response' in acoustic_shader:
#                config["spatial_freq_response"] = acoustic_shader['spatial_freq_response']
        
        return config
    
    def get_source_config(self, source):
        """Get source-specific configuration"""
        config = {
            "type": source.pbraudio.source_type,
            "audio_file": bpy.path.abspath(source.pbraudio.source_file) 
                          if source.pbraudio.source_file.startswith('//') 
                          else source.pbraudio.source_file
        }
        
        if source.pbraudio.source_type == 'PLANE':
            config["size"] = [
                source.pbraudio.source_planar_height,
                source.pbraudio.source_planar_width
            ]
        elif source.pbraudio.source_type == 'SPHERE':
            config["size"] = source.pbraudio.source_sphere_size
        
        return config
    
    def get_output_config(self, output):
        """Get output-specific configuration"""
        config = {
            "type": output.pbraudio.output_type,
            "size": output.pbraudio.output_size
        }
        
        if output.pbraudio.output_type == 'AMBI':
            config.update({
                "order": output.pbraudio.ambisonic_order,
                "spatial_arrangement_file": bpy.path.abspath(output.pbraudio.spatial_arrangement_file)
                                           if output.pbraudio.spatial_arrangement_file.startswith('//')
                                           else output.pbraudio.spatial_arrangement_file
            })
        elif output.pbraudio.output_type == 'MONO':
            config.update({
                "microphone_type": output.pbraudio.mono_mic_type,
                "calibration_file": bpy.path.abspath(output.pbraudio.output_cal_file)
                                   if output.pbraudio.output_cal_file.startswith('//')
                                   else output.pbraudio.output_cal_file
            })
        
        return config
    
    def update_config_with_objects(self):
        """Update configuration with exported objects"""
        # Remove invalid objects and update references
        self.cleanup_object_references()
        
        # Add objects to config
        self.config["objects"] = self.objects
        self.config["sources"] = self.sources
        self.config["outputs"] = self.outputs
        self.config["environments"] = self.environments
    
    def cleanup_object_references(self):
        """Clean up object references (connected and shard objects)"""
        # Clean connected object references
        for obj_config in self.objects:
            connected = obj_config.get("connected", False)
            if isinstance(connected, list):
                # Remove invalid objects
                connected = [conn for conn in connected 
                           if conn[0] not in self.not_valid]
                
                # Replace names with indices
                for i, conn in enumerate(connected):
                    name = conn[0]
                    for target_obj in self.objects:
                        if target_obj["name"] == name:
                            connected[i][0] = target_obj["idx"]
                            break
                
                obj_config["connected"] = connected if connected else False
        
        # Clean shard object references
        for obj_config in self.objects:
            shard = obj_config.get("shard", False)
            if isinstance(shard, list):
                # Remove invalid objects
                shard = [s for s in shard if s not in self.not_valid]
                
                # Replace names with indices and mark as shard
                for i, shard_name in enumerate(shard):
                    for target_obj in self.objects:
                        if target_obj["name"] == shard_name:
                            shard[i] = target_obj["idx"]
                            # Mark as shard and set fracture frame
                            target_obj["is_shard"] = obj_config.get("fractured", False)
                            break
                
                obj_config["shard"] = shard if shard else False
        
        # Remove invalid objects from main list
        self.objects = [obj for obj in self.objects if obj["name"] not in self.not_valid]

    def save_config(self):
        """Save configuration to JSON file"""
        config_file = os.path.join(self.render_path, "config.json")
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, dict):
                return {key: convert_for_json(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            else:
                return obj
        
        config_json = convert_for_json(self.config)

        with open(config_file, 'w') as f:
            ast.literal_eval(json.dump(config_json, f, indent=2, separators=(',', ': ')))
        
        print(f"Configuration saved to: {config_file}")
        return config_file
    
    def export(self, start_frame=None, end_frame=None):
        """Main export method - exports the complete scene"""
        print("Starting scene export...")
        
        try:
            # Export scene data
            self.export_scene(start_frame, end_frame)
            
            # Save configuration
            config_path = self.save_config()
            
#            print(f"Export completed successfully!")
            print(f"Exported {len(self.objects)} mesh objects")
            print(f"Exported {len(self.sources)} sound sources")
            print(f"Exported {len(self.outputs)} sound outputs")
            print(f"Exported {len(self.environments)} environments")
#            print(f"Configuration saved to: {config_path}")
            
            return True
            
        except Exception as e:
            print(f"Export failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

