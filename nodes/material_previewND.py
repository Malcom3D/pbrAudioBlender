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
import bpy
import numpy as np
import trimesh
import soundfile as sf
import tempfile
import json
import hashlib
import aud
from bpy.types import Node, Operator
from bpy.props import IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

from .baseND import AcousticMaterialNode
from physicsSolver import EntityManager
from physicsSolver.lib.functions import _parse_lib
from rigidBody import Mesh2Modal, RigidBodySynth, ConnectedBuffer

classes = []

@dataclass
class ShapeGeometry:
    """Geometric parameters for test shapes"""
    name: str
    vertices: np.ndarray
    normals: np.ndarray
    faces: np.ndarray
    
    def get_contact_vertices(self, contact_area: float) -> List[int]:
        """Get vertex indices within contact area from center"""
        if len(self.vertices) == 0:
            return []

        mesh = trimesh.Trimesh(vertices=self.vertices, faces_normals=self.normals, faces=self.faces)
        contact_area *= mesh.area

        # Calculate center of mesh
        center = np.mean(self.vertices, axis=0)
        
        # Calculate distances from center
        distances = np.linalg.norm(self.vertices - center, axis=1)
        
        # Find radius based on contact area (assuming circular contact)
        contact_radius = np.sqrt(contact_area / np.pi)
        
        # Get vertices within contact radius
        contact_indices = np.where(distances <= contact_radius)[0].tolist()
        
        return contact_indices if contact_indices else [0]  # At least one vertex
    
    def to_mesh_npz(self, output_file: str) -> None:
        """Save mesh as npz file"""
        np.savez_compressed(output_file, vertices=self.vertices, normals=self.normals, faces=self.faces)

def generate_u_bar(length: float = 0.3, width: float = 0.03, height: float = 0.02, subdivisions: int = 1) -> ShapeGeometry:
    """
    Generate a U-shaped bar (channel section) for decay and brightness evaluation.
    Dimensions are automatically calculated from physical parameters.
    """
    gap = 10.0 # gap between prongs

    # We'll create a simple U shape using trimesh primitives
    # Two parallel prongs connected by a base
    prong1 = trimesh.creation.box(extents=[length*0.45, width, height])
    prong2 = trimesh.creation.box(extents=[length*0.45, width, height])
    base   = trimesh.creation.box(extents=[width, width*2 + gap, height])

    # position prongs
    prong1.apply_translation([length*0.275, -(width/2 + gap/2), 0])
    prong2.apply_translation([length*0.275,  (width/2 + gap/2), 0])
    base.apply_translation([-length*0.05, 0, 0])

    mesh = trimesh.util.concatenate([prong1, prong2, base])

    return ShapeGeometry(
        name=f"U_Bar_{length:.2f}m",
        vertices=mesh.vertices,
        normals=mesh.vertex_normals,
        faces=mesh.faces
    )

def generate_circular_plate(radius: float = 0.05, thickness: float = 0.003, radial_segments: int = 2, circumferential_segments: int = 4) -> ShapeGeometry:
    """
    Generate a thin circular plate for inharmonicity and brightness evaluation.
    """
    sections = radial_segments * circumferential_segments
    mesh = trimesh.creation.cylinder(radius=radius, height=thickness, sections=sections)
    return ShapeGeometry(
        name=f"Circular_Plate_{radius*1000:.0f}mm",
        vertices=mesh.vertices,
        normals=mesh.vertex_normals,
        faces=mesh.faces
    )

def generate_solid_bar(length: float = 0.2, radius: float = 0.008, length_segments: int = 2, radial_segments: int = 2) -> ShapeGeometry:
    """
    Generate a solid cylindrical bar (free-free) for tonal balance evaluation.
    """
    width, height = (2*radius for _ in range(2))
    mesh = trimesh.creation.box(extents=[length, width, height])

    return ShapeGeometry(
        name=f"Solid_Bar_{length*100:.0f}cm",
        vertices=mesh.vertices,
        normals=mesh.vertex_normals,
        faces=mesh.faces
    )

