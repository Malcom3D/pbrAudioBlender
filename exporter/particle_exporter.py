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
    
    def __init__(self, scene: bpy.types.Scene, decimals: int = 18, chunk_size: int = 10000):
        self.scene = scene
        self.decimals = decimals
        self.scale_factor = 1.0  # Blender units to meters
        self.chunk_size = chunk_size  # Process particles in chunks
        
        # Track particle data across frames
        self.particle_data = {}  # particle_id -> {frame: data}
        self.particle_states = {}  # particle_id -> 'alive', 'unborn', 'dead'
        
        # For consistent indexing
        self.master_particle_list = []  # List of particle identifiers
        self.particle_index_map = {}  # identifier -> index
        
    def _get_particle_rotation(self, particle: bpy.types.Particle) -> Tuple[float, float, float, float]:
        """Extract particle rotation as quaternion"""
        if hasattr(particle, 'rotation') and particle.rotation:
            # Particle has explicit rotation
            return particle.rotation
        else:
            # Calculate rotation from velocity direction
            velocity = particle.velocity
            if velocity.length > 0.001:
                # Create Create rotation that aligns Z axis with velocity
                direction = velocity.normalized()
                quat = Vector((0, 0, 1)).rotation_difference(direction)
                return quat
            else:
                # Default rotation
                return Quaternion((1, 0, 0, 0))
    
    def _get_particle_size(self, particle: bpy.types.Particle, psys: bpy.types.ParticleSystem) -> Tuple[float, float, float]:
        """Extract particle size (can be anisotropic with size_random)"""
        # Base size
        size_x = size_y = size_z = particle.size
        
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
            for index, particle in particles.items():
                # Get particle identifier
                identifier = f"{obj.name}_{psys.name}_{index}"
                
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
            child_particles = psys_eval.child_particles
            for index, child in child_particles.items():
                identifier = f"{obj.name}_{psys.name}_{psys.settings.child_type}_{index}"
                
                if child.alive_state == 'ALIVE':
                    position = self._get_particle_position(child, obj)
                    rotation = self._get_particle_rotation(child)
                    size = self._get_particle_size(child, psys)
                    
                    rot_0, rot_1, rot_2 = self._get_particle_euler_rotation(rotation)
                    
                    particle_data[identifier] = {
                        'position': position,
                        'rotation': (rot_0, rot_1, rot_2),
                        'size': size,
                        'state': 'alive'
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
    
    def _export_particle_frame(self, frame_data: Dict[str, Dict], frame: int, output_path: str, obj_name: str, psys_name: str, static: bool = False, start_frame: int = None):
        """
        Export a single frame of particle data to npz format.
        
        The format follows the 3DGS PLY structure:
:
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
                rotations[index] = data['rotation']
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
        
        # Clear frame data to free memory
        del frame_data
        del data
    
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
        particle_config['proxy'] = obj.pbraudio.particles_proxy
        
        output_path = f"{output_path}/{obj_name}_{psys_name}"

        particle_config['obj_path'] = output_path

        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        # First pass: Collect particle identifiers across all frames
        # This is done without storing all frame data
        print("First pass: Collecting particle identifiers...")
        
        # Use a set to track unique particles across frames
        all_particle_ids = set()
        
        # Process frames in the first pass to collect particle IDs
        for frame in range(start_frame, end_frame + 1):
            frame_data = self._collect_particles_at_frame(obj, psys, frame)
            
            # Add all particle IDs from this frame
            for particle_id in frame_data.keys():
                all_particle_ids.add(particle_id)
            
            # Clear frame data to free memory
            del frame_data
        
        # Build master particle list
        self.master_particle_list = list(all_particle_ids)
        self.particle_index_map = {particle_id: idx for idx, particle_id in enumerate(self.master_particle_list)}
        
        # Clear the set as we have the list now
        del all_particle_ids
        
        print(f"Total unique particles: {len(self.master_particle_list)}")
        
        # Check if the entire particle system is static
        # We'll check a few frames to determine if static
        is_system_static = self._is_system_static(obj, psys, start_frame, end_frame)
        
        particle_config['static'] = is_system_static

        # Get acoustic shader based on particle system render type
        acoustic_shader = self._get_particle_acoustic_shader(obj, psys, particle_config)
        particle_config['acoustic_shader'] = acoustic_shader

        # Second pass: Export frames
        print("Second pass: Exporting frames...")
        
        if is_system_static:
            # Export single frame for static system
            frame_data = self._collect_particles_at_frame(obj, psys, start_frame)
            self._export_particle_frame(frame_data, 0, output_path, obj_name, psys_name, static=True, start_frame=start_frame)
            del frame_data  # Free memory
        else:
            # Export all frames
            for i, frame in enumerate(range(start_frame, end_frame + 1)):
                frame_data = self._collect_particles_at_frame(obj, psys, frame)
                self._export_particle_frame(frame_data, frame, output_path, obj_name, psys_name)
                del frame_data  # Free memory after each frame
        
        print(f"Exported particle system '{psys.name}' from {start_frame} to {end_frame}")
        print(f"  Total particles: {len(self.master_particle_list)}")
        print(f"  Static: {is_system_static}")

        # Clear memory
        self.master_particle_list = []
        self.particle_index_map = {}

        return particle_config

    def _is_system_static(self, obj: bpy.types.Object, psys: bpy.types.ParticleSystem, start_frame: int, end_frame: int) -> bool:
        """
        Check if the particle system is static by sampling frames.
        
        Instead of checking all frames, we sample a few frames to determine if static.
        """
        # Sample up to 3 frames (start, middle, end)
        sample_frames = set()
        sample_frames.add(start_frame)
        sample_frames.add(end_frame)
        sample_frames.add((start_frame + end_frame) // 2)
        
        # Remove duplicates and sort
        sample_frames = sorted(sample_frames)
        
        # Track positions for comparison
        reference_positions = None
        
        for frame in sample_frames:
            frame_data = self._collect_particles_at_frame(obj, psys, frame)
            
            # Get alive particles positions
            current_positions = {}
            for particle_id, data in frame_data.items():
                if data['state'] == 'alive':
                    current_positions[particle_id] = data['position']
            
            if reference_positions is not None:
                # Compare with reference
                if set(current_positions.keys()) != set(reference_positions.keys()):
                    del frame_data
                    return False
                
                # Check if positions are the same
                for particle_id in current_positions:
                    if particle_id in reference_positions:
                        pos1 = np.array(current_positions[particle_id])
                        pos2 = np.array(reference_positions[particle_id])
                        if not np.allclose(pos1, pos2, atol=1e-6):
                            del frame_data
                            return False
                    else:
                        del frame_data
                        return False
            
            reference_positions = current_positions
            del frame_data  # Free memory
        
        return True

    def _get_particle_acoustic_shader(self, obj: bpy.types.Object, psys: bpy.types.ParticleSystem, particle_config: dict) -> dict:
        """
        Get the acoustic shader for a particle system based based on its render type.
        
        Returns:
            dict: Acoustic shader properties
        """
        # Get the render type of the particle system
        render_type = psys.settings.render_type
        
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
        else:
            # Default: use emitter's acoustic material
            acoustic_shader = self._get_acoustic_shader_from_object(obj)
        
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
            obj: The object with with the particle system
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
        material_to_object = {}  # Map material name to object name
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
                            material_to_object[mat_name] = collection_obj.name
        
        if len(materials) == 1:
            # Only one material - use standard export
            return self.export_particle_systemystem(obj, particle_idx, psys, output_path, start_frame, end_frame)
        
        # Multiple materials - split by material
        if start_frame is None:
            start_frame = self.scene.frame_start
        if end_frame is None:
            end_frame = self.scene.frame_end
        
        # Get the particle system name for file naming
        psys_name = psys.name.replace('.', '_')
        obj_name = obj.name.replace('.', '_')
        
        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        # For each material, we'll do two passes (collect IDs, then export)
        material_configs = []
        
        for mat_name, mat_data in materials.items():
            # Create material-specific output path
            mat_psys_name = f"{psys_name}_{mat_name.replace('.', '_')}"
            mat_output_path = f"{output_path}/{obj_name}_{mat_psys_name}"
            os.makedirs(mat_output_path, exist_ok=True)
            
            # First pass: Collect particle IDs for this material
            print(f"First pass for material {mat_name}: Collecting particle identifiers...")
            all_particle_ids = set()
            
            for frame in range(start_frame, end_frame + 1):
                frame_data = self._collect_particles_at_frame(obj, psys, frame)
                
                # Filter particles by material
                for particle_id, data in frame_data.items():
                    if self._particle_belongs_to_material(particle_id, mat_name, material_to_object):
                        all_particle_ids.add(particle_id)
                
                del frame_data  # Free memory
            
            if len(all_particle_ids) == 0:
                continue  # No particles for this material
            
            # Build master particle list for this material
            self.master_particle_list = list(all_particle_ids)
            self.particle_index_map = {pid: idx for idx, pid in enumerate(self.master_particle_list)}
            
            del all_particle_ids
            
            # Check if this material's particles are static
            is_material_static = self._is_material_static(obj, psys, start_frame, end_frame, mat_name, material_to_object)
            
            # Create material-specific config
            material_config = {
                'idx': particle_idx,
                'name': f"{obj_name}_{mat_psys_name}",
                'obj_path': mat_output_path,
                'static': is_material_static,
                'acoustic_shader': mat_data['acoustic_shader']
            }
            
            # Second pass: Export frames for this material
            print(f"Second pass for material {mat_name}: Exporting frames...")
            
            if is_material_static:
                # Export single frame for static material
                frame_data = self._collect_particles_at_frame(obj, psys, start_frame)
                # Filter by material
                filtered_data = {pid: data for pid, data in frame_data.items() 
                               if self._particle_belongs_to_material(pid, mat_name, material_to_object)}
                self._export_particle_frame(filtered_data, 0, mat_output_path, obj_name, mat_psys_name, static=True, start_frame=start_frame)
                del frame_data, filtered_data
            else:
                # Export all frames for this material
                for frame in range(start_frame, end_frame + 1):
                    frame_data = self._collect_particles_at_frame(obj, psys, frame)
                    # Filter by material
                    filtered_data = {pid: data for pid, data in frame_data.items() 
                                   if self._particle_belongs_to_material(pid, mat_name, material_to_object)}
                    self._export_particle_frame(filtered_data, frame, mat_output_path, obj_name, mat_psys_name)
                    del frame_data, filtered_data
            
            material_configs.append(material_config)
            particle_idx += 1
            
            # Clear memory after each material
            self.master_particle_list = []
            self.particle_index_map = {}
        
        # If we have material configs, return the first one with materials info
        if material_configs:
            # Store all material configs for later processing
            self._material_configs = material_configs
            
            # Return the first config with all materials info
            first_config = material_configs[0].copy()
            first_config['materials'] = {
                mat_name: {
                    'acoustic_shader': mat_data['acoustic_shader']
                }
                for mat_name, mat_data in materials.items()
                if any(config['name'].endswith(mat_name.replace('.', '_')) for config in material_configs)
            }
            
            return first_config
        
        # No materials found - fallback to standard export
        return self.export_particle_system(obj, particle_idx, psys, output_path, start_frame, end_frame)

    def _particle_belongs_to_material(self, particle_id: str, mat_name: str, material_to_object: dict) -> bool:
        """
        Helper method to determine if a particle belongs to a specific material.
        This is a simplified version - in reality, you'd need to track which object each particle instances.
        """
        # For now, distribute particles evenly among materials based on hash
        # This is a placeholder - you should implement proper material assignment
        particle_hash = hash(particle_id) % len(material_to_object)
        mat_names = list(material_to_object.keys())
        return mat_names[particle_hash] == mat_name

    def _is_material_static(self, obj, psys, start_frame, end_frame, mat_name, material_to_object) -> bool:
        """
        Check if particles for a specific material are static.
        """
        # Sample a few frames
        sample_frames = sorted(set([start_frame, end_frame, (start_frame + end_frame) // 2]))
        
        reference_positions = None
        
        for frame in sample_frames:
            frame_data = self._collect_particles_at_frame(obj, psys, frame)
            
            # Filter by material
            current_positions = {}
            for particle_id, data in frame_data.items():
                if data['state'] == 'alive' and self._particle_belongs_to_material(particle_id, mat_name, material_to_object):
                    current_positions[particle_id] = data['position']
            
            if reference_positions is not None:
                if set(current_positions.keys()) != set(reference_positions.keys()):
                    del frame_data
                    return False
                
                for particle_id in current_positions:
                    if particle_id in reference_positions:
                        pos1 = np.array(current_positions[particle_id])
                        pos2 = np.array(reference_positions[particle_id])
                        if not np.allclose(pos1, pos2, atol=1e-6):
                            del frame_data
                            return False
                    else:
                        del frame_data
                        return False
            
            reference_positions = current_positions
            del frame_data
        
        return True

    def _get_particle_material(self, particle, psys, collection, material_to_object):
        """
        Determine which material a particle uses based on its instance object.
        
        For collection rendering, particles instance objects from the collection.
        We need to figure out which object each particle instances and thus which material it uses.
        """
        # Check if particle has instance information
        if hasattr(particle, 'instanceinstance_object') and particle.instance_object:
            # Direct instance object reference
            if particle.instance_object.name in material_to_object.values():
                # Find the material for this object
                for mat_name, obj_name in material_to_object.items():
                    if particle.instance_object.name == obj_name:
                        return mat_name
        elif hasattr(particle, 'instance_collection') and particle.instance_collection:
            # Instance collection - check which object in the collection
            pass
        else:
            # For collection rendering, particles are distributed among collection objects
            # We can use the particle's index or random value to determine which object it instances
            # This is a simplified approach - in reality, Blender uses a more complex distribution
            
            # Get the collection objects objects that have materials
            mat_objects = list(material_to_object.keys())
            if not mat_objects:
                return None
            
            # Use particle's random value or index to distribute
            if hasattr(particle, 'random'):
                # Use particle's random value for distribution
                random_value = particle.random
            elif hasattr(particle, 'index'):
                # Use particle index as fallback
                random_value = particle.index / max(psys.settings.count, 1)
            else:
                random_value = 0.5
            
            # Simple distribution based on random value
            # This assumes equal distribution among objects
            # For more accurate results, you'd need to check the actual instance
            num_objects = len(mat_objects)
            object_idx = int(random_value * num_objects)
            object_idx = min(object_idx, num_objects - 1)
            
            return mat_objects[object_idx]
        
        return None
