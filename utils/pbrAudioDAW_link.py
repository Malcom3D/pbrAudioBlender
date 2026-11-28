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
import time
import bpy


class pbrAudioDAWlink:
    """
    Manages a client connection to the pbrAudioDAW TUI or GUI socket server.
    """

    _instance = None
    _client_socket = None
    _server_address = None
    _client_address = None
    _recv_thread = None
    _running = False
    _connected = False
    _status = 'DISABLED'            # DISABLED, WAITING, CONNECTED

    # Connection / reconnection tuning
    _CONNECT_TIMEOUT = 5.0
    _RECV_TIMEOUT = 0.5
    _RECONNECT_DELAY = 2.0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------ #
    # Status helpers
    # ------------------------------------------------------------------ #
    @classmethod
    def get_status(cls):
        return cls._status

    @classmethod
    def get_client_address(cls):
        """Address the OS assigned to our client socket once connected."""
        if cls._client_address is not None:
            return f"{cls._client_address[0]}:{cls._client_address[1]}"
        return ""

    @classmethod
    def get_pbraudiodaw_address(cls):
        """Address of the pbrAudioDAW server we are (or will be) connected to."""
        if cls._server_address is not None:
            return f"{cls._server_address[0]}:{cls._server_address[1]}"
        return ""

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    @classmethod
    def start(cls, host, port):
        """Start the client (attempt to connect to the pbrAudioDAW server)."""
        if cls._running:
            return False, "Client already running"

        cls._server_address = (host, port)
        cls._running = True
        cls._connected = False
        cls._status = 'WAITING'

        # Kick off background thread that connects (and reconnects).
        cls._recv_thread = threading.Thread(target=cls._connect_and_receive_loop, daemon=True)
        cls._recv_thread.start()

        return True, f"Connecting to {host}:{port}"

    @classmethod
    def stop(cls):
        """Stop the client and tear down any active connection."""
        cls._running = False
        cls._connected = False
        cls._status = 'DISABLED'

        if cls._client_socket is not None:
            try:
                cls._client_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                cls._client_socket.close()
            except Exception:
                pass
            cls._client_socket = None

        cls._client_address = None
        cls._recv_thread = None
        cls._tag_redraw()

    # ------------------------------------------------------------------ #
    # Background worker
    # ------------------------------------------------------------------ #
    @classmethod
    def _connect_and_receive_loop(cls):
        """Connect to the server (with retries) and then receive messages."""
        while cls._running:
            # --- connect phase ---
            if not cls._connected:
                cls._status = 'WAITING'
                cls._tag_redraw()
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(cls._CONNECT_TIMEOUT)
                    sock.connect(cls._server_address)

                    cls._client_socket = sock
                    cls._client_socket.settimeout(cls._RECV_TIMEOUT)
                    # Address of the *remote* peer (per your sample code)
                    cls._client_address = sock.getpeername()

                    cls._connected = True
                    cls._status = 'CONNECTED'
                    cls._tag_redraw()
                    print(f"[pbrAudio Socket] Connected to {cls._server_address} "
                          f"from {cls._client_address}")
                except Exception as e:
                    cls._status = 'WAITING'
                    cls._tag_redraw()
                    print(f"[pbrAudio Socket] Connect failed: {e}. "
                          f"Retrying in {cls._RECONNECT_DELAY}s...")
                    cls._client_socket = None
                    # sleep in small slices so stop() is responsive
                    deadline = time.time() + cls._RECONNECT_DELAY
                    while cls._running and time.time() < deadline:
                        time.sleep(0.1)
                    continue

            # --- receive phase ---
            try:
                data = cls._client_socket.recv(4096)
                if not data:
                    # Peer closed
                    raise ConnectionError("Peer closed the connection.")
                message = data.decode(errors='replace')
                print(f"[pbrAudio Socket] Received: {message}")
                cls._handle_message(message)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[pbrAudio Socket] Receive error: {e}")
                # tear down and loop → reconnect
                if cls._client_socket is not None:
                    try:
                        cls._client_socket.close()
                    except Exception:
                        pass
                cls._client_socket = None
                cls._client_address = None
                cls._connected = False
                cls._status = 'WAITING' if cls._running else 'DISABLED'
                cls._tag_redraw()

        # thread exit
        cls._status = 'DISABLED'
        cls._connected = False
        cls._tag_redraw()

    # ------------------------------------------------------------------ #
    # Messaging
    # ------------------------------------------------------------------ #
    @classmethod
    def send(cls, message):
        """Send a message to the connected server."""
        if cls._client_socket is None or not cls._connected:
            return False
        try:
            print(f"[pbrAudio Socket] Send: {message}")
            cls._client_socket.sendall(message.encode())
            return True
        except Exception as e:
            print(f"[pbrAudio Socket] Send error: {e}")
            return False

    @classmethod
    def _handle_message(cls, message):
        """Process an incoming message from the pbrAudioDAW."""
        text = message.strip()
        if not text:
            return
        try:
            if text == "animation_play":
                bpy.ops.screen.animation_play()
            elif text == "animation_stop":
                bpy.ops.screen.animation_cancel(restore_frame=False)
            elif text.startswith("frame"):
                _, _, arg = text.partition(" ")
                try:
                    frame = int(arg.strip())
                except (TypeError, ValueError):
                    return
                scene = bpy.context.scene
                scene.frame_set(frame)
                # Force a viewport update on the next tick.
                cls._tag_redraw()
        except Exception as e:
            print(f"[pbrAudio Socket] handle message failed: {e}")

    # ------------------------------------------------------------------ #
    # UI helpers
    # ------------------------------------------------------------------ #
    @classmethod
    def _tag_redraw(cls):
        """Trigger a redraw so the panel updates its status label."""
        try:
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type in {'VIEW_3D'}:
                        area.tag_redraw()
        except Exception:
            pass
