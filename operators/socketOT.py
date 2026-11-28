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

from ..utils.pbrAudioDAW_link import pbrAudioDAWlink

classes = []


class PBRAUDIO_OT_toggle_socket_server(Operator):
    """Toggle the socket server on/off"""
    bl_idname = "pbraudio.toggle_socket_server"
    bl_label = "Toggle Socket Server"
    bl_description = "Start or stop the pbrAudio socket server"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.pbraudio_socket
        status = pbrAudioDAWlink.get_status()

        if status == 'DISABLED':
            success, msg = pbrAudioDAWlink.start(props.host, props.port)
            if success:
                props.enabled = True
                self.report({'INFO'}, msg)
            else:
                props.enabled = False
                self.report({'ERROR'}, msg)
                return {'CANCELLED'}
        else:
            pbrAudioDAWlink.stop()
            props.enabled = False
            self.report({'INFO'}, "pbrAudioDAW link stopped")

        # Force redraw so panel updates
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}

classes.append(PBRAUDIO_OT_toggle_socket_server)

#class PBRAUDIO_OT_send_socket_message(Operator):
#    """Send a message to the connected client"""
#    bl_idname = "pbraudio.send_socket_message"
#    bl_label = "Send Message"
#    bl_description = "Send a test message to the connected client"
#
#    def execute(self, context):
#        ok = pbrAudioDAWlink.send("Hello from Blender")
#        if ok:
#            self.report({'INFO'}, "Message sent")
#        else:
#            self.report({'WARNING'}, "No client connected")
#        return {'FINISHED'}
#
#classes.append(PBRAUDIO_OT_send_socket_message)
