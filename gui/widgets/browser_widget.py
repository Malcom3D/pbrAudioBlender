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

"""
Single-line pbrAudioStorage path browser.

Renders as:   [ < ]  objects / rigidbody / 3 / body  [ > ]
                         ^ current selection window

Wheel over the widget = cycle sibling entries in the current directory.
Left/right arrows = go up/down one level.
Clicking on a path segment = cd to that segment.
"""

import blf
import gpu
from gpu_extras.batch import batch_for_shader
from typing import List, Optional

from .widget_base import ViewportWidget


BG_COLOR       = (0.12, 0.12, 0.12, 0.85)
BG_HOVER       = (0.16, 0.16, 0.18, 0.95)
FG_SEGMENT     = (0.78, 0.82, 0.90, 1.0)
FG_SEGMENT_HOV = (1.00, 0.82, 0.30, 1.0)
FG_ARROW       = (0.70, 0.70, 0.72, 1.0)
FG_MUTED       = (0.55, 0.55, 0.58, 1.0)

BASE_FONT_SIZE = 14
BASE_PAD_X     = 10
ARROW_W        = 18


class BrowserWidget(ViewportWidget):
    name = "browser"

    def __init__(self, browser_state_provider, on_path_change=None):
        """
        browser_state_provider : callable() -> BrowserState
            A live provider so we can rebuild if the storage engine changes.
        on_path_change : callable(cwd: list[str]) | None
            Fired after every successful navigation.
        """
        super().__init__()
        self._provider = browser_state_provider
        self._on_path_change = on_path_change
        # rects per region: list of {kind, x, y, w, h, payload, hover}
        self._hits: dict[int, list[dict]] = {}

    # -- helpers ------------------------------------------------------
    def _bs(self):
        return self._provider()

    def _rects(self, region) -> list:
        return self._hits.setdefault(region.as_pointer(), [])

    def _reset_rects(self, region):
        self._hits[region.as_pointer()] = []

    # -- draw ---------------------------------------------------------
    def draw(self, ctx, region, rv3d, x, y, w, h):
        self._reset_rects(region)
        bs = self._bs()
        if bs is None:
            self._draw_muted(region, x, y, w, h, "no storage")
            return

        st = self.state(region)

        # -- background
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        hover_bg = st.get("hover", False)
        shader.uniform_float("color", BG_HOVER if hover_bg else BG_COLOR)
        _rect_fill(shader, x, y, w, h)
        gpu.state.blend_set('NONE')

        font_id = 0
        blf.size(font_id, BASE_FONT_SIZE)

        cwd = bs.cwd
        sep_h = BASE_FONT_SIZE + 6
        baseline = y + (h - sep_h) / 2 + 2

        cx = x + BASE_PAD_X
        cy_mid = y + h / 2

        # -- left arrow
        self._draw_arrow(region, cx, cy_mid, ARROW_W, "<", "up", st.get("arrow_up_hover", False))
        cx += ARROW_W + 6

        # -- breadcrumb segments
        # root
        seg = "(root)"
        x0 = cx
        tw = _text_width(font_id, seg)
        self._draw_segment(region, cx, baseline, seg, x0, w=tw, hover=st.get(f"seg_hover_{0}", False), payload=[], is_last=(len(cwd) == 0))
        cx += tw + 6
        if len(cwd) == 0:
            cx += 4  # small spacer
        for i, seg_txt in enumerate(cwd):
            # separator
            slash = "/"
            sw = _text_width(font_id, slash)
            blf.color(font_id, *FG_MUTED)
            blf.position(font_id, cx, baseline, 0)
            blf.draw(font_id, slash)
            cx += sw + 4

            seg = seg_txt
            x0 = cx
            tw = _text_width(font_id, seg)
            self._draw_segment(region, cx, baseline, seg, x0, w=tw, hover=st.get(f"seg_hover_{i+1}", False), payload=cwd[:i+1], is_last=(i == len(cwd) - 1))
            cx += tw + 6

        # -- right arrow (next sibling in current dir)
        arrow_x = x + w - BASE_PAD_X - ARROW_W
        self._draw_arrow(region, arrow_x, cy_mid, ARROW_W, ">", "down",
                         st.get("arrow_dn_hover", False))

        # -- sibling window hint on the right
        label = self._sibling_hint(bs)
        if label:
            lw = _text_width(font_id, label)
            lx = arrow_x - lw - 12
            if lx > cx + 8:
                blf.color(font_id, *FG_MUTED)
                blf.position(font_id, lx, baseline, 0)
                blf.draw(font_id, label)

    # -- drawing helpers ---------------------------------------------
    def _draw_muted(self, region, x, y, w, h, text):
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        shader.uniform_float("color", BG_COLOR)
        _rect_fill(shader, x, y, w, h)
        gpu.state.blend_set('NONE')
        font_id = 0
        blf.size(font_id, BASE_FONT_SIZE)
        blf.color(font_id, *FG_MUTED)
        blf.position(font_id, x + BASE_PAD_X, y + (h - BASE_FONT_SIZE) / 2 + 2, 0)
        blf.draw(font_id, text)

    def _draw_segment(self, region, x, baseline, text, rx, w, hover, payload, is_last):
        font_id = 0
        blf.color(font_id, *(FG_SEGMENT_HOV if hover else FG_SEGMENT))
        blf.position(font_id, x, baseline, 0)
        blf.draw(font_id, text)

        # hit rect
        th = BASE_FONT_SIZE + 6
        self._rects(region).append({
            "kind": "segment",
            "x": rx, "y": baseline - 3, "w": w, "h": th,
            "payload": payload,
            "hover": hover,
        })

    def _draw_arrow(self, region, x, cy_mid, size, glyph, kind, hover):
        font_id = 0
        blf.size(font_id, BASE_FONT_SIZE + 4)
        tw = _text_width(font_id, glyph)
        blf.color(font_id, *(FG_SEGMENT_HOV if hover else FG_ARROW))
        blf.position(font_id, x + (size - tw) / 2, cy_mid - (BASE_FONT_SIZE + 4) / 2 + 2, 0)
        blf.draw(font_id, glyph)
        blf.size(font_id, BASE_FONT_SIZE)

        self._rects(region).append({
            "kind": kind,
            "x": x, "y": cy_mid - 10, "w": size, "h": 20,
            "payload": None,
            "hover": hover,
        })

    def _sibling_hint(self, bs) -> str:
        """Show how many siblings exist next to the current cwd."""
        try:
            parent = bs.cwd[:-1]
            entries = bs._children(parent) if bs.cwd else bs._children([])
            n = len([e for e in entries if e.kind != "signal"])
            if n <= 1:
                return ""
            cur = bs.cwd[-1] if bs.cwd else None
            if cur is None:
                return f"{n} entries"
            try:
                idx = [e.name for e in entries if e.kind != "signal"].index(cur)
                return f"{idx+1}/{n}"
            except ValueError:
                return f"{n} entries"
        except Exception:
            return ""

    # -- hit-testing --------------------------------------------------
    def hit(self, region, mx, my) -> bool:
        return any(
            r["x"] <= mx <= r["x"] + r["w"] and
            r["y"] <= my <= r["y"] + r["h"]
            for r in self._rects(region)
        )

    # -- events -------------------------------------------------------
    def on_event(self, ctx, region, event) -> bool:
        if event.type not in {"MOUSEMOVE", "WHEELUPMOUSE", "WHEELDOWNMOUSE", "LEFTMOUSE"}:
            return False

        mx, my = event.mouse_region_x, event.mouse_region_y
        rects = self._rects(region)
        if not rects:
            return False

        # region-level hover flag
        st = self.state(region)
        on_widget = any(r["x"] <= mx <= r["x"] + r["w"] and
                        r["y"] <= my <= r["y"] + r["h"] for r in rects)
        if st.get("hover") != on_widget:
            st["hover"] = on_widget
            region.tag_redraw()

        # per-hit hover
        changed = False
        for r in rects:
            h = r["x"] <= mx <= r["x"] + r["w"] and r["y"] <= my <= r["y"] + r["h"]
            if h != r["hover"]:
                r["hover"] = h
                changed = True
                key = (
                    f"seg_hover_{len(r['payload'])}" if r["kind"] == "segment"
                    else ("arrow_up_hover" if r["kind"] == "up"
                          else "arrow_dn_hover" if r["kind"] == "down" else None)
                )
                if key:
                    st[key] = h
        if changed:
            region.tag_redraw()

        if not on_widget:
            # still want wheel to pass through if the mouse isn't on us;
            # return True only if we're hovering so that wheel-goes-to-3D nav
            return False

        # wheel → cycle siblings in current dir
        if event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self._cycle_sibling(ctx, -1 if event.type == "WHEELUPMOUSE" else +1)
            return True

        # click
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            for r in rects:
                if not (r["x"] <= mx <= r["x"] + r["w"] and r["y"] <= my <= r["y"] + r["h"]):
                    continue
                if r["kind"] == "segment":
                    self._cd_abs(ctx, r["payload"])
                    return True
                if r["kind"] == "up":
                    self._cd_rel(ctx, "..")
                    return True
                if r["kind"] == "down":
                    # "down" = first child of the current directory
                    self._enter_first_child(ctx)
                    return True
        return False

    # -- navigation helpers ------------------------------------------
    def _cd_abs(self, ctx, path: list):
        bs = self._bs()
        target = "/" + "/".join(str(s) for s in path) if path else "/"
        try:
            bs.cd(target)
        except Exception as e:
            _report(ctx, f"pbrAudio browser: {e}", "WARNING")
            return
        self._after_change(ctx)

    def _cd_rel(self, ctx, rel: str):
        bs = self._bs()
        try:
            bs.cd(rel)
        except Exception as e:
            _report(ctx, f"pbrAudio browser: {e}", "WARNING")
            return
        self._after_change(ctx)

    def _enter_first_child(self, ctx):
        bs = self._bs()
        try:
            entries = bs._children(bs.cwd)
        except Exception:
            return
        for e in entries:
            if e.kind == "signal":
                continue
            try:
                bs.cd(e.name)
                self._after_change(ctx)
                break
            except Exception:
                continue

    def _cycle_sibling(self, ctx, delta: int):
        bs = self._bs()
        if not bs.cwd:
            return
        parent = bs.cwd[:-1]
        try:
            entries = bs._children(parent)
        except Exception:
            return
        names = [e.name for e in entries if e.kind != "signal"]
        if not names:
            return
        cur = bs.cwd[-1]
        if cur not in names:
            return
        idx = (names.index(cur) + delta) % len(names)
        try:
            bs.cd(names[idx])
            self._after_change(ctx)
        except Exception as e:
            _report(ctx, f"pbrAudio browser: {e}", "WARNING")

    def _after_change(self, ctx):
        if self._on_path_change:
            self._on_path_change(self._bs().cwd)


# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------
def _rect_fill(shader, x, y, w, h):
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {"pos": [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]},
    )
    batch.draw(shader)

def _text_width(font_id, text):
    if not text:
        return 0.0
    w, _ = blf.dimensions(font_id, text)
    return w

def _report(ctx, msg, level="INFO"):
    try:
        bpy.context.window_manager  # noqa
    except Exception:
        pass
    # operators usually report; widgets can't, so queue to log
    print(f"[pbrAudio widget] {msg}")
