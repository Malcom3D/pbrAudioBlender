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
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils

from .browser_widget import BrowserWidget
from .playback_widget import PlaybackWidget

_handles = []
_watch_timer = None
_modal_running = False

BROWSER: BrowserWidget | None = None
PLAYBACK: PlaybackWidget | None = None

# panel anchor (region pixels)
PANEL_MARGIN    = 16
PANEL_WIDTH     = 520
PANEL_ROW_H     = 28
PANEL_GAP       = 6

_draw_handle = None

# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------
def _engine_is_pbraudio() -> bool:
    scene = getattr(bpy.context, "scene", None)
    return scene is not None and scene.render.engine == 'PBRAUDIO'

def _panel_enabled() -> bool:
    scene = getattr(bpy.context, "scene", None)
    if scene is None or not hasattr(scene, "pbraudio"):
        return False
    return bool(getattr(scene.pbraudio, "show_viewport_panel", True))

def _get_view3d_region(context):
    region = context.region
    rv3d = context.region_data
    if region and region.type == 'WINDOW' and rv3d:
        return region, rv3d
    return None, None

def _ensure_widgets():
    """Lazy-create widget instances and share them across all viewports."""
    global BROWSER, PLAYBACK
    scene = bpy.context.scene

    if BROWSER is None:
        def _provider():
            bs = scene.get("_pbraudio_browser")
            if bs is not None:
                return bs
            try:
                from ...operators.playbackOT import _get_storage_engine
            except Exception:
                return None
            storage = _get_storage_engine(bpy.context)
            if storage is None:
                return None
            from pbrAudioDAW import BrowserState
            bs = BrowserState(storage)
            scene["_pbraudio_browser"] = bs
            return bs

        def _on_path(cwd):
            scene["_pbraudio_browser_cwd"] = list(cwd)
            for area in bpy.context.screen.areas if bpy.context.screen else ():
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        BROWSER = BrowserWidget(browser_state_provider=_provider, on_path_change=_on_path)

    if PLAYBACK is None:
        def _spec():
            try:
                from ...operators.playbackOT import _spec_from_browser_selection
            except Exception:
                return None
            return _spec_from_browser_selection(bpy.context)
        PLAYBACK = PlaybackWidget(spec_provider=_spec)

# ---------------------------------------------------------------------
# draw
# ---------------------------------------------------------------------
def draw_callback_px():
    if not _engine_is_pbraudio() or not _panel_enabled():
        return

    ctx = bpy.context
    region, rv3d = _get_view3d_region(ctx)
    if region is None or not region.width or not region.height:
        return

    _ensure_widgets()
    if BROWSER is None or PLAYBACK is None:
        return

    # Anchor top-left
    x0 = PANEL_MARGIN
    y_top = region.height - PANEL_MARGIN - PANEL_ROW_H

    # Browser row
    BROWSER.draw(ctx, region, rv3d, x0, y_top, PANEL_WIDTH, PANEL_ROW_H)

    # Play/stop row (narrower, right-aligned to browser width)
    y_play = y_top - PANEL_ROW_H - PANEL_GAP
    PLAYBACK.draw(ctx, region, rv3d, x0, y_play, 120, PANEL_ROW_H)

