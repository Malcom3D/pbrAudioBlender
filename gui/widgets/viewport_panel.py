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
import math
from gpu_extras.batch import batch_for_shader
from bpy_extras import view3d_utils

_handles = []
_button_rects = []          # {region, x, y, w, h, hover, owner}
_watch_timer = None         # persistent timer that (re)starts the modal
_modal_running = False

MIN_SCALE = 0.5
MAX_SCALE = 2.5
REF_DISTANCE = 5.0
BASE_BUTTON_W = 120
BASE_BUTTON_H = 32
BASE_FONT_SIZE = 16
BASE_OFFSET_Y = 40

_draw_handle = None


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _panel_enabled():
    scene = getattr(bpy.context, "scene", None)
    if scene is None or not hasattr(scene, "pbraudio"):
        return False
    return bool(getattr(scene.pbraudio, "show_viewport_panel", True))

def _get_distance_scale(world_pos, rv3d):
    view_loc = rv3d.view_matrix.inverted().translation
    distance = max((world_pos - view_loc).length, 1e-3)
    raw = math.log(REF_DISTANCE + 1.0) / math.log(distance + 1.0)
    return max(MIN_SCALE, min(MAX_SCALE, raw))


def _get_view3d_region(context):
    region = context.region
    rv3d = context.region_data
    if region and region.type == 'WINDOW' and rv3d:
        return region, rv3d
    return None, None


def _get_supported_objects():
    ctx = bpy.context
    if not ctx.selected_objects:
        return []
    return [
        o for o in ctx.selected_objects
        if hasattr(o, "pbraudio")
        and (o.pbraudio.source
             or o.pbraudio.output
             or o.pbraudio.environment
             or o.type == 'CAMERA'
             or o.type == 'MESH')
    ]


def _is_playing():
    scene = getattr(bpy.context, "scene", None)
    if scene is None or not hasattr(scene, "pbraudio"):
        return False
    return bool(getattr(scene.pbraudio, "preview_playing", False))

def _engine_is_pbraudio():
    scene = getattr(bpy.context, "scene", None)
    return scene is not None and scene.render.engine == 'PBRAUDIO'


# ----------------------------------------------------------------------------
# Draw handler (POST_PIXEL on SpaceView3D)
# ----------------------------------------------------------------------------

def draw_callback_px():
    if not _engine_is_pbraudio():
        return
    if not _panel_enabled():
        return

    ctx = bpy.context
    region, rv3d = _get_view3d_region(ctx)
    if region is None:
        return
    if not region.width or not region.height:
        return

    # Reset rects for *this* region only
    _button_rects[:] = [r for r in _button_rects if r["region"] is not region]

    objects = _get_supported_objects()
    if not objects:
        return

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')

    font_id = 0
    blf.color(font_id, 1, 1, 1, 1)

    for ob in objects:
        world_pos = ob.matrix_world.translation
        co_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
        if co_2d is None:
            continue

        scale = _get_distance_scale(world_pos, rv3d)
        btn_w = BASE_BUTTON_W * scale
        btn_h = BASE_BUTTON_H * scale
        offset_y = BASE_OFFSET_Y * scale
        font_size = int(max(8, round(BASE_FONT_SIZE * scale)))

        x = co_2d.x - btn_w / 2
        y = co_2d.y + offset_y

        hover = any(
            r["region"] is region and r["owner"] == ob.name and r.get("hover")
            for r in _button_rects
        )

        bg = (0.15, 0.15, 0.15, 0.85) if not hover else (0.25, 0.35, 0.55, 0.95)

        batch = batch_for_shader(
            shader, 'TRI_FAN',
            {"pos": [(x, y), (x + btn_w, y),
                     (x + btn_w, y + btn_h), (x, y + btn_h)]},
        )
        shader.uniform_float("color", bg)
        batch.draw(shader)

        blf.size(font_id, font_size)
        text = "■  Stop" if _is_playing() else "▶  Play"
        tw, th = blf.dimensions(font_id, text)
        blf.position(font_id, x + (btn_w - tw) / 2, y + (btn_h - th) / 2, 0)
        blf.draw(font_id, text)

        _button_rects.append({
            "region": region,
            "x": x, "y": y, "w": btn_w, "h": btn_h,
            "hover": hover,
            "owner": ob.name,
        })

    gpu.state.blend_set('NONE')


