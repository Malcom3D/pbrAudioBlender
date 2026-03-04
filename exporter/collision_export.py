import bpy
import numpy as np
import os
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion

class MeshToNumpyExporter:
    def __init__(self, scene: bpy.types.Scene, decimals: int = 18):
        np.set_printoptions(precision=decimals, floatmode='fixed', threshold=np.inf)
        self.decimals = decimals
        self.scale_factor = 1.0  # Blender units to meters
        system = {}
        system["sample_rate"] = scene.pbraudio.sample_rate
        system["bit_depth"] = scene.pbraudio.sample_rate
        system["fps"] = scene.pbraudio.sample_rate
        system["fps_base"] = scene.pbraudio.sample_rate
        system["subframes"] = 1
        system["collision_margin"] = scene.pbraudio.collision_margin
        system["cache_path"] = scene.pbraudio.cache_path
        self.config = {}
        self.config["system"] = system

        self.objects = []
        self.obj_idx = 0

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
    
    def export_animation(self, obj, output_path, start_frame=None, end_frame=None):
        """Export animation sequence"""

        obj.select_set(True)
        name = obj.name_full.replace('.', '_')
        
        acoustic_shader = {}
        acoustic_shader["sound_speed"] = obj.pbraudio.sound_speed
        acoustic_shader["young_modulus"] = obj.pbraudio.young_modulus
        acoustic_shader["poisson_ratio"] = obj.pbraudio.poisson_ratio
        acoustic_shader["density"] = obj.pbraudio.density
        acoustic_shader["damping"] = obj.pbraudio.damping
        acoustic_shader["friction"] = obj.pbraudio.friction
        acoustic_shader["roughness"] = obj.pbraudio.roughness
        acoustic_shader["low_frequency"] = obj.pbraudio.low_frequency
        acoustic_shader["high_frequency"] =  obj.pbraudio.high_frequency

        object = {}
        object["idx"] = self.obj_idx
        object["name"] = name
        object["acoustic_shader"] = acoustic_shader
        object["ground"] = obj.pbraudio.ground

        os.makedirs(output_path, exist_ok=True)
        os.makedirs(f"{output_path}/pose", exist_ok=True)
        os.makedirs(f"{output_path}/{name}", exist_ok=True)
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
        output_pose = os.path.join(output_path, f"pose/{name}.npz")

        # verify is not static
        if not np.all(location == location[0]) or not np.all(rotation == rotation[0]):
            object["static"] = False
            print(f"{obj.name} is not static...")
            print(f"Exporting pose for {obj.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location, rotation=rotation)

            for frame in range(start_frame, end_frame + 1):
                scene.frame_float = frame
                bpy.context.view_layer.update()
                print(f"Exporting {obj.name} frame {frame} in {output_path}/{name}...")
                frame_result = self.export_frame(obj, frame)
            
                # Store each component separately for easy access
                frame_data[f'vertices'] = frame_result['vertices']
                frame_data[f'normals'] = frame_result['normals']
                frame_data[f'faces'] = frame_result['faces']

                # Save to npz
                output_file = os.path.join(output_path, f"{name}/{name}_{frame:05d}.npz")
                np.savez_compressed(output_file, **frame_data)
        else:
            object["static"] = True
            print(f"{obj.name} is static...")
            print(f"Exporting pose for {obj.name} to {output_pose}...")
            np.savez_compressed(output_pose, location=location[0], rotation=rotation[0])            
            print(f"Exporting {obj.name} in {output_path}/{name}...")
            frame_result = self.export_frame(obj, start_frame)

            # Store each component separately for easy access
            frame_data[f'vertices'] = frame_result['vertices']
            frame_data[f'normals'] = frame_result['normals']
            frame_data[f'faces'] = frame_result['faces']

            # Save to npz
            output_file = os.path.join(output_path, f"{name}/{name}.npz")
            np.savez_compressed(output_file, **frame_data)
        obj.select_set(False)            
        self.objects.append(object)
        self.obj_idx += 1
