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
import hashlib
from bpy.types import Operator
from bpy.props import StringProperty, PointerProperty

classes = []

class PBRAUDIO_OT_validate_cache_hash(Operator):
    bl_idname = "object.pbraudio_validate_cache_hash"
    bl_label = "Validate pbrAudio collection cache hash"
    bl_description = "Validate collision collection cache hash"
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: StringProperty(
        name="Collection Name",
        description="Name of the pbrAudio collision collection",
        default=""
    )

    def compute_collision_hash(self, context):
        """Compute a hash of the collision collection state"""
        scene = context.scene

        collision_collection = bpy.data.collection[self.collection_name]
   
        hash_input = []
   
        # Include collection name
        hash_input.append(self.collection_name)
   
        # Include all object names and their properties
        for obj in collision_collection.objects:
            hash_input.append(obj.name)
            hash_input.append(str(obj.type))

            # Include pbrAudio properties that affect cache
            if hasattr(obj, 'pbraudio'):
                hash_input.append(str(obj.pbraudio.stochastic_variation))
                hash_input.append(str(obj.pbraudio.ground))
                hash_input.append(str(obj.pbraudio.resonance))
                hash_input.append(str(obj.pbraudio.resonance_modes))
                hash_input.append(str(obj.pbraudio.connected))
                hash_input.append(str(obj.pbraudio.fractured))
                hash_input.append(str(obj.pbraudio.proxy))
                hash_input.append(str(obj.pbraudio.proxy_type))

        # Include general properties
        hash_input.append(scene.pbraudio.modal_modes)
        hash_input.append(scene.pbraudio.enable_forces_denoiser)
        hash_input.append(scene.pbraudio.enable_postprocess)

        # Create hash
        hash_str = json.dumps(hash_input, sort_keys=True)
        return hashlib.sha256(hash_str.encode()).hexdigest()


    def execute(self, context):
        scene = context.scene
        collision_collection = bpy.data.collection[self.collection_name]
        cache_hash = compute_collision_hash
        if collision_collection['cache_hash'] == cache_hash:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

classes.append(PBRAUDIO_OT_validate_cache_hash)
