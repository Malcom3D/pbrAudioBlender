import bpy
import json
import os

def load_rays_from_json(filepath):
    """Load ray data from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    origins = data['origins']
    hit_points = data['hit_points']
    
    return origins, hit_points

def create_ray_visualization(origins, hit_points, clear_scene=False):
    """Create line segments for each ray in Blender"""
    
#    if clear_scene:
#        # Clear existing objects
#        bpy.ops.object.select_all(action='SELECT')
#        bpy.ops.object.delete(use_global=False)
    
    # Create a collection for rays
    ray_collection = bpy.data.collections.new('Rays')
    bpy.context.scene.collection.children.link(ray_collection)
    
    # Create rays
    for i, (origin, hit_point) in enumerate(zip(origins, hit_points)):
        # Create a curve for each ray
        curve_data = bpy.data.curves.new(name=f'Ray_{i:04d}', type='CURVE')
        curve_data.dimensions = '3D'
        
        # Create spline
        spline = curve_data.splines.new('POLY')
        spline.points.add(1)  # Add one more point (we need 2 points total)
        
        # Set points
        spline.points[0].co = (*origin, 1)
        spline.points[1].co = (*hit_point, 1)
        
        # Create object
        curve_obj = bpy.data.objects.new(f'Ray_{i:04d}', curve_data)
        ray_collection.objects.link(curve_obj)
        
        # Set curve properties for better visualization
        curve_data.bevel_depth = 0.02
        curve_data.bevel_resolution = 4
        
        # Optional: Add material for color coding
        mat = bpy.data.materials.new(name=f'Ray_Material_{i:04d}')
        mat.use_nodes = True
        
        # Assign different colors based on hit point location or other criteria
        if hit_point[0] > 5:  # Example: color based on x-coordinate
            mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (1, 0, 0, 1)  # Red
        elif hit_point[1] > 5:
            mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (0, 1, 0, 1)  # Green
        else:
            mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (0, 0, 1, 1)  # Blue
        
        curve_obj.data.materials.append(mat)
    
    print(f"Created {len(origins)} rays")

def create_ray_visualization_efficient(origins, hit_points, clear_scene=False):
    """More efficient version using a single mesh with vertex colors"""

#    if clear_scene:
#        bpy.ops.object.select_all(action='SELECT')
#        bpy.ops.object.delete(use_global=False)
    
    # Create vertices and edges
    vertices = []
    edges = []
    
    for i, (origin, hit_point) in enumerate(zip(origins, hit_points)):
        start_idx = len(vertices)
        vertices.append(origin)
        vertices.append(hit_point)
        edges.append((start_idx, start_idx + 1))
    
    # Create mesh
    mesh = bpy.data.meshes.new('Rays_Mesh')
    mesh.from_pydata(vertices, edges, [])
    mesh.update()
    
    # Create object
    obj = bpy.data.objects.new('Rays', mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # Add edge split modifier for better visualization
    edge_split = obj.modifiers.new(name='EdgeSplit', type='EDGE_SPLIT')
    edge_split.split_angle = 1.32645
    
    # Create material
    mat = bpy.data.materials.new(name='Ray_Material')
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (0.8, 0.2, 0.2, 1.0)
    obj.data.materials.append(mat)
    
    # Set display settings
    obj.show_wire = True
    obj.show_all_edges = True
    
    print(f"Created {len(origins)} rays efficiently")

def batch_process_json_files(directory):
    """Process multiple JSON files in a directory"""
    import glob
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(directory, "*.json"))
    
    for json_file in sorted(json_files):
        print(f"Processing {json_file}...")
        origins, hit_points = load_rays_from_json(json_file)
        
        # Create collection for this file
        filename = os.path.basename(json_file).replace('.json', '')
        collection = bpy.data.collections.new(filename)
        bpy.context.scene.collection.children.link(collection)
        
        # Set active collection
        layer_collection = bpy.context.view_layer.layer_collection.children[filename]
        bpy.context.view_layer.active_layer_collection = layer_collection
        
        # Create rays
        create_ray_visualization_efficient(origins, hit_points, clear_scene=False)

# Main execution
def main():
    # Option 1: Load a single file
    #filepath = "/home/malcom3d/Documents/pbrAudioRender/renderSingle/embreex.json"  # Change this to your file path
    #filepath = "embreex_0.json"  # Change this to your file path
    #origins, hit_points = load_rays_from_json(filepath)
    #create_ray_visualization_efficient(origins, hit_points)
    
    # Option 2: Process multiple files in a directory
    directory = "ray_datas"  # Change this to your directory
    batch_process_json_files(directory)

# Run the script
if __name__ == "__main__":
    main()
