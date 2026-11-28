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
from bpy.types import Panel

from ..utils.socket_server import SocketServerManager

classes = []

class PBRAUDIO_PT_socket_server_panel(Panel):
    """Panel for pbrAudio socket server"""
    bl_label = "Socket Server"
    bl_idname = "PBRAUDIO_PT_socket_server_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "pbrAudio"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PBRAUDIO'

    def draw(self, context):
        layout = self.layout
        props = context.scene.pbraudio_socket
        status = SocketServerManager.get_status()

        # --- Status label ---
        status_box = layout.box()
        row = status_box.row()
        if status == 'DISABLED':
            row.label(text="Status: Disabled", icon='CANCEL')
        elif status == 'WAITING':
            row.label(text="Status: Waiting for client...", icon='TIME')
        elif status == 'CONNECTED':
            row.label(text=f"Status: Client connected ({SocketServerManager.get_client_address()})", icon='LINKED')

        # --- Toggle button ---
        row = layout.row()
        row.scale_y = 1.5
        if status == 'DISABLED':
            row.operator("pbraudio.toggle_socket_server", text="Enable Server", icon='PLAY')
        else:
            row.operator("pbraudio.toggle_socket_server", text="Disable Server", icon='PAUSE')

        # --- Send test button (enabled only if client connected) ---
        row = layout.row()
        sub = row.row()
        sub.enabled = (status == 'CONNECTED')
        sub.operator("pbraudio.send_socket_message", text="Send Test Message", icon='SORTALPHA')

        layout.separator()

        # --- Advanced options ---
        row = layout.row()
        row.prop(props, "show_advanced",
                 icon='TRIA_DOWN' if props.show_advanced else 'TRIA_RIGHT',
                 icon_only=True, emboss=False)
        row.label(text="Advanced Options")

        if props.show_advanced:
            box = layout.box()
            col = box.column(align=True)
            col.enabled = (status == 'DISABLED')  # lock when running
            col.prop(props, "host", text="Host")
            col.prop(props, "port", text="Port")

            if status != 'DISABLED':
                box.label(text="Stop server to edit host/port", icon='INFO')

classes.append(PBRAUDIO_PT_socket_server_panel)