# ----------------------------------------------------------------------------
# Operators
# ----------------------------------------------------------------------------

class PBRAUDIO_OT_playback_toggle(bpy.types.Operator):
    bl_idname = "pbraudio.playback_toggle"
    bl_label = "Toggle pbrAudio Playback"
    bl_options = {'REGISTER', 'UNDO'}

    object_name: bpy.props.StringProperty(name="Object Name", default="")

    def execute(self, context):
        obj = context.scene.objects.get(self.object_name)
        if not obj:
            self.report({'WARNING'}, "Object no longer exists")
            return {'CANCELLED'}

        # TODO: call into pbrAudio acoustic preview / player here.
        try:
            scene = context.scene
            if hasattr(scene, "pbraudio"):
                scene.pbraudio.preview_playing = not getattr(scene.pbraudio, "preview_playing", False)
        except Exception as e:
            self.report({'ERROR'}, f"Playback toggle failed: {e}")
            return {'CANCELLED'}

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Toggled playback for {obj.name}")
        return {'FINISHED'}

class PBRAUDIO_OT_toggle_viewport_panel(bpy.types.Operator):
    """Toggle the pbrAudio 3D viewport overlay panel"""
    bl_idname = "pbraudio.toggle_viewport_panel"
    bl_label = "Toggle pbrAudio Viewport Panel"
    bl_description = "Toggle the pbrAudio play/stop overlay in the 3D viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if not hasattr(scene, "pbraudio"):
            return {'CANCELLED'}

        # Flip the property; its update callback triggers redraw
        scene.pbraudio.show_viewport_panel = not scene.pbraudio.show_viewport_panel

        # Immediately stop the modal if we just disabled it
        global _modal_running
        if not scene.pbraudio.show_viewport_panel:
            _modal_running = False

        state = "enabled" if scene.pbraudio.show_viewport_panel else "disabled"
        self.report({'INFO'}, f"pbrAudio viewport panel {state}")
        return {'FINISHED'}

