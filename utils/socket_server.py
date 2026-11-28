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

import socket
import threading
import bpy

class SocketServerManager:
    """Manages the socket server lifecycle for pbrAudio"""
    
    _instance = None
    _server_socket = None
    _client_socket = None
    _client_address = None
    _server_thread = None
    _running = False
    _status = 'DISABLED'  # DISABLED, WAITING, CONNECTED
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_status(cls):
        return cls._status
    
    @classmethod
    def get_client_address(cls):
        if cls._client_address is not None:
            return f"{cls._client_address[0]}:{cls._client_address[1]}"
        return ""
    
    @classmethod
    def start(cls, host, port):
        """Start the socket server"""
        if cls._running:
            return False, "Server already running"
        
        try:
            cls._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cls._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            cls._server_socket.bind((host, port))
            cls._server_socket.listen(1)
            cls._running = True
            cls._status = 'WAITING'
            
            cls._server_thread = threading.Thread(target=cls._accept_loop, daemon=True)
            cls._server_thread.start()
            return True, f"Server listening on {host}:{port}"
        except Exception as e:
            cls._running = False
            cls._status = 'DISABLED'
            cls._server_socket = None
            return False, f"Failed to start server: {e}"
    
    @classmethod
    def stop(cls):
        """Stop the socket server"""
        cls._running = False
        cls._status = 'DISABLED'
        
        # Close client
        if cls._client_socket is not None:
            try:
                cls._client_socket.close()
            except Exception:
                pass
            cls._client_socket = None
            cls._client_address = None
        
        # Close server
        if cls._server_socket is not None:
            try:
                cls._server_socket.close()
            except Exception:
                pass
            cls._server_socket = = None
        
        cls._server_thread = None
        cls._tag_redraw()
    
    @classmethod
    def _accept_loop(cls):
        """Background thread that accepts client connections and receives messages"""
        while cls._running:
            try:
                cls._server_socket.settimeout(0.5)
                try:
                    client_socket, client_address = cls._server_socket.accept()
                except socket.timeout:
                    continue
                
                # If a client is already connected, close the previous one
                if cls._client_socket is not None:
                    try:
                        cls._client_socket.close()
                    except Exception:
                        pass
                
                cls._client_socket = client_socket
                cls._client_address = client_address
                cls._status = 'CONNECTED'
                cls._tag_redraw()
                print(f"[pbrAudio Socket] Client connected from {client_address}")
                
                # Receive loop
                cls._client_socket.settimeout(0.5)
                while cls._running:
                    try:
                        data = cls._client_socket.recv(4096)
                        if not data:
                            break
                        message = data.decode(errors='replace')
                        print(f"[pbrAudio Socket] Received: {message}")
                        cls._handle_message(message)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"[pbrAudio Socket] Receive error: {e}")
                        break
                
                # Client disconnected
                try:
                    cls._client_socket.close()
                except Exception:
                    pass
                cls._client_socket = None
                cls._client_address = None
                cls._status = 'WAITING' if cls._running else 'DISABLED'
                cls._tag_redraw()
                print("[pbrAudio Socket] Client disconnected")
                
            except Exception as e:
                if cls._running:
                    print(f"[pbrAudio Socket] Accept error: {e}")
                break
    
    @classmethod
    def send(cls, message):
        """Send a message to the connected client"""
        if cls._client_socket is None:
            return False
        try:
            cls._client_socket.sendall(message.encode())
            return True
        except Exception as e:
            print(f"[pbrAudio Socket] Send error: {e}")
            return False
    
    @classmethod
    def _handle_message(cls, message):
        """Process an incoming message """
        # Placeholder: could parse commands from client like playback
        pass
    
    @classmethod
    def _tag_redraw(cls):
        """Trigger a redraw so the panel updates status"""
        try:
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type in {'VIEW_3D'}:
                        area.tag_redraw()
        except Exception:
            pass
