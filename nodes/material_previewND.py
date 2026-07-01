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
import struct
import wave
from bpy.types import Node, Operator
from bpy.props import IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty
from dataclasses import dataclass
from typing import List, Tuple, Optional

from .baseND import AcousticMaterialNode
from rigidBody import Pym2f
from rigidBody import FaustRender
from physicsSolver.lib.functions import _parse_lib

classes = []

# Shape definitions for modal analysis
@dataclass
class ShapeGeometry:
    """Geometric parameters for test shapes"""
    name: str
    vertices: np.ndarray
    normals: np.ndarray
    faces: np.ndarray
    
    def to_obj_string(self) -> str:
        """Convert to OBJ format string"""
        obj_lines = []
        for v in self.vertices:
            obj_lines.append(f"v {v[0]:.10f} {v[1]:.10f} {v[2]:.10f}")
        for n in self.normals:
            obj_lines.append(f"vn {n[0]:.10f} {n[1]:.10f} {n[2]:.10f}")
        for f in self.faces:
            obj_lines.append(f"f {f[0]+1}//{f[0]+1} {f[1]+1}//{f[1]+1} {f[2]+1}//{f[2]+1}")
        return "\n".join(obj_lines)

def generate_u_bar(length: float = 0.3, width: float = 0.03, height: float = 0.02, 
                   subdivisions: int = 4) -> ShapeGeometry:
    """
    Generate a U-shaped bar (channel section) for decay and brightness evaluation.
    
    Parameters:
    -----------
    length : float
        Length of the bar in meters (default 0.3m)
    width : float
        Width of the U-channel in meters (default 0.03m)
    height : float
        Height of the U-channel in meters (default 0.02m)
    subdivisions : int
        Number of subdivisions along the length
    """
    # Create U-shaped cross-section points
    # The U shape has: bottom, left wall, right wall
    n_length = max(4, subdivisions * 2)
    n_cross = 8  # Points around U cross-section
    
    # Cross-section vertices (U shape)
    t = np.linspace(0, 1, n_cross)
    # U profile: [bottom-left, bottom-right, right-bottom, right-top, top-right, top-left, left-top, left-bottom]
    cross_section = np.array([
        [-width/2, -height/2],  # bottom-left
        [width/2, -height/2],   # bottom-right
        [width/2, -height/2 + 0.001],  # right-bottom inner
        [width/2, height/2],    # right-top
        [width/2 - 0.002, height/2],  # right-top inner
        [-width/2 + 0.002, height/2], # left-top inner
        [-width/2, height/2],   # left-top
        [-width/2, -height/2 + 0.001]  # left-bottom inner
    ])
    
    # Extrude along length
    z_positions = np.linspace(-length/2, length/2, n_length)
    
    vertices = []
    normals = []
    faces = []
    
    for i, z in enumerate(z_positions):
        for j, (x, y) in enumerate(cross_section):
            vertices.append([x, y, z])
            # Normal approximation (radial from center)
            norm = np.array([x, y, 0])
            norm_norm = np.linalg.norm(norm)
            if norm_norm > 0:
                norm = norm / norm_norm
            else:
                norm = [0, 0, 1]
            normals.append(norm.tolist())
    
    # Create faces (triangles between consecutive cross-sections)
    for i in range(n_length - 1):
        for j in range(n_cross):
            v0 = i * n_cross + j
            v1 = i * n_cross + (j + 1) % n_cross
            v2 = (i + 1) * n_cross + j
            v3 = (i + 1) * n_cross + (j + 1) % n_cross
            
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])
    
    # Close ends
    # Front face
    for j in range(1, n_cross - 1):
        faces.append([j, j+1, 0])
    # Back face
    offset = (n_length - 1) * n_cross
    for j in range(1, n_cross - 1):
        faces.append([offset, offset + j + 1, offset + j])
    
    return ShapeGeometry(
        name=f"U_Bar_{length:.2f}m",
        vertices=np.array(vertices, dtype=np.float32),
        normals=np.array(normals, dtype=np.float32),
        faces=np.array(faces, dtype=np.int32)
    )

