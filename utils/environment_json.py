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
import json
import uuid
import bpy
from mathutils import Vector

def generate_environment_id():
    """Generate a unique ID for environment files"""
    return str(uuid.uuid4())

def save_environment_json(environment_obj, cache_path):
    """
    Save WorldEnvironment object data to JSON file
    
    Parameters:
        environment_obj: The WorldEnvironment object
        cache_path: Base cache path from scene.pbraudio.cache_path
    """
    if not environment_obj or not hasattr(environment_obj, ' 'pbraudio'):
        return None
    
    # Get environment properties
    env_props = environment_obj.pbraudio
    
    # Create environment data structure
    environment_data = {
        "id": generate_environment_id(),
        "name": environment_obj.name,
        "file_path": bpy.path.abspath(env_props.environment_file) if env_props.environment_file else "",
        "channels": env_props.environment_chanels,
        "radius": env_props.environment_size,
        "center_location": {
            "x": environment_obj.location.x,
            "y": environment_obj.location.y,
            "z": environment_obj.location.z
        },
        "boundaries": []
    }
    
    # Get boundary empties
    if "pbraudio_boundary_empties" in environment_obj:
        boundary_names = environment_obj["pbraudio_boundary_empties"]
        
        for name in boundary_names:
            boundary_obj = bpy.data.objects.get(name)
            if boundary_obj:
                boundary_data = {
                    "name": boundary_obj.name,
                    "location": {
                        "x": boundary_obj.location.x,
                        "y": boundary_obj.location.y,
                        "z": boundary_obj.location.z
                    },
                    "relative_position": {
                        "x": boundary_obj.location.x - environment_obj.location.x,
                        "y": boundary_obj.location.y - environment_obj.location.y,
                        "z": boundary_obj.location.z - environment_obj.location.z
                    }
                }
                environment_data["boundaries"].append(boundary_data)
    
    # Create directories if they don't exist
    env_dir = os.path.join(cache_path, "AcousticDomain", "Environments")
    os.makedirs(env_dir, exist_ok=True)
    
    # Save to JSON file
    json_filename = f"environment_{environment_data['id']}.json"
    json_path = os.path.join(env_dir, json_filename)
    
    with open(json_path, 'w') as f:
        json.dump(environment_data, f, indent=2, separators=(',', ': '))
    
    # Store the JSON file path in the object for reference
    environment_obj["pbraudio_environment_json"] = json_path
    
    return json_path

def update_all_environment_json(scene):
    """
    Update JSON files for all WorldEnvironment objects in the scene
    """
    if not hasattr(scene, 'pbraudio') or not scene.pbraudio.cache_path:
        return
    
    cache_path = scene.pbraudio.cache_path
    if cache_path.startswith('//'):
        cache_path = bpy.path.abspath(cache_path)
    
    # Find all WorldEnvironment objects
    for obj in bpy.data.objects:
        if hasattr(obj, 'pbraudio') and obj.pbraudio.environment:
            save_environment_json(obj, cache_path)

def get_environment_json_path(environment_obj):
    """
    Get the JSON file path for a WorldEnvironment object
    """
    if "pbraudio_environment_json" in environment_obj:
        return environment_obj["pbraudio_environment_json"]
    return None

def load_environment_json(json_path):
    """
    Load environment data from JSON file
    """
    if not os.path.exists(json_path):
        return None
    
    with open(json_path, 'r') as f:
        return json.load(f)

