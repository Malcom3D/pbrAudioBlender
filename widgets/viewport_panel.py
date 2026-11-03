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

# ---------------------------------------------------------------------------
# Widget state (kept in a module-level dict to survive redraws)
# ---------------------------------------------------------------------------
_handles = []            # list of (space, region) -> draw handle
_button_rects = []       # list of dicts: {region, x, y, w, h, callback, hover}

# Tunable constants
MIN_SCALE = 0.5       # smallest the widget can shrink to
MAX_SCALE = 2.5       # largest the widget can grow to
REF_DISTANCE = 5.0    # world distance (m) at which scale = 1.0
BASE_BUTTON_W = 120
BASE_BUTTON_H = 32
BASE_FONT_SIZE = 16
BASE_OFFSET_Y = 40
BUTTON_W = 120
BUTTON_H = 32
BUTTON_OFFSET_Y = 40     # pixels above the object

def _get_distance_scale(region, rv3d, world_pos):
    view_loc = rv3d.view_matrix.inverted().translation
    distance = max((world_pos - view_loc).length, 1e-3)

    # Log-distance gives a much gentler ramp than pure 1/d
    # scale = 1.0 at REF_DISTANCE, decreasing as distance grows
    raw = math.log(REF_DISTANCE + 1.0) / math.log(distance + 1.0)
    return max(MIN_SCALE, min(MAX_SCALE, raw))

#def _get_distance_scale(region, rv3d, world_pos):
#    """
#    Compute a scale factor for the widget based on the distance
#    between the camera and the anchor point.
#
#    Returns:
#        float: scale factor clamped to [MIN_SCALE, MAX_SCALE]
#    """
#    view_loc = rv3d.view_matrix.inverted().translation
#    distance = (world_pos - view_loc).length
#
#    if distance <= 1e-6:
#        return MAX_SCALE
#
#    # Linear inverse relationship with distance, normalized around REF_DISTANCE
#    scale = REF_DISTANCE / distance
#
#    return max(MIN_SCALE, min(MAX_SCALE, scale))

def _get_target_object():
    """Return the object to attach the button to (active object)."""
    ctx = bpy.context
    ob = ctx.active_object
    return ob if ob and ob.type in {'MESH', 'EMPTY', 'LIGHT', 'CAMERA'} else None


def _get_view3d_region(context):
    region = context.region
    rv3d = context.region_data
    if region and region.type == 'WINDOW' and rv3d:
        return region, rv3d
    return None, None

def draw_callback_px():
    ctx = bpy.context
    region, rv3d = _get_view3d_region(ctx)
    if region is None:
        return

    ob = _get_target_object()
    if ob is None:
        return

    world_pos = ob.matrix_world.translation
    co_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
    if co_2d is None:
        return

    # --- scale by view distance ---
    scale = _get_distance_scale(region, rv3d, world_pos)

    btn_w = BASE_BUTTON_W * scale
    btn_h = BASE_BUTTON_H * scale
    offset_y = BASE_OFFSET_Y * scale
    font_size = BASE_FONT_SIZE * scale

    x = co_2d.x - btn_w / 2
    y = co_2d.y + offset_y

    hover = _button_rects[0]["hover"] if _button_rects else False

    # --- background ---
    bg = (0.15, 0.15, 0.15, 0.85) if not hover else (0.25, 0.35, 0.55, 0.95)
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {"pos": [
            (x, y),
            (x + btn_w, y),
            (x + btn_w, y + btn_h),
            (x, y + btn_h),
        ]},
    )
    shader.uniform_float("color", bg)
    batch.draw(shader)
    gpu.state.blend_set('NONE')

    # --- label ---
    font_id = 0
    blf.size(font_id, font_size)
    text = "▶  Play" if not _is_playing() else "■  Stop"
    tw, th = blf.dimensions(font_id, text)
    blf.color(font_id, 1, 1, 1, 1)
    blf.position(
        font_id,
        x + (btn_w - tw) / 2,
        y + (btn_h - th) / 2,
        0,
    )
    blf.draw(font_id, text)

    # --- store rect for hit-testing ---
    _button_rects[:] = [{
        "region": region,
        "x": x, "y": y, "w": btn_w, "h": btn_h,
        "hover": hover,
    }]