class PBRAUDIO_OT_widget_modal(bpy.types.Operator):
    """Consumes hover/click events over the 3D-viewport widget."""
    bl_idname = "pbraudio.viewport_widget_modal"
    bl_label = "pbrAudio Viewport Widget Modal"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        global _modal_running

        # If engine no longer pbrAudio, stop cleanly so the timer can restart
        # us later when the user comes back.
        if not _engine_is_pbraudio():
            _modal_running = False
            return {'FINFINISHED'}
        if not _panel_enabled():
            _modal_running = False
            return {'FINISHED'}

        # Context area may have changed (user switched area type). Veto out.
        if context.area is None or context.area.type != 'VIEW_3D':
            _modal_running = False
            return {'FINISHED'}

        region = context.region
        if region is None or region.type != 'WINDOW':
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            mx, my = event.mouse_region_x, event.mouse_region_y
            changed = False
            for r in _button_rects:
                if r["region"] is not region:
                    continue
                inside = (r["x"] <= mx <= r["x"] + r["w"]
                          and r["y"] <= my <= r["y"] + r["h"])
                if inside != r["hover"]:
                    r["hover"] = inside
                    changed = True
            if changed:
                region.tag_redraw()
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mx, my = event.mouse_region_x, event.mouse_region_y
            for r in _button_rects:
                if r["region"] is not region:
                    continue
                if (r["x"] <= mx <= r["x"] + r["w"]
                        and r["y"] <= my <= r["y"] + r["h"]):
                    bpy.ops.pbraudio.playback_toggle('INVOKE_DEFAULT',
                                                     object_name=r["owner"])
                    return {'CONSUMED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        global _modal_running
        _modal_running = True
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# ----------------------------------------------------------------------------
# Engine-change handler: force a redraw when user toggles engines
# ----------------------------------------------------------------------------

def _on_engine_change(scene, depsgraph=None):
    try:
        for area in bpy.context.screen.areas if bpy.context.screen else ():
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    except Exception:
        pass

# ------------------------------------------------------------------
# Topbar menu: "pbrAudio"
# ------------------------------------------------------------------

class TOPBAR_MT_pbraudio(bpy.types.Menu):
    """pbrAudio topbar menu"""
    bl_idname = "TOPBAR_MT_pbraudio"
    bl_label = "pbrAudio"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Only show detailed items when pbrAudio is the active engine
        is_pbraudio = scene.render.engine == 'PBRAUDIO'

        # --- Viewport Panel toggle ---
        if is_pbraudio:
            is_on = getattr(scene.pbraudio, "show_viewport_panel", True)
            icon = 'CHECKBOX_HLT' if is_on else 'CHECKBOX_DEHLT'
            layout.operator("pbraudio.toggle_viewport_panel", text="Show Viewport Panel", icon=icon, depress=is_on)
        else:
            col = layout.column()
            col.enabled = False
            col.label(text="Enable pbrAudio engine", icon='INFO')

        layout.separator()

#        # --- Render / Preview shortcuts ---
#        col = layout.column()
#        col.enabled = is_pbraudio
#
#        if scene.pbraudio.enable_acoustic_preview:
#            col.operator("render.pbraudio_preview_toggle", text="Audio Preview", icon='SOUND)
#
#        col.operator("render.render", text="Render Audio", icon='RENDER_STILL')
#        col.operator("render.render", text="Render Animation", icon='RENDER_ANIMATION').animation = True

def draw_topbar_menu(self, context):
    """Add the pbrAudio menu to the topbar editor menus."""
    self.layout.menu("TOPBAR_MT_pbraudio", icon='SOUND')

# ----------------------------------------------------------------------------
# Watchdog timer: ensures exactly one modal is running whenever a VIEW_3D
# exists and the engine is PBRAUDIO.
# ----------------------------------------------------------------------------

def _watchdog(_dummy=None):
    global _modal_running

    try:
        ctx = bpy.context
        screen = getattr(ctx, "screen", None)
        if screen is None:
            return 1.0

        has_view3d = any(a.type == 'VIEW_3D' for a in screen.areas)
        if not has_view3d:
            return 1.0

        if not _engine_is_pbraudio():
            return 1.0
        if not _panel_enabled():
            return 1.0

        if not _modal_running:
            try:
                bpy.ops.pbraudio.viewport_widget_modal('INVOKE_DEFAULT')
            except RuntimeError:
                pass
    except Exception:
        pass

    return 1.0  # seconds — re-check

# ----------------------------------------------------------------------------
# Register / Unregister
# ----------------------------------------------------------------------------

classes = [
    PBRAUDIO_OT_playback_toggle,
    PBRAUDIO_OT_widget_modal,
    PBRAUDIO_OT_toggle_viewport_panel,
    TOPBAR_MT_pbraudio
]

def register():
    global _draw_handle, _watch_timer

    for cls in classes:
        bpy.utils.register_class(cls)

    # Attach the draw handler *always* — regardless of the modal state.
    if _draw_handle is None:
        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (), 'WINDOW', 'POST_PIXEL')
        _handles.append(_draw_handle)

    # Hook engine-change so we can redraw immediately when the user switches.
    if _on_engine_change not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_engine_change)

    # Persistent watchdog timer (fires every 1s, cheap)
    if _watch_timer is None:
        _watch_timer = bpy.app.timers.register(_watchdog, first_interval=0.5, persistent=True)

    # Add the topbar menu
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
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None

    _handles.clear()
    _button_rects.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