# ---------------------------------------------------------------------
# modal
# ---------------------------------------------------------------------
class PBRAUDIO_OT_widget_modal(bpy.types.Operator):
    """Consumes hover/click/wheel events over the 3D-viewport widgets."""
    bl_idname = "pbraudio.viewport_widget_modal"
    bl_label = "pbrAudio Viewport Widget Modal"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        global _modal_running

        if not _engine_is_pbraudio() or not _panel_enabled():
            _modal_running = False
            return {'FINISHED'}
        if context.area is None or context.area.type != 'VIEW_3D':
            _modal_running = False
            return {'FINISHED'}

        region = context.region
        if region is None or region.type != 'WINDOW':
            return {'PASS_THROUGH'}

        _ensure_widgets()
        if BROWSER is None or PLAYBACK is None:
            return {'PASS_THROUGH'}

        # Give the topmost (playback) widget first pass so it wins on overlap
        if PLAYBACK.on_event(context, region, event):
            return {'CONSUMED'}
        if BROWSER.on_event(context, region, event):
            return {'CONSUMED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        global _modal_running
        _modal_running = True
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# ---------------------------------------------------------------------
# topbar toggle (unchanged)) + watchdog + register/unregister
# ---------------------------------------------------------------------
class PBRAUDIO_OT_toggle_viewport_panel(bpy.types.Operator):
    """Toggle the pbrAudio widget overlay in the 3D viewport"""
    bl_idname = "pbraudio.toggle_viewport_panel"
    bl_label = "Toggle pbrAudio Viewport Panel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if not hasattr(scene, "pbraudio"):
            return {'CANCELLED'}
        scene.pbraudio.show_viewport_panel = not scene.pbraudio.show_viewport_panel

        global _modal_running
        if not scene.pbraudio.show_viewport_panel:
            _modal_running = False

        state = "enabled" if scene.pbraudio.show_viewport_panel else "disabled"
        self.report({'INFO'}, f"pbrAudio viewport panel {state}")
        return {'FINISHED'}

class TOPBAR_MT_pbraudio(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_pbraudio"
    bl_label = "pbrAudio"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        is_pbraudio = scene.render.engine == 'PBRAUDIO'

        if is_pbraudio:
            is_on = getattr(scene.pbraudio, "show_viewport_panel", True)
            icon = 'CHECKBOX_HLT' if is_on else 'CHECKBOX_DEHLT'
            layout.operator("pbraudio.toggle_viewport_panel", text="Show Viewport Panel", icon=icon, depress=is_on)
        else:
            col = layout.column()
            col.enabled = False
            col.label(text="Enable pbrAudio engine", icon='INFO')

def draw_topbar_menu(self, context):
    self.layout.menu("TOPBAR_MT_pbraudio", icon='SOUND')

def _on_engine_change(scene, depsgraph=None):
    try:
        for area in bpy.context.screen.areas if bpy.context.screen else ():
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    except Exception:
        pass

def _watchdog(_dummy=None):
    global _modal_running
    try:
        screen = getattr(bpy.context, "screen", None)
        if screen is None:
            return 1.0
        if not any(a.type == 'VIEW_3D' for a in screen.areas):
            return 1.0
        if not _engine_is_pbraudio() or not _panel_enabled():
            return 1.0
        if not _modal_running:
            try:
                bpy.ops.pbraudio.viewport_widget_modal('INVOKE_DEFAULT')
            except RuntimeError:
                pass
    except Exception:
        pass
    return 1.0

classes = [
    PBRAUDIO_OT_toggle_viewport_panel,
    PBRAUDIO_OT_widget_modal,
    TOPBAR_MT_pbraudio,
]

def register():
    global _draw_handle, _watch_timer
    for cls in classes:
        bpy.utils.register_class(cls)

    if _draw_handle is None:
        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (), 'WINDOW', 'POST_PIXEL')
        _handles.append(_draw_handle)

    if _on_engine_change not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_engine_change)

    if _watch_timer is None:
        _watch_timer = bpy.app.timers.register(_watchdog, first_interval=0.5, persistent=True)

    bpy.types.TOPBAR_MT_editor_menus.append(draw_topbar_menu)

def unregister():
    global _draw_handle, _watch_timer, _modal_running

    _modal_running = False

    try:
        bpy.types.TOPBAR_MT_editor_menus.remove(draw_topbar_menu)
    except (ValueError, AttributeError):
        pass

    if _watch_timer is not None:
        try:
            if bpy.app.timers.is_registered(_watch_timer):
                bpy.app.timers.unregister(_watch_timer)
        except Exception:
            pass
        _watch_timer = None

    if _on_engine_change in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_engine_change)

    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOWOW')
        except Exception:
            pass
        _draw_handle = None

    _handles.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