def generate_circular_plate(radius: float = 0.05, thickness: float = 0.003,
                           radial_segments: int = 8, circumferential_segments: int = 16) -> ShapeGeometry:
    """
    Generate a thin circular plate for inharmonicity and brightness evaluation.
    
    Parameters:
    -----------
    radius : float
        Radius of the plate in meters (default 0.05m)
    thickness : float
        Thickness of the plate in meters (default 0.003m)
    radial_segments : int
        Number of radial subdivisions
    circumferential_segments : int
        Number of circumferential subdivisions
    """
    vertices = []
    normals = []
    faces = []
    
    # Generate vertices
    for i in range(radial_segments + 1):
        r = radius * i / radial_segments
        for j in range(circumferential_segments):
            theta = 2 * np.pi * j / circumferential_segments
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Top face
            vertices.append([x, y, thickness/2])
            normals.append([0, 0, 1])
            # Bottom face
            vertices.append([x, y, -thickness/2])
            normals.append([0, 0, -1])
    
    # Center vertex
    center_top = len(vertices)
    vertices.append([0, 0, thickness/2])
    normals.append([0, 0, 1])
    center_bottom = len(vertices)
    vertices.append([0, 0, -thickness/2])
    normals.append([0, 0, -1])
    
    n_vertices_per_ring = 2 * circumferential_segments
    
    # Generate faces
    for i in range(radial_segments - 1):
        for j in range(circumferential_segments):
            v0 = i * n_vertices_per_ring + 2 * j
            v1 = i * n_vertices_per_ring + 2 * ((j + 1) % circumferential_segments)
            v2 = (i + 1) * n_vertices_per_ring + 2 * j
            v3 = (i + 1) * n_vertices_per_ring + 2 * ((j + 1) % circumferential_segments)
            
            # Top faces
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])
            # Bottom faces (reversed normals)
            faces.append([v0 + 1, v2 + 1, v1 + 1])
            faces.append([v1 + 1, v2 + 1, v3 + 1])
    
    # Connect to center
    for j in range(circumferential_segments):
        v0 = (radial_segments - 1) * n_vertices_per_ring + 2 * j
        v1 = (radial_segments - 1) * n_vertices_per_ring + 2 * ((j + 1) % circumferential_segments)
        
        # Top
        faces.append([v0, v1, center_top])
        # Bottom
        faces.append([v0 + 1, center_bottom, v1 + 1])
    
    # Side faces (edge)
    for j in range(circumferential_segments):
        v0 = 2 * j
        v1 = 2 * ((j + 1) % circumferential_segments)
        v2 = v0 + 1
        v3 = v1 + 1
        
        faces.append([v0, v1, v2])
        faces.append([v1, v3, v2])
    
    return ShapeGeometry(
        name=f"Circular_Plate_{radius*1000:.0f}mm",
        vertices=np.array(vertices, dtype=np.float32),
        normals=np.array(normals, dtype=np.float32),
        faces=np.array(faces, dtype=np.int32)
    )

def generate_solid_bar(length: float = 0.2, radius: float = 0.008,
                      length_segments: int = 8, radial_segments: int = 8) -> ShapeGeometry:
    """
    Generate a solid cylindrical bar (free-free) for tonal balance evaluation.
    
    Parameters:
    -----------
    length : float
        Length of the bar in meters (default 0.2m)
    radius : float
        Radius of the bar in meters (default 0.008m)
    length_segments : int
        Number of segments along the length
    radial_segments : int
        Number of radial segments
    """
    vertices = []
    normals = []
    faces = []
    
    # Generate vertices along length
    z_positions = np.linspace(-length/2, length/2, length_segments)
    
    for z in z_positions:
        for i in range(radial_segments):
            theta = 2 * np.pi * i / radial_segments
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            
            vertices.append([x, y, z])
            # Normal is radial
            norm = np.array([x, y, 0])
            norm_norm = np.linalg.norm(norm)
            if norm_norm > 0:
                norm = norm / norm_norm
            else:
                norm = [0, 0, 1]
            normals.append(norm.tolist())
    
    # End caps
    center_front = len(vertices)
    vertices.append([0, 0, -length/2])
    normals.append([0, 0, -1])
    center_back = len(vertices)
    vertices.append([0, 0, length/2])
    normals.append([0, 0, 1])
    
    # Side faces
    for i in range(length_segments - 1):
        for j in range(radial_segments):
            v0 = i * radial_segments + j
            v1 = i * radial_segments + (j + 1) % radial_segments
            v2 = (i + 1) * radial_segments + j
            v3 = (i + 1) * radial_segments + (j + 1) % radial_segments
            
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])
    
    # Front cap
    for j in range(1, radial_segments - 1):
        faces.append([center_front, center_front + j, center_front + j + 1])
    # Back cap
    offset = (length_segments - 1) * radial_segments
    for j in range(1, radial_segments - 1):
        faces.append([center_back, offset + j, offset + j + 1])
    
    return ShapeGeometry(
        name=f"Solid_Bar_{length*100:.0f}cm",
        vertices=np.array(vertices, dtype=np.float32),
        normals=np.array(normals, dtype=np.float32),
        faces=np.array(faces, dtype=np.int32)
        )

