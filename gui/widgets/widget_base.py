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
Common base for all viewport widgets.

Each widget is instanced once, but draws once per 3D-View region per
frame. It owns a dict of per-region state (hover, scroll offset, rects).
"""

from typing import Dict, Any, Optional

class ViewportWidget:
    #: short id used as a registry key; must be unique
    name: str = "widget"

    def __init__(self) -> None:
        # per-region state, keyed by region.as_pointer()
        self._region_state: Dict[int, Dict[str, Any]] = {}

    # -- lifecycle ---------------------------------------------------
    def state(self, region) -> Dict[str, Any]:
        rk = region.as_pointer()
        st = self._region_state.get(rk)
        if st is None:
            st = {}
            self._region_state[rk] = st
        return st

    # -- draw ---------------------------------------------------------
    def draw(self, ctx, region, rv3d, x: float, y: float, w: float, h: float) -> None:
        """Draw the widget in the given rect (region pixel space)."""
        raise NotImplementedError

    # -- interaction --------------------------------------------------
    def hit(self, region, mx: float, my: float) -> bool:
        """True if the mouse is over the widget's bounding box."""
        raise NotImplementedError

    def on_event(self, ctx, region, event) -> bool:
        """
        Handle a modal event if it targets this widget.
        Return True if consumed (modal returns CONSUMED / RUNNING_MODAL).
        """
        return False

    # -- tooltip ------------------------------------------------------
    def tooltip(self) -> Optional[str]:
        return None