#def draw_callback_px():
#    """Called every time the 3D viewport redraws."""
#    ctx = bpy.context
#    region, rv3d = _get_view3d_region(ctx)
#    if region is None:
#        return
#
#    ob = _get_target_object()
#    if ob is None:
#        return
#
#    # 3D world pos -> 2D screen coords
#    world_pos = ob.matrix_world.translation
#    co_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
#    if co_2d is None:
#        return  # object is behind camera
#
#    x = co_2d.x - BUTTON_W / 2
#    y = co_2d.y + BUTTON_OFFSET_Y
#
#    # If the mouse is inside this rect (tracked by operator/modal), highlight
#    hover = _button_rects[0]["hover"] if _button_rects else False
#
#    # Background
#    bg = (0.15, 0.15, 0.15, 0.85) if not hover else (0.25, 0.35, 0.55, 0.95)
#    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
#    gpu.state.blend_set('ALPHA')
#    batch = batch_for_shader(
#        shader, 'TRI_FAN',
#        {"pos": [
#            (x, y),
#            (x + BUTTON_W, y),
#            (x + BUTTON_W, y + BUTTON_H),
#            (x, y + BUTTON_H),
#        ]},
#    )
#    shader.uniform_float("color", bg)
#    batch.draw(shader)
#    gpu.state.blend_set('NONE')
#
#    # Label
#    font_id = 0
#    blf.size(font_id, 16)
#    text = "▶  Play" if not _is_playing() else "■  Stop"
#    tw, th = blf.dimensions(font_id, text)
#    blf.color(font_id, 1, 1, 1, 1)
#    blf.position(font_id, x + (BUTTON_W - tw) / 2, y + (BUTTON_H - th) / 2, 0)
#    blf.draw(font_id, text)
#
#    # Store rect in region space so click handling can test it
#    _button_rects[:] = [{
#        "region": region,
#        "x": x, "y": y, "w": BUTTON_W, "h": BUTTON_H,
#        "hover": hover,
#    }]


def _is_playing():
    # Placeholder - link to your pbrAudio playback state later
    return False


# ---------------------------------------------------------------------------
# Playback operator (to hook up to pbrAudio)
# ---------------------------------------------------------------------------
class PBR_OT_playback_toggle(bpy.types.Operator):
    bl_idname = "pbr_audio.playback_toggle"
    bl_label = "Toggle Playback"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # TODO: call your pbrAudio play/stop here
        self.report({'INFO'}, "Playback toggled (hook me to pbrAudio)")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Modal operator that turns clicks on the button into operator calls
# ---------------------------------------------------------------------------
class PBR_OT_button_modal(bpy.types.Operator):
    """Keeps listening for clicks/hover over widgets in the 3D Viewport"""
    bl_idname = "pbr_audio.widget_modal"
    bl_label = "PBR Widget Modal"

    _timer = None
    _registered = False

    def modal(self, context, event):
        region = context.region
        rv3d = context.region_data

        # Only care about the 3D viewport WINDOW region
        if region is None or region.type != 'WINDOW':
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            mx, my = event.mouse_region_x, event.mouse_region_y
            hovered = False
            for r in _button_rects:
                if r["region"] is not region:
                    continue
                if r["x"] <= mx <= r["x"] + r["w"] and r["y"] <= my <= r["y"] + r["h"]:
                    r["hover"] = True
                    hovered = True
            for r in _button_rects:
                if r["region"] is region and not hovered:
                    r["hover"] = False
            region.tag_redraw()
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mx, my = event.mouse_region_x, event.mouse_region_y
            for r in _button_rects:
                if r["region"] is not region:
                    continue
                if r["x"] <= mx <= r["x"] + r["w"] and r["y"] <= my <= r["y"] + r["h"]:
                    bpy.ops.pbr_audio.playback_toggle('INVOKE_DEFAULT')
                    return {'CONSUMED'}

        return {'PASS_THROUGH'}

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        if not PBR_OT_button_modal._registered:
            handler = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_px, (), 'WINDOW', 'POST_PIXEL'
            )
            _handles.append(handler)
            PBR_OT_button_modal._registered = True

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


# ---------------------------------------------------------------------------
# Menu hook + registration
# ---------------------------------------------------------------------------
def menu_func(self, context):
    self.layout.operator("pbr_audio.widget_modal",
                         text="Start PBR Audio Button")


def register():
    bpy.utils.register_class(PBR_OT_playback_toggle)
    bpy.utils.register_class(PBR_OT_button_modal)
    bpy.types.VIEW3D_MT_editor_menus.append(menu_func)


def unregister():
    for h in _handles:
        bpy.types.SpaceView3D.draw_handler_remove(h, 'WINDOW')
    _handles.clear()
    _button_rects.clear()
    PBR_OT_button_modal._registered = False
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_func)
    bpy.utils.unregister_class(PBR_OT_button_modal)
    bpy.utils.unregister_class(PBR_OT_playback_toggle)


if __name__ == "__main__":
    register()