class PBRAUDIO_OT_preview_material(Operator):
    """Preview acoustic material sound"""
    bl_idname = "node.pbraudio_preview_material"
    bl_label = "Preview Material Sound"
    bl_description = "Generate and play preview sound for the acoustic material"
    
    node_tree: StringProperty(name="Node Tree", default="")
    node_name: StringProperty(name="Node Name", default="")
    
    def _get_acoustic_params(self, node):
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
    
    def _create_temp_obj(self, shape_geo: ShapeGeometry) -> str:
        """Create temporary OBJ file from shape geometry"""
        temp_dir = tempfile.mkdtemp()
        obj_path = os.path.join(temp_dir, f"{shape_geo.name}.obj")
        
        with open(obj_path, 'w') as f:
            f.write(f"# {shape_geo.name}\n")
            f.write(shape_geo.to_obj_string())
        
        return obj_path, temp_dir
    
    def _compute_modal_model(self, obj_path: str, params: dict, temp_dir: str) -> Optional[str]:
        """Compute modal model using mesh2faust"""
        try:
            # Create a temporary EntityManager-like config
            import json
            config = {
                "system": {
                    "cache_path": temp_dir,
                    "modal_modes": 30  # Use 30 modes for preview
                },
                "objects": [{
                    "idx": 0,
                    "name": "preview",
                    "obj_path": os.path.dirname(obj_path),
                    "pose_path": temp_dir,
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
            
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            # Use Pym2f to compute modal model
            from physicsSolver import EntityManager
            entity_manager = EntityManager(config_path)
            pym2f = Pym2f(entity_manager)
            pym2f.compute(0)
            
            # Check if lib file was created
            lib_path = os.path.join(temp_dir, "dsp", "preview.lib")
            if os.path.exists(lib_path):
                return lib_path
            
            return None
            
        except Exception as e:
            print(f"Modal model computation error: {e}")
            return None
    
    def _create_faust_dsp(self, lib_path: str, params: dict, num_vertices: int) -> str:
        """Create Faust DSP file for modal synthesis"""
        dsp_content = f"""
// Auto-generated preview DSP for acoustic material
// Parameters:
// - Young's Modulus: {params['young_modulus']} GPa
// - Poisson Ratio: {params['poisson_ratio']}
// - Density: {params['density']} kg/m³
// - Damping: {params['damping']}%
// - Frequency Range: {params['low_frequency']} - {params['high_frequency']} Hz

import("stdfaust.lib");
import("preview.lib");

// Number of vertices to excite
nVertices = {num_vertices};

// Process: excite all vertices with same impulse
process = par(i, nVertices, 
    (button("play") : 
        (0.0 : si.smoo) :  // Smooth trigger
        *(1.0/nVertices) : // Distribute energy
        modalModel(i)      // Each vertex's modal response
    )
) :> _;  // Sum all outputs

// Apply gain and limiter
process = process : fi.power_limiter(0.95) : *(0.5);
"""
        
        dsp_path = os.path.join(os.path.dirname(lib_path), "preview.dsp")
        with open(dsp_path, 'w') as f:
            f.write(dsp_content)
        
        return dsp_path
    
    def _render_audio(self, dsp_path: str, duration: float = 2.0) -> Optional[str]:
        """Render audio using FaustRender"""
        try:
            output_path = os.path.join(os.path.dirname(dsp_path), "preview.raw")
            renderer = FaustRender()
            renderer.compute(dsp_path, output_path, duration)
            
            if os.path.exists(output_path):
                return output_path
            
            return None
            
        except Exception as e:
            print(f"Audio rendering error: {e}")
            return None
    
    def _play_audio(self, audio_path: str):
        """Play audio in Blender using aud module"""
        try:
            import aud
            
            # Read RAW PCM FLOAT32 file
            with open(audio_path, 'rb') as f:
                raw_data = f.read()
            
            # Convert to numpy array
            samples = np.frombuffer(raw_data, dtype=np.float32)
            
            # Create temporary WAV file for aud
            temp_wav = os.path.join(os.path.dirname(audio_path), "preview.wav")
            sf.write(temp_wav, samples, 48000, subtype='FLOAT')
            
            # Play using aud
            device = aud.Device()
            sound = aud.Sound(temp_wav)
            handle = device.play(sound)
            
            print(f"Playing preview audio: {temp_wav}")
            
        except ImportError:
            print("aud module not available. Playing with system player...")
            import subprocess
            import platform
            
            if platform.system() == 'Linux':
                subprocess.Popen(['aplay', audio_path])
            elif platform.system() == 'Darwin':
                subprocess.Popen(['afplay', audio_path])
            else:
                print("Please install aud module or use an external player")
    
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
            
            # Get acoustic parameters
            params = self._get_acoustic_params(node)
            
            # Get shape type and parameters from node
            shape_type = node.preview_shape
            num_vertices = node.preview_vertices
            
            # Generate shape based on type
            if shape_type == 'U_BAR':
                shape_geo = generate_u_bar(
                    length=node.u_bar_length,
                    width=node.u_bar_width,
                    height=node.u_bar_height
                )
            elif shape_type == 'CIRCULAR_PLATE':
                shape_geo = generate_circular_plate(
                    radius=node.plate_radius,
                    thickness=node.plate_thickness
                )
            else:  # SOLID_BAR
                shape_geo = generate_solid_bar(
                    length=node.bar_length,
                    radius=node.bar_radius
                )
            
            # Create temporary OBJ file
            obj_path, temp_dir = self._create_temp_obj(shape_geo)
            
            # Compute modal model
            self.report({'INFO'}, "Computing modal model...")
            lib_path = self._compute_modal_model(obj_path, params, temp_dir)
            
            if not lib_path:
                self.report({'ERROR'}, "Failed to compute modal model")
                return {'CANCELLED'}
            
            # Create Faust DSP
            self.report({'INFO'}, "Creating synthesis DSP...")
            dsp_path = self._create_faust_dsp(lib_path, params, num_vertices)
            
            # Render audio
            self.report({'INFO'}, "Rendering preview audio...")
            duration = node.preview_duration
            audio_path = self._render_audio(dsp_path, duration)
            
            if not audio_path:
                self.report({'ERROR'}, "Failed to render audio")
                return {'CANCELLED'}
            
            # Play audio
            self.report({'INFO'}, "Playing preview...")
            self._play_audio(audio_path)
            
            # Cleanup temp files (optional)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
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
    
    # Preview shape selection
    preview_shape: EnumProperty(
        name="Test Shape",
        description="Shape to use for modal analysis preview",
        items=[
            ('U_BAR', "U-Bar", "U-shaped bar for decay and brightness"),
            ('CIRCULAR_PLATE', "Circular Plate", "Thin circular plate for inharmonicity"),
            ('SOLID_BAR', "Solid Bar", "Solid cylindrical bar for tonal balance balance"),
        ],
        default='SOLID_BAR'
    )
    
    # Number of vertices to excite
    preview_vertices: IntProperty(
        name="Excitation Vertices",
        description="Number of vertices to excite in the modal model",
        default=4,
        min=1,
        max=20
    )
    
    # Preview duration
    preview_duration: FloatProperty(
        name="Preview Duration",
        description="Duration of the preview sound in seconds",
        default=2.0,
        min=0.5,
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
        box = layout.box()
        box.label(text="Preview Settings", icon='SETTINGS')
        
        # Shape selection
        row = box.row()
        row.prop(self, "preview_shape", expand=True)
        
        # Shape-specific parameters
        if self.preview_shape == 'U_BAR':
            sub_box = box.box()
            sub_box.label(text="U-Bar Dimensions:", icon='MESH_CUBE')
            sub_box.prop(self, "u_bar_length")
            sub_box.prop(self, "u_bar_width")
            sub_box.prop(self, "u_bar_height")
            
        elif self.preview_shape == 'CIRCULAR_PLATE':
            sub_box = box.box()
            sub_box.label(text="Circular Plate Dimensions:", icon='MESH_CIRCLE')
            sub_box.prop(self, "plate_radius")
            sub_box.prop(self, "plate_thickness")
            
        else:  # SOLID_BAR
            sub_box = box.box()
            sub_box.label(text="Solid Bar Dimensions:", icon='MESH_CYLINDER')
            sub_box.prop(self, "bar_length")
            sub_box.prop(self, "bar_radius")
        
        # Excitation settings
        box.separator()
        box.prop(self, "preview_vertices")
        box.prop(self, "preview_duration")
        
        # Preview button
        box.separator()
        row = box.row(align=True)
        row.scale_y = 2.0
        
        # Create operator properties
        op = row.operator(
            "node.pbraudio_preview_material",
            text="PlayPlay Preview",
            icon='PLAY'
        )
        op.node_tree = self.id_data.name
        op.node_name = self.name
        
        # Status indicator
        row = box.row()
        row.label(text="", icon='SOUND')

classes.append(AcousticMaterialPreviewNode)

