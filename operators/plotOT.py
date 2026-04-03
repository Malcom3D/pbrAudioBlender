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
from bpy.types import Operator

classes = []

class BigPreview(Operator):
    bl_idname = "pbraudio.big_preview"
    bl_label = "Big Preview"
    def execute(self, context):
        print("Running big preview")
        return {'FINISHED'}
    def check(self, context):
        return False
    def invoke(self, context, event):
        wm = context.window_manager
        self.texture = bpy.data.textures.new(name="previewTexture", type="IMAGE")
        self.texture.image = context.window_manager.image
        self.textute.extension = 'CLIP'  #EXTEND # CLIP # CLIP_CUBE # REPEAT # CHECKER
        print("Invoke big preview")
        return wm.invoke_props_dialog(self, width=600)
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        #col.scale_y = 2
        col.template_preview(self.texture, show_buttons=False)
        
classes.append(BigPreview)