def generate_from_mesh(obj) -> ShapeGeometry:
    """Generate shape geometry from an existing mesh object"""
    # Get mesh data
    mesh = obj.data
    world_matrix = obj.matrix_world
    
    # Get vertices in world space
    vertices = []
    for vert in mesh.vertices:
        world_co = world_matrix @ vert.co
        vertices.append([world_co.x, world_co.y, world_co.z])
    
    # Get faces
    faces = []
    for poly in mesh.polygons:
        if len(poly.vertices) == 3:
            faces.append(list(poly.vertices))
        elif len(poly.vertices) > 3:
            # Triangulate
            for i in range(1, len(poly.vertices) - 1):
                faces.append([poly.vertices[0], poly.vertices[i], poly.vertices[i + 1]])
    
    # Get normals
    normals = []
    for vert in mesh.vertices:
        normal = world_matrix.to_3x3() @ vert.normal
        normals.append([normal.x, normal.y, normal.z])
    
    return ShapeGeometry(
        name=obj.name.replace('.', '_'),
        vertices=np.array(vertices, dtype=np.float32),
        normals=np.array(normals, dtype=np.float32),
        faces=np.array(faces, dtype=np.int32)
    )

def get_cache_path(node) -> str:
#    """Get unique cache path for this node's preview"""
#    # Create a unique hash based on node parameters
#    params = f"{node.preview_shape}_{node.contact_area}_{node.force_value}_{node.impulse_duration}_{node.preview_duration}"
#    
#    # Add acoustic parameters from connected nodes
#    node_tree = node.id_data
#    for n in node_tree.nodes:
#        if hasattr(n, 'pbraudio_type') and n.pbraudio_type == 'AcousticShader':
#            for prop in ['young_modulus', 'poisson_ratio', 'density', 'damping', 'friction', 'roughness', 'low_frequency', 'high_frequency']:
#                if hasattr(n, f'pbraudio_{prop}'):
#                    params += f"_{getattr(n, f'pbraudio_{prop}')}"
    
    # Use Blender's temp directory
    return bpy.app.tempdir

