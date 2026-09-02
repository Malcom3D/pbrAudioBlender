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
import os
from mathutils import Vector, Quaternion, Matrix
from typing import Dict, List, Tuple, Optional, Set

class ParticleExporter:
    """Exporter for Blender particle systems to 3DGS-compatible format"""
    
    def __init__(self, scene: bpy.types.Scene, decimals: int = 18):
        self.scene = scene
        self.decimals = decimals
        self.scale_factor = 1.0  # Blender units to meters
        
        # Track particle data across frames
        self.particle_data = {}  # particle_id -> {frame: data}
        self.particle_states = {}  # particle_id -> 'alive', 'unborn', 'dead'
        
        # For consistent indexing
        self.master_particle_list = []  # List of particle identifiers
        self.particle_index_map = {}  # identifier -> index
        
    def _get_particle_identifier(self, obj: bpy.types.Object, psys: bpy.types.ParticleSystem, particle: bpy.types.Particle) -> str:
        """Create a unique identifier for a particle"""
        # Use particle.id if available, otherwise use index
        if hasattr(particle, 'id') and particle.id != -1:
            return f"{obj.name}_{psys.name}_{particle.id}"
        else:
            # Fallback to persistent index if available
            if hasattr(particle, 'persistent_index'):
                return f"{obj.name}_{psys.name}_{particle.persistent_index}"
            else:
                # Use the particle's index in the system
                return f"{obj.name}_{psys.name}_{particle.index}"
    
    def _get_particle_rotation(self, particle: bpy.types.Particle) -> Tuple[float, float, float, float]:
        """Extract particle rotation as quaternion"""
        if hasattr(particle, 'rotation') and particle.rotation:
            # Particle has explicit rotation
            return particle.rotation
        else:
            # Calculate rotation from velocity direction
            velocity = particle.velocity
            if velocity.length > 0.001:
                # Create rotation that aligns Z axis with velocity
                direction = velocity.normalized()
                quat = Vector((0, 0, 1)).rotation_difference(direction)
                return quat
            else:
                # Default rotation
                return Quaternion((1, 0, 0, 0))
    
    def _get_particle_size(self, particle: bpy.types.Particle, psys: bpy.types.ParticleSystem) -> Tuple[float, float, float]:
        """Extract particle size (can be anisotropic with size_random)"""
        # Base size
        base_size = particle.size
        
        # Check if particle system uses size randomization
        if psys.settings.use_size_random:
            # Particle size is already randomized per-particle
            size_x = size_y = size_z = base_size
        else:
            size_x = size_y = size_z = base_size
        
        # Check for anisotropic scaling (if available)
        if hasattr(particle, 'size_x'):
            size_x = particle.size_x
        if hasattr(particle, 'size_y'):
            size_y = particle.size_y
        if hasattr(particle, 'size_z'):
            size_z = particle.size_z
        
        # Apply scale factor
        size_x *= self.scale_factor
        size_y *= self.scale_factor
        size_z *= self.scale_factor
        
        return (size_x, size_y, size_z)
    
    def _get_particle_position(self, particle: bpy.types.Particle, obj: bpy.types.Object) -> Tuple[float, float, float]:
        """Get particle position in world space"""
        # Particle location is in object space
        location = particle.location * self.scale_factor
        
        # Transform to world space
        world_location = obj.matrix_world @ location
        
        return (world_location.x, world_location.y, world_location.z)
    
    def _get_particle_euler_rotation(self, quat: Quaternion) -> Tuple[float, float, float]:
        """Convert quaternion to euler rotation (rot_0, rot_1, rot_2)"""
        # Convert to euler
        euler = quat.to_euler('XYZ')
        return (euler.x, euler.y, euler.z)
    
    def _collect_particles_at_frame(self, obj: bpy.types.Object, psys: bpy.types.ParticleSystem, frame: int) -> Dict[str, Dict]:
        """Collect all particles for a given frame"""
        # Set the frame
        self.scene.frame_set(frame)
        
        # Update the scene
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        
        # Get particle system data
        particle_data = {}
        
        # Get the particle system from the evaluated object
        for psys_eval in eval_obj.particle_systems:
            if psys_eval.name != psys.name:
                continue
            
            # Get particles
            particles = psys_eval.particles
            
            # Process each particle
            for particle in particles:
                # Get particle identifier
                identifier = self._get_particle_identifier(obj, psys, particle)
                
                # Check particle state
                is_alive = particle.alive_state == 'ALIVE'
                is_unborn = particle.alive_state == 'UNBORN'
                is_dead = particle.alive_state == 'DEAD'
                
                # Skip particles that are not alive and have no data
                if is_unborn and not hasattr(particle, 'location'):
                    continue
                    
                if is_dead and not hasattr(particle, 'location'):
                    continue
                
                # Get particle data
                if is_alive:
                    position = self._get_particle_position(particle, obj)
                    rotation = self._get_particle_rotation(particle)
                    size = self._get_particle_size(particle, psys)
                    
                    # Convert to euler
                    rot_0, rot_1, rot_2 = self._get_particle_euler_rotation(rotation)
                    
                    particle_data[identifier] = {
                        'position': position,
                        'rotation': (rot_0, rot_1, rot_2),
                        'size': size,
                        'state': 'alive'
                    }
                elif is_unborn:
                    # Store placeholder data for unborn particles
                    particle_data[identifier] = {
                        'position': (0, 0, 0),
                        'rotation': (0, 0, 0),
                        'size': (0, 0, 0),
                        'state': 'unborn'
                    }
                elif is_dead:
                    # Store placeholder data for dead particles
                    # Try to get last known position
                    if hasattr(particle, 'prev_location'):
                        position = self._get_particle_position_from_prev(particle, obj)
                    else:
                        position = (0, 0, 0)
                    
                    particle_data[identifier] = {
                        'position': position,
                        'rotation': (0, 0, 0),
                        'size': (0, 0, 0),
                        'state': 'dead'
                    }
            
            # Handle children particles
            if psys.settings.child_nbr > 0:
                child_particles = psys_eval.child_particles
                for child in child_particles:
                    identifier = self._get_particle_identifier(obj, psys, child)
                    
                    if child.alive_state == 'ALIVE':
                        position = self._get_particle_position(child, obj)
                        rotation = self._get_particle_rotation(child)
                        size = self._get_particle_size(child, psys)
                        
                        rot_0, rot_1, rot_2 = self._getget_particle_euler_rotation(rotation)
                        
                        particle_data[identifier] = {
                            'position': position,
                            'rotation': (rot_0, rot_1, rot_2),
                            'size': size,
                            'state':': 'alive'
                        }
                    elif child.alive_state == 'UNBORN':
                        particle_data[identifier] = {
                            'position': (0, 0, 0),
                            'rotation': (0, 0, 0),
                            'size': (0, 0, 0),
                            'state': 'unborn'
                        }
                    elif child.alive_state == 'DEAD':
                        particle_data[identifier] = {
                            'position': (0, 0, 0),
                            'rotation': (0, 0, 0),
                            'size': (0, 0, 0),
                            'state': 'dead'
                        }
        
        return particle_data
    
    def _get_particle_position_from_prev(self, particle: bpy.types.Particle, obj: bpy.types.Object) -> Tuple[float, float, float]:
        """Get particle position from previous frame"""
        # Use previous location if available
        if hasattr(particle, 'prev_location'):
            location = particle.prev_location * self.scale_factor
            world_location = obj.matrix_world @ location
            return (world_location.x, world_location.y, world_location.z)
        return (0, 0, 0)
    
    def _build_master_particle_list(self, all_particles: List[Dict[str, Dict]], start_frame: int, end_frame: int) -> None:
        """Build the master list of all particles for consistent indexing"""
        self.master_particle_list = []
        self.particle_index_map = {}
        
        # Collect all unique particle identifiers
        for frame_data in all_particles:
            for identifier in frame_data.keys():
                if identifier not in self.particle_index_map:
                    self.particle_index_map[identifier] = len(self.master_particle_list)
                    self.master_particle_list.append(identifier)
    
    def _is_particle_static(self, particle_data: List[Dict], particle_id: str) -> bool:
        """Check if a particle is static across all frames"""
        positions = []
        rotations = []
        sizes = []
        
        for frame_data in particle_data:
            if particle_id in frame_data:
                data = frame_data[particle_id]
                if data['state'] == 'alive':
                    positions.append(data['position'])
                    rotations.append(data['rotation'])
                    sizes.append(data['size'])
        
        if len(positions) < 2:
            return True  # Not enough data to determine movement
        
        # Check if all positions are the same
        positions_array = np.array(positions)
        rotations_array = np.array(rotations)
        sizes_array = np.array(sizes)
        
        position_static = np.all(np.abs(positions_array - positions_array[0]) < 1e-6)
        rotation_static = np.all(np.abs(rotations_array - rotations_array[0]) < 1e-6)
        size_static = np.all(np.abs(sizes_array - sizes_array[0]) < 1e-6)
        
        return position_static and rotation_static and size_static
    
    def export_particle_system(self, obj: bpy.types.Object, particle_idx: int, psys: bpy.types.ParticleSystem, output_path: str, start_frame: int = None, end_frame: int = None):
        """
        Export a particle system to per-frame npz files.
        
        Args:
            obj: The object with the particle system
            particle_idx: the particle id for the exported collection
            psys: The particle system to export
            output_path: Directory to save the npz files
            start_frame: First frame to export (default: scene.frame_start)
            end_frame: Last frame to export (default: scene.frame_end)
        """
        particle_config = {}
        particle_config['idx'] = particle_idx

        if start_frame is None:
            start_frame = self.scene.frame_start
        if end_frame is None:
            end_frame = self.scene.frame_end
        
        # Get the particle system name for file naming
        psys_name = psys.name.replace('.', '_')
        obj_name = obj.name.replace('.', '_')

        particle_config['name'] = f"{obj_name}_{psys_name}"
        
        output_path = f"{output_path}/{obj_name}_{psys_name}"

        particle_config['obj_path'] = output_path

        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        # Collect particle data for all frames
        all_particles = []
        for frame in range(start_frame, end_frame + 1):
            frame_data = self._collect_particles_at_frame(obj, psys, frame)
            all_particles.append(frame_data)
        
        # Build master particle list for consistent indexing
        self._build_master_particle_list(all_particles, start_frame, end_frame)
        
        # Check if the entire particle system is static
        is_system_static = True
        for particle_id in self.master_particle_list:
            if not self._is_particle_static(all_particles, particle_id):
                is_system_static = False
                break
        
        particle_config['static'] = is_system_static

        # Get acoustic shader based on particle system render type
        acoustic_shader = self._get_particle_acoustic_shader(obj, psys, particle_config)
        particle_config['acoustic_shader'] = acoustic_shader

        if is_system_static:
            # Export single frame for static system
            self._export_particle_frame(all_particles[0], 0, output_path, obj_name, psys_name, static=True, start_frame=start_frame)
        else:
            # Export all frames
            for i, frame_data in enumerate(all_particles):
                frame = start_frame + i
                self._export_particle_frame(frame_data, frame, output_path, obj_name, psys_name)
        
        print(f"Exported particle system '{psys.name}' from {start_frame} to {end_frame}")
        print(f"  Total particles: {len(self.master_particle_list)}")
        print(f"  Static: {is_system_static}")

        return particle_config

    def _get_particle_acoustic_shader(self, obj: bpy.types.Object, psys: bpy.types.ParticleSystem, particle_config: dict) -> dict:
        """
        Get the acoustic shader for a particle system based based on its render type.
        
        Returns:
            dict: Acoustic shader properties
        """
        # Get the render type of the particle system
        render_type = psys.settings.render_type
        
        # Default: use emitter's acoustic material
        acoustic_shader = self._get_acoustic_shader_from_object(obj)
        
        if render_type == 'OBJECT':
            # Particle system renders as an object - use that object's material
            if psys.settings.instance_object:
                instance_obj = psys.settings.instance_object
                acoustic_shader = self._get_acoustic_shader_from_object(instance_obj)
        
        elif render_type == 'COLLECTION':
            # Particle system renders as a collection - split per material
            # This will be handled in export_particle_system_by_material()
            # For now, use the first material found in the collection
            if psys.settings.instance_collection:
                collection = psys.settings.instance_collection
                for collection_obj in collection.objects:
                    if collection_obj.type == 'MESH':
                        acoustic_shader = self._get_acoustic_shader_from_object(collection_obj)
                        break
        
        return acoustic_shader

    def _get_acoustic_shader_from_object(self, obj: bpy.types.Object) -> dict:
        """
        Extract acoustic shader from an object's material node tree.
        
        Args:
            obj: Blender object with material
            
        Returns:
            dict: Acoustic shader properties or empty dict if none found
        """
        acoustic_shader = {}
        
        # Check if object has the pbraudio property
        if hasattr(obj, 'pbraudio') and hasattr(obj.pbraudio, 'nodetree'):
            nodetree = obj.pbraudio.nodetree
            if nodetree is not None:
                for node in nodetree.nodes.values():
                    if node.pbraudio_type == 'MaterialOutput':
                        acoustic_shader = self._traverse_acoustic_node_tree(node)
                        break
        
        return acoustic_shader

    def _traverse_acoustic_node_tree(self, node) -> dict:
        """
        Traverse the acoustic node tree to extract properties.
        
        Args:
            node: Starting node (MaterialOutput)
            
        Returns:
            dict: Acoustic properties
        """
        acoustic_dict = {'type': node.pbraudio_type}
        
        # Handle inputs recursively
        for input_socket in node.inputs:
            if input_socket.is_linked:
                linked_node = input_socket.links[0].from_node
                linked_data = self._traverse_acoustic_node_tree(linked_node)
                
                # Merge based on node type
                if linked_data['type'] == 'AcousticShader':
                    acoustic_dict.update(linked_data)
                elif linked_data['type'] == 'AcousticProperties':
                    acoustic_dict['acoustic_properties'] = linked_data
        
        # Extract node properties
        for prop_name in node.bl_rna.properties.keys():
            if prop_name.startswith('pbraudio_'):
                prop_value = getattr(node, prop_name)
                
                # Apply unit conversions
                if 'young_modulus' in prop_name:
                    prop_value *= 1e9
                elif 'damping' in prop_name:
                    prop_value *= 0.01
                
                prop_attr = prop_name.replace('pbraudio_', '')
                if not ((node.pbraudio_type == 'AcousticProperties') and (prop_attr in acoustic_dict.keys())):
                    acoustic_dict[prop_attr] = prop_value
        
        return acoustic_dict

    def export_particle_system_by_material(self, obj: bpy.types.Object, particle_idx: int, psys: bpy.types.ParticleSystem, output_path: str, start_frame: int = None, end_frame: int = None):
        """
        Export a particle system split by material when rendering as collection with multiple materials.
        
        Args:
            obj: The object with the particle system
            particle_idx: the particle id for the exported collection
            psys: The particle system to export
            output_path: Directory to save the npz files
            start_frame: First frame to export (default: scene.frame_start)
            end_frame: Last frame to export (default: scene.frame_end)
        """
        if psys.settings.render_type != 'COLLECTION':
            # Not a collection render - use standard export
            return self.export_particle_system(obj, particle_idx, psys, output_path, start_frame, end_frame)
        
        if not psys.settings.instance_collection:
            # No collection assigned - use standard export
            return self.export_particle_system(obj, particle_idx, psys, output_path, start_frame, end_frame)
        
        collection = psys.settings.instance_collection
        
        # Get all materials from the collection objects
        materials = {}
        for collection_obj in collection.objects:
            if collection_obj.type == 'MESH':
                for material_slot in collection_obj.material_slots:
                    if material_slot.material:
                        mat_name = material_slot.material.name
                        if mat_name not in materials:
                            materials[mat_name] = {
                                'object': collection_obj,
                                'acoustic_shader': self._get_acoustic_shader_from_object(collection_obj)
                            }
        
        if len(materials) == 1:
            # Only one material - use standard export
            return self.export_particle_system(obj, particle_idx, psys, output_path, start_frame, end_frame)
        
        # Multiple materials - split by material
        # This is a simplified approach - for proper per-material splitting,
        # you would need to track which particles use which material
        # For now, we'll export the full system with the first material's shader
        # and note the other materials in the config
        
        particle_config = self.export_particle_system(obj, particle_idx, psys, output_path, start_frame, end_frame)
        
        # Add material information to the config
        particle_config['materials'] = {
            mat_name: {
                'acoustic_shader': mat_data['acoustic_shader']
            }
            for mat_name, mat_data in materials.items()
        }
        
        return particle_config

    def _export_particle_frame(self, frame_data: Dict[str, Dict], frame: int, output_path: str, 
                              obj_name: str, psys_name: str, static: bool = False, start_frame: int = None):
        """
        Export a single frame of particle data to npz format.
        
        The format follows the 3DGS PLY structure:
        - position: (x, y, z)
        - rotation: (rot_0, rot_1, rot_2) - euler angles
        - size: (size_x, size_y, size_z)
        """
        num_particles = len(self.master_particle_list)
        
        # Initialize arrays
        positions = np.zeros((num_particles, 3), dtype=np.float32)
        rotations = np.zeros((num_particles, 3), dtype=np.float32)
        sizes = np.zeros((num_particles, 3), dtype=np.float32)
        states = np.zeros(num_particles, dtype=np.int8)  # 0=dead, 1=alive, 2=unborn
        
        # Fill arrays
        for particle_id, index in self.particle_index_map.items():
            if particle_id in frame_data:
                data = frame_data[particle_id]
                positions[index] = data['position']
                rotations[index] = data['['rotation']
                sizes[index] = data['size']
                
                if data['state'] == 'alive':
                    states[index] = 1
                elif data['state'] == 'unborn':
                    states[index] = 2
                else:  # dead
                    states[index] = 0
            else:
                # Particle not in this frame - mark as dead
                states[index] = 0
        
        # Round to specified decimals
        if self.decimals is not None:
            positions = np.round(positions, self.decimals)
            rotations = np.round(rotations, self.decimals)
            sizes = np.round(sizes, self.decimals)
        
        # Create data dictionary
        data = {
            'positions': positions,
            'rotations': rotations,
            'sizes': sizes,
            'states': states,
            'particle_count': num_particles
        }
        
        # Save to file
        if static:
            filename = f"{obj_name}_{psys_name}.npz"
        else:
            filename = f"{obj_name}_{psys_name}_{frame:05d}.npz"
        
        output_file = os.path.join(output_path, filename)
        np.savez_compressed(output_file, **data)
        
        print(f"  Exported frame {frame}: {num_particles} particles -> {filename}")
    
    # Update the export_all_particle_systems method to use per-material splitting:
    def export_all_particle_systems(self, obj: bpy.types.Object, output_path: str, start_frame: int = None, end_frame: int = None):
        """Export all particle systems on an object"""
        if not obj.particle_systems:
            print(f"Object '{obj.name}' has no particle systems")
            return

        for particle_idx, psys in enumerate(obj.particle_systems):
            self.export_particle_system_by_material(obj, particle_idx, psys, output_path, start_frame, end_frame)
