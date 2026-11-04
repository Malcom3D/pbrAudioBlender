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
# Module-level state (persists across viewports via single set of handlers)
# ---------------------------------------------------------------------------
_handles = []          # list of (draw_handle) that live for the addon lifecycle
_button_rects = []     # list of {region, x, y, w, h, hover, owner}

MIN_SCALE = 0.5
MAX_SCALE = 2.5
REF_DISTANCE = 5.0
BASE_BUTTON_W = 120
BASE_BUTTON_H = 32
BASE_FONT_SIZE = 16
BASE_OFFSET_Y = 40

_draw_handle = None
_modal_handle = None


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------
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

# per-object selection 3d viewport panel
def _get_supported_objects():
    ctx = bpy.context
    return [o for o in ctx.selected_objects if hasattr(o, "pbraudio") and (o.pbraudio.source or o.pbraudio.output or o.pbraudio.environment or o.type == 'CAMERA')]

## per-scene selection 3d viewport panel
#def _get_supported_objects():
#    """Objects in the viewport eligible for the widget."""
#    ctx = bpy.context
#    results = []
#    for obj in ctx.visible_objects:
#        if not hasattr(obj, "pbraudio"):
#            continue
#        pb = obj.pbraudio
#        # Show widget on any pbrAudio-relevant object
#        if pb.source or pb.output or pb.environment or obj.type == 'CAMERA':
#            results.append(obj)
#    return results


def _is_playing():
    """Hook into pbrAudio playback state if/when available."""
    scene = bpy.context.scene
    if not hasattr(scene, "pbraudio"):
        return False
    return bool(getattr(scene.pbraudio, "preview_playing", False))


def _engine_is_pbraudio():
    scene = getattr(bpy.context, "scene", None)
    return scene is not None and scene.render.engine == 'PBRAUDIO'


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------
def draw_callback_px():
    if not _engine_is_pbraudio():
        return

    ctx = bpy.context
    region, rv3d = _get_view3d_region(ctx)
    if region is None:
        return

    # Only draw in the "real" viewport, not the render border area
    if not region.width or not region.height:
        return

    # Reset rects for this region
    _button_rects[:] = [
        r for r in _button_rects if r["region"] is not region
    ]

    objects = _get_supported_objects()
    if not objects:
        return

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')

    font_id = 0
    blf.color(font_id, 1, 1, 1, 1)

    for ob in objects objects:
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

        # Find existing hover state
        hover = False
        for r in _button_rects:
            if (r["region"] is region and r["owner"] == ob.name
                    and r.get("hover")):
                hover = True
                break

        bg = (0.15, 0.15, 0.15, 0.85) if not hover else (0.25, 0.35, 0.55, 0.95)

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

        # Label
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


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------
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
        # Example hook points:
        #   from pbrAudioCommon import Player
        #   ...
        try:
            scene = context.scene
            if hasattr(scene, "pbraudio"):
                scene.pbraudio.preview_playing = not getattr(
                    scene.pbraudio, "preview_playing", False
                )
        except Exception as e:
            self.report({'ERROR'}, f"Playback toggle failed: {e}")
            return {'CANCELLED'}

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Toggled playback for {obj.name}")
        return {'FINISHED'}


class PBRAUDIO_OT_widget_modal(bpy.types.Operator):
    """Consumes hover/click events over the 3D-viewport widget."""
    bl_idname = "pbraudio.viewport_widget_modal"
    bl_label = "pbrAudio Viewport Widget Modal"

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        region = context.region
        if region is None or region.type != 'WINDOW':
            return {'PASS_THROUGH'}

        if not _engine_is_pbraudio():
            # Nothing to do – let Blender handle the event
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
        # Attach draw handler once
        global _draw_handle
        if _draw_handle is None:
            _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_px, (), 'WINDOW', 'POST_PIXEL'
            )
            _handles.append(_draw_handle)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


# ---------------------------------------------------------------------------
# Registration – exposed to gui/__init__.py
# ---------------------------------------------------------------------------
classes = [
    PBRAUDIO_OT_playback_toggle,
    PBRAUDIO_OT_widget_modal,
]


def _start_modal(context):
    """Launch the modal operator once the first VIEW_3D is available."""
    try:
        bpy.ops.pbraudio.viewport_widget_modal('INVOKE_DEFAULT')
    except RuntimeError:
        pass


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Start the modal in a deferred way – context isn't fully ready at import
    bpy.app.timers.register(_start_modal, first_interval=0.5, persistent=False)


def unregister():
    if bpy.app.timers.is_registered(_start_modal):
        bpy.app.timers.unregister(_start_modal)

    global _draw_handle
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handlehandle = None
        _handles.clear()

    _button_rects.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