class PBRAUDIO_OT_preview_material(Operator):
    """Preview acoustic material sound"""
    bl_idname = "node.pbraudio_preview_material"
    bl_label = "Preview Material Sound"
    bl_description = "Generate and play preview sound for the acoustic material"
    
    node_tree: StringProperty(name="Node Tree", default="")
    node_name: StringProperty(name="Node Name", default="")
    
    def _get_acoustic_params(self, node) -> Dict:
        """Traverse node tree to get acoustic parameters"""
        params = {
            'young_modulus': 0.005,  # Default values (GPa)
            'poisson_ratio': 0.46,
            'density': 800.0,
            'damping': 5.0,
            'friction': 0.5,
            'roughness': 0.4,
            'low_frequency': 5.0,
            'high_frequency': 24000.0
        }
        
        # Traverse backwards from this node
        def traverse_backwards(current_node):
            if hasattr(current_node, 'inputs'):
                for input_socket in current_node.inputs:
                    if input_socket.is_linked:
                        from_node = input_socket.links[0].from_node
                        # Extract pbraudio properties
                        for prop_name in from_node.bl_rna.properties.keys():
                            if prop_name.startswith('pbraudio_'):
                                prop_value = getattr(from_node, prop_name)
                                attr_name = prop_name.replace('pbraudio_', '')
                                if attr_name in params:
                                    params[attr_name] = prop_value
                        traverse_backwards(from_node)
        
        traverse_backwards(node)
        return params
    
    def _calculate_shape_dimensions(self, params: Dict, shape_type: str) -> Dict:
        """Calculate appropriate shape dimensions based on physical parameters"""
        dimensions = {}
        
        # Calculate characteristic dimensions based on material properties
        young_modulus = params.get('young_modulus', 0.005) * 1e9  # Convert GPa to Pa
        density = params.get('density', 800.0)
        
        # Calculate wave speed in material
        wave_speed = np.sqrt(young_modulus / density) if density > 0 else 1000.0
        
        # Target fundamental frequency range (based on low_frequency)
        target_freq = params.get('low_frequency', 100.0)
        
        if shape_type == 'U_BAR':
            # For a U-bar, fundamental frequency ~ (wave_speed * thickness) / (2 * length^2)
            # We want the fundamental to be near the low_frequency
            thickness = 0.02  # Fixed thickness
            length = np.sqrt(wave_speed * thickness / (2 * target_freq))
            length = np.clip(length, 0.1, 1.0)
            width = length * 0.1  # Width proportional to length
            height = length * 0.07  # Height proportional to length
            
            dimensions = {
                'length': length,
                'width': width,
                'height': height
            }
            
        elif shape_type == 'CIRCULAR_PLATE':
            # For a circular plate, fundamental frequency ~ (wave_speed * thickness) / (2 * radius^2)
            thickness = 0.003  # Fixed thickness
            radius = np.sqrt(wave_speed * thickness / (2 * target_freq))
            radius = np.clip(radius, 0.01, 0.3)
            
            dimensions = {
                'radius': radius,
                'thickness': thickness
            }
            
        else: # SOLID_BAR
            # For a solid bar, fundamental frequency ~ wave_speed / (2 * length)
            length = wave_speed / (2 * target_freq)
            length = np.clip(length, 0.05, 0.5)
            radius = length * 0.04  # Aspect ratio
            
            dimensions = {
                'length': length,
                'radius': radius
            }

        return dimensions
    
    def _create_config(self, node, shape_geo: ShapeGeometry, params: Dict, cache_path: str) -> str:
        """Create configuration JSON for Mesh2Modal"""
        config = {
            "system": {
                "cache_path": os.path.dirname(cache_path),
                "sample_rate": 48000,
                "modal_modes": 6,  # Use 6 modes for preview
                "fps": 120,
                "fps_base": 1.0,
                "subframes": 1
            },
            "objects": [{
                "idx": 0,
                "name": "preview",
                "obj_path": f"{cache_path}/data/preview",
                "pose_path": f"{cache_path}",
                "static": True,
                "acoustic_shader": {
                    "young_modulus": params['young_modulus'] * 1e9,  # Convert GPa to Pa
                    "poisson_ratio": params['poisson_ratio'],
                    "density": params['density'],
                    "damping": params['damping'] / 100.0,  # Convert % to ratio
                    "low_frequency": params['low_frequency'],
                    "high_frequency": params['high_frequency'],
                    "friction": params['friction'],
                    "roughness": params['roughness']
                }
            }]
        }
        
        config_path = os.path.join(cache_path, "config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config_path
    
    def _compute_modal_model(self, cache_path: str, config_path: str) -> Optional[str]:
        """Compute modal model using Mesh2Modal"""
        try:
            # Create EntityManager
            self.entity_manager = EntityManager(config_path)

            # Initialize connected buffer
            connected_buffer = ConnectedBuffer()
            connected_buffer.add_obj(0)
            self.entity_manager.register('connected_buffer', connected_buffer)

            # Use Mesh2Modal to compute modal model
            mesh2modal = Mesh2Modal(self.entity_manager)
            mesh2modal.compute(0)
            
            # Check if lib file was created
            lib_path = os.path.join(cache_path, "dsp/preview.lib")
            if os.path.exists(lib_path):
                return lib_path
            
            return None
            
        except Exception as e:
            print(f"Modal model computation error: {e}")
            return None
    
    def _render_audio(self, cache_path: str, lib_path: str, node, params: Dict, shape_geo: ShapeGeometry) -> Optional[np.ndarray]:
        """Render audio using RigidBodySynth"""
        try:
            # Load config
            config_path = os.path.join(cache_path, "config.json")
            
            # Get sample rate from config
            config = self.entity_manager.get('config')
            sample_rate = 48000
            
            # Calculate duration in samples
            duration_samples = int(node.preview_duration * sample_rate)
            
            # Get vertex list from shape geometry
            vertex_list = np.arange(len(shape_geo.vertices))
            
            # Initialize RigidBodySynth
            rigidbody_synth = RigidBodySynth(entity_manager=self.entity_manager, obj_idx=0, modal_lib=lib_path, vertex_list=vertex_list, sample_rate=sample_rate)
 
            # Get contact vertices
            contact_area = node.contact_area
            vertex_ids = shape_geo.get_contact_vertices(contact_area)
            
            # Render audio
            audio_buffer = np.zeros(duration_samples)
            
            # Impulse excitation (synth_type = 1)
            force_value = node.force_value

            # Calculate impulse
            impulse_duration = node.impulse_duration / 1000
            impulse = force_value * impulse_duration

            # Impulse duration in sample
            impulse_samples = int(impulse_duration * sample_rate)

            # Generate impact envelope (Hertzian asimmetric force profile)
            rise_sample = int(impulse_samples / 2) + 1
            decay_sample = int(impulse_samples / 2)
            t_rise = np.linspace(0, 0.5, int(rise_sample))
            t_decay = np.linspace(0.5, 1, int(decay_sample))
            t = np.concatenate((t_rise, t_decay[1:]))

            force_envelope = force_value * (1 - np.cos(2 * np.pi * t))/2

            # Normalize to match total impulse
            actual_impulse = np.trapz(force_envelope, t)
            if actual_impulse > 0:
                force_envelope = force_envelope * (impulse / actual_impulse)
            
            for sample_idx in range(duration_samples):
                if sample_idx < force_envelope.shape[0]:
                    # Apply impulse at first sample
                    output = rigidbody_synth.process(synth_type=1, vertex_ids=vertex_ids, input_force=force_envelope[sample_idx], contact_area=contact_area)
                else:
                    # Continue processing (no new input)
                    output = rigidbody_synth.process(synth_type=1, vertex_ids=vertex_ids, input_force=0.0, contact_area=contact_area)
                
                audio_buffer[sample_idx] = output if not np.isnan(output) and not np.isinf(output) else 0.0

            # Normalize
            max_val = np.max(np.abs(audio_buffer))
            if max_val > 0:
                audio_buffer = audio_buffer / max_val * 0.95
            
            return audio_buffer
            
        except Exception as e:
            print(f"Audio rendering error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _save_audio(self, audio_buffer: np.ndarray, cache_path: str) -> str:
        """Save rendered audio to file"""
        audio_path = os.path.join(cache_path, "preview.wav")
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        sf.write(audio_path, audio_buffer, 48000, subtype='FLOAT')
        
        return audio_path
    
    def _play_audio(self, audio_path: str, node) -> aud.Handle:
        """Play audio using aud module and return handle"""
        try:
            # Create device
            device = aud.Device()
            
            # Create sound object
            sound = aud.Sound(audio_path)
            
            # Play sound
            handle = device.play(sound)
            
            print(f"Playing preview audio: {audio_path}")
            
            # Close device if audio is played
            while not handle.status:
                if device:
                    try:
                        handle = None
                        device.stopAll()
                        device = None
                    except:
                        pass

        except Exception as e:
            print(f"Error playing audio: {e}")
            return None

    def _cleanup_preview(self, node):
        """Clean up existing preview data"""
        
        # Clear cached paths
        node.cache_path = None
        node.audio_path = None
        node.lib_path = None
    
    def _has_parameters_changed(self, node) -> bool:
        """Check if parameters have changed since last render"""
        if not hasattr(node, '_last_params_hash'):
            return True
        
        current_hash = self._get_params_hash(node)
        return current_hash != node._last_params_hash
    
    def _get_params_hash(self, node) -> str:
        """Get hash of current parameters"""
        params = f"{node.preview_shape}_{node.contact_area}_{node.force_value}_{node.impulse_duration}_{node.preview_duration}"
        
        # Add acoustic parameters from connected nodes
        node_tree = node.id_data
        for n in node_tree.nodes:
            if hasattr(n, 'pbraudio_type') and n.pbraudio_type == 'AcousticShader':
                for prop in ['young_modulus', 'poisson_ratio', 'density', 'damping', 'friction', 'roughness', 'low_frequency', 'high_frequency']:
                    if hasattr(n, f'pbraudio_{prop}'):
                        params += f"_{getattr(n, f'pbraudio_{prop}')}"
        
        return hashlib.md5(params.encode()).hexdigest()
    
    def execute(self, context):
        if not self.node_tree or not self.node_name:
            self.report({'ERROR'}, "No node selected")
            return {'CANCELLED'}
        
        try:
            # Get the node
            nodetree = bpy.data.node_groups.get(self.node_tree)
            if not nodetree:
                self.report({'ERROR'}, "Node tree not found")
                return {'CANCELLED'}
            
            node = nodetree.nodes.get(self.node_name)
            if not node:
                self.report({'ERROR'}, "Node not found")
                return {'CANCELLED'}
            
            # Check if parameters have changed
            if self._has_parameters_changed(node):
                self.report({'INFO'}, "Parameters changed, cleaning up and recomputing...")
                self._cleanup_preview(node)
            
            # Check if we have cached audio
            if hasattr(node, 'audio_path') and node.audio_path and os.path.exists(node.audio_path):
                self.report({'INFO'}, "Playing cached preview...")
                self._play_audio(node.audio_path, node)
                return {'FINISHED'}
 
            # Get acoustic parameters
            params = self._get_acoustic_params(node)
            
            # Calculate shape dimensions from physical parameters
            shape_type = node.preview_shape
            dimensions = self._calculate_shape_dimensions(params, shape_type)
            
            # Generate shape based on type
            if shape_type == 'U_BAR':
                shape_geo = generate_u_bar(
                    length=dimensions.get('length', node.u_bar_length),
                    width=dimensions.get('width', node.u_bar_width),
                    height=dimensions.get('height', node.u_bar_height)
                )
            elif shape_type == 'CIRCULAR_PLATE':
                shape_geo = generate_circular_plate(
                    radius=dimensions.get('radius', node.plate_radius),
                    thickness=dimensions.get('thickness', node.plate_thickness)
                )
            elif shape_type == 'SOLID_BAR':
                shape_geo = generate_solid_bar(
                    length=dimensions.get('length', node.bar_length),
                    radius=dimensions.get('radius', node.bar_radius)
                )
            else:  # MESH_OBJECT
                # Get the mesh object from the node tree
                obj = None
                for o in bpy.data.objects:
                    if hasattr(o, 'pbraudio') and o.pbraudio.nodetree == nodetree:
                        obj = o
                        break
                
                if obj and obj.type == 'MESH':
                    shape_geo = generate_from_mesh(obj)
                else:
                    self.report({'ERROR'}, "No valid mesh object found")
                    return {'CANCELLED'}
            
            # Get cache path
            cache_path = get_cache_path(node)
            os.makedirs(f"{cache_path}/data/preview", exist_ok=True)
            
            # Save mesh as npz
            self.report({'INFO'}, f"Saving mesh to {cache_path}...")
            mesh_path = os.path.join(cache_path, "data/preview/preview.npz")
            shape_geo.to_mesh_npz(mesh_path)
            
            # Create config
            self.report({'INFO'}, "Creating configuration...")
            config_path = self._create_config(node, shape_geo, params, cache_path)
            
            # Compute modal model
            self.report({'INFO'}, "Computing modal model...")
            lib_path = self._compute_modal_model(cache_path, config_path)
            
            if not lib_path:
                self.report({'ERROR'}, "Failed to compute modal model")
                return {'CANCELLED'}
            
            # Render audio
            self.report({'INFO'}, "Rendering preview audio...")
            audio_buffer = self._render_audio(cache_path, lib_path, node, params, shape_geo)
            
            if audio_buffer is None:
                self.report({'ERROR'}, "Failed to render audio")
                return {'CANCELLED'}
            
            # Save audio
            audio_path = self._save_audio(audio_buffer, cache_path)
            
            # Store paths in node for caching
            node.cache_path = cache_path
            node.audio_path = audio_path
            node.lib_path = lib_path
            node.last_params_hash = self._get_params_hash(node)
            
            # Play audio
            self.report({'INFO'}, "Playing preview...")
            self._play_audio(audio_path, node)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Preview error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

classes.append(PBRAUDIO_OT_preview_material)

class AcousticMaterialPreviewNode(AcousticMaterialNode):
    """Acoustic material preview node for modal synthesis evaluation"""
    bl_idname = 'AcousticMaterialPreviewNode'
    bl_label = "Acoustic Material Preview"
    bl_icon = 'PLAY'
    
    pbraudio_type: StringProperty(default='MaterialPreview')

    # Preview tmp path
    cache_path: StringProperty(
        subtype='DIR_PATH',
#        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default=''
    )

    audio_path: StringProperty(
        subtype='FILE_PATH',
#        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default=''
    )

    lib_path: StringProperty(
        subtype='FILE_PATH',
#        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default=''
    )

    # Preview parameters hash
    _last_params_hash: StringProperty(default='')

    # Preview shape selection
    preview_shape: EnumProperty(
        name="Test Shape",
        description="Shape to use for modal analysis preview",
        items=[
            ('U_BAR', "U-Bar", "U-shaped bar for decay and brightness"),
            ('CIRCULAR_PLATE', "Circular Plate", "Thin circular plate for inharmonicity"),
            ('SOLID_BAR', "Solid Bar", "Solid cylindrical bar for tonal balance"),
            ('MESH_OBJECT', "Mesh Object", "Use the mesh object assigned to this node tree"),
        ],
        default='SOLID_BAR'
    )
    
    # Contact area
    contact_area: FloatProperty(
        name="Contact Area",
        description="Contact area ratio for the impulse",
        default=0.001,
        min=0.0001,
        max=1,
        precision=4
    )
    
    # Force value
    force_value: FloatProperty(
        name="Force (N)",
        description="Force value for the impulse in Newtons",
        default=10.0,
        min=0.1,
        max=1000.0
    )

    # Impulse duration 
    impulse_duration: FloatProperty(
        name="Impulse Duration (s)",
        description="Duration of the impulse force in seconds",
        default=0.2,
        min=0.00001,
        max=1
    )
    
    # Preview duration
    preview_duration: FloatProperty(
        name="Preview Duration (s)",
        description="Duration of the preview sound in seconds",
        default=0.1,
        min=0.01,
        max=10.0
    )
    
    # U-Bar parameters
    u_bar_length: FloatProperty(
        name="Length (m)",
        description="Length of the U-bar in meters",
        default=0.3,
        min=0.1,
        max=1.0,
        unit='LENGTH'
    )
    
    u_bar_width: FloatProperty(
        name="Width (m)",
        description="Width of the U-bar in meters",
        default=0.03,
        min=0.01,
        max=0.1,
        unit='LENGTH'
    )
    
    u_bar_height: FloatProperty(
        name="Height (m)",
        description="Height of the U-bar in meters",
        default=0.02,
        min=0.005,
        max=0.05,
        unit='LENGTH'
    )
    
    # Circular plate parameters
    plate_radius: FloatProperty(
        name="Radius (m)",
        description="Radius of the circular plate in meters",
        default=0.05,
        min=0.01,
        max=0.3,
        unit='LENGTH'
    )
    
    plate_thickness: FloatProperty(
        name="Thickness (m)",
        description="Thickness of the circular plate in meters",
        default=0.003,
        min=0.001,
        max=0.01,
        unit='LENGTH'
    )
    
    # Solid bar parameters
    bar_length: FloatProperty(
        name="Length (m)",
        description="Length of the solid bar in meters",
        default=0.2,
        min=0.05,
        max=0.5,
        unit='LENGTH'
    )
    
    bar_radius: FloatProperty(
        name="Radius (m)",
        description="Radius of the solid bar in meters",
        default=0.008,
        min=0.003,
        max=0.02,
        unit='LENGTH'
    )
    
    def init(self, context):
        self.inputs.new('AcousticMaterialNodeSocket', "AcousticMaterial")
    
    def draw_buttons(self, context, layout):
#        box = layout.box()
#        box.label(text="Preview Settings", icon='SETTINGS')
#        
#        # Shape selection
#        row = box.row()
#        row.prop(self, "preview_shape", expand=True)
#        
#        # Shape-specific parameters
#        if self.preview_shape == 'U_BAR':
#            sub_box = box.box()
#            sub_box.label(text="U-Bar Dimensions:", icon='MESH_CUBE')
#            sub_box.prop(self, "u_bar_length")
#            sub_box.prop(self, "u_bar_width")
#            sub_box.prop(self, "u_bar_height")
#            
#        elif self.preview_shape == 'CIRCULAR_PLATE':
#            sub_box = box.box()
#            sub_box.label(text="Circular Plate Dimensions:", icon='MESH_CIRCLE')
#            sub_box.prop(self, "plate_radius")
#            sub_box.prop(self, "plate_thickness")
#            
#        elif self.preview_shape == 'SOLID_BAR':
#            sub_box = box.box()
#            sub_box.label(text="Solid Bar Dimensions:", icon='MESH_CYLINDER')
#            sub_box.prop(self, "bar_length")
#            sub_box.prop(self, "bar_radius")
#            
#        elif self.preview_shape == 'MESH_OBJECT':
#            sub_box = box.box()
#            sub_box.label(text="Using mesh object from scene", icon='OBJECT_DATA')
#        
#        # Contact parameters
#        box.separator()
#        sub_box = box.box()
#        sub_box.label(text="Impulse Parameters:", icon='FORCE_FORCE')
#        sub_box.prop(self, "contact_area")
#        sub_box.prop(self, "force_value")
#        
#        # Duration
#        box.separator()
#        box.prop(self, "preview_duration")
#        
#        # Preview button
#        box.separator()
#        row = box.row(align=True)
#        row.scale_y = 2.0
#        
#        # Create operator properties
#        op = row.operator(
#            "node.pbraudio_preview_material",
#            text="Play Preview",
#            icon='PLAY'
#        )
#        op.node_tree = self.id_data.name
#        op.node_name = self.name
#        
#        # Status indicator
#        if hasattr(self, '_audio_path') and self._audio_path and os.path.exists(self._audio_path):
#            row = box.row()
#            row.label(text="Cached", icon='CHECKMARK')

        layout.prop(self, "preview_shape", expand=True)
        layout.label(text="Preview Settings", icon='SETTINGS')
        layout.label(text="Impulse Parameters:", icon='FORCE_FORCE')
        layout.prop(self, "contact_area", slider=True)
        layout.prop(self, "force_value", slider=True)
        layout.prop(self, "impulse_duration", slider=True)

        # Duration
        layout.separator()
        layout.prop(self, "preview_duration", slider=True)

        # Preview button
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 2.0

        # Create operator properties
        op = row.operator("node.pbraudio_preview_material", text="Play Preview", icon='PLAY')
        op.node_tree = self.id_data.name
        op.node_name = self.name

        # Status indicator
        if hasattr(self, 'audio_path') and self.audio_path and os.path.exists(self.audio_path):
            row = layout.row()
            row.label(text="Cached", icon='CHECKMARK')
    
    def free(self):
        """Clean up when node is deleted"""
        self._cleanup_preview()
    
    def _cleanup_preview(self):
        """Clean up preview resources"""
        
        # Clear cached paths
        self.cache_path = None
        self.audio_path = None
        self.lib_path = None

classes.append(AcousticMaterialPreviewNode)
