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
import math
from .baseND import AcousticMaterialNode
from mathutils import Vector

# -------------------------------------------------------------------
# Property Group for a single Frequency–Magnitude point
# -------------------------------------------------------------------
class AcousticFreqPoint(bpy.types.PropertyGroup):
    frequency: bpy.props.FloatProperty(
        name="Freq (Hz)",
        description="Frequency in Hertz",
        default=1000.0,
        min=1.0,
        soft_max=20000.0
    )
    magnitude: bpy.props.FloatProperty(
        name="Mag (dB)",
        description="Magnitude (e.g. dB, absorption coefficient, etc.)",
        default=0.0,
        soft_min=-60.0,
        soft_max=10.0
    )

# -------------------------------------------------------------------
# Custom Node Tree (container for our nodes)
# -------------------------------------------------------------------
class AcousticMaterialNodeTree(bpy.types.NodeTree):
    """Node tree for acoustic material design"""
    bl_idname = 'AcousticMaterialNodeTree'
    bl_label = 'Acoustic Material Node Tree'
    bl_icon = 'SOUND'

# -------------------------------------------------------------------
# The actual node that draws the frequency response
# -------------------------------------------------------------------
class AcousticFreqResponseNode(AcousticMaterialNode):
    bl_idname = 'AcousticFreqResponseNode'
    bl_label = 'Frequency Response Shape'
    bl_icon = 'GRAPH'

    # Collection of user‑defined points
    points: bpy.props.CollectionProperty(type=AcousticFreqPoint)
    # Index of the currently selected point in the UI list
    point_index: bpy.props.IntProperty(default=0)

    # Scaling factors for the generated curve
    x_scale: bpy.props.FloatProperty(
        name="X Scale",
        description="Scales the log10(frequency) coordinate",
        default=2.0,
        min=0.1,
        max=10.0
    )
    y_scale: bpy.props.FloatProperty(
        name="Y Scale",
        description="Scales the magnitude coordinate",
        default=0.05,
        min=0.01,
        max=1.0
    )

    # Optional X offset (moves the curve along X)
    x_offset: bpy.props.FloatProperty(
        name="X Offset",
        default=-5.0,
        description="Shift the curve left/right"
    )

    def init(self, context):
        """Add two example points when the node is first created"""
        pt1 = self.points.add()
        pt1.frequency = 100.0
        pt1.magnitude = -20.0
        pt2 = self.points.add()
        pt2.frequency = 1000.0
        pt2.magnitude = 0.0
        pt3 = self.points.add()
        pt3.frequency = 10000.0
        pt3.magnitude = -10.0

    def draw_buttons(self, context, layout):
        """UI inside the node"""
        # --- List of points ---
        row = layout.row()
        col = row.column()
        col.template_list(
            "UI_UL_list", "freq_points", self, "points",
            self, "point_index", rows=3
        )

        # Add / remove buttons
        col = row.column(align=True)
        col.operator("acoustic.point_add", icon='ADD', text="")
        col.operator("acoustic.point_remove", icon='REMOVE', text="")

        # --- Point properties (when a point is selected) ---
        if self.point_index < len(self.points):
            pt = self.points[self.point_index]
            box = layout.box()
            box.label(text="Selected Point", icon='DOT')
            box.prop(pt, "frequency")
            box.prop(pt, "magnitude")

        # --- Scaling and generation ---
        layout.separator()
        layout.prop(self, "x_scale")
        layout.prop(self, "y_scale")
        layout.prop(self, "x_offset")
        layout.separator()
        layout.operator("acoustic.generate_curve", text="Generate Curve", icon='OUTLINER_OB_CURVE')

    def draw_buttons_ext(self, context, layout):
        """Extra UI in the sidebar (N‑panel) – same as main UI"""
        self.draw_buttons(context, layout)

# -------------------------------------------------------------------
# Operators for managing points and generating the curve
# -------------------------------------------------------------------
class ACOUSTIC_OT_point_add(bpy.types.Operator):
    bl_idname = "acoustic.point_add"
    bl_label = "Add Frequency Point"
    bl_description = "Add a new frequency–magnitude point"

    def execute(self, context):
        node = context.node
        if node and hasattr(node, "points"):
            node.points.add()
            node.point_index = len(node.points) - 1
        return {'FINISHED'}

class ACOUSTIC_OT_point_remove(bpy.types.Operator):
    bl_idname = "acoustic.point_remove"
    bl_label = "Remove Frequency Point"
    bl_description = "Remove the selected point"

    def execute(self, context):
        node = context.node
        if node and hasattr(node, "points") and node.points:
            if node.point_index < len(node.points):
                node.points.remove(node.point_index)
                node.point_index = min(node.point_index, len(node.points) - 1)
        return {'FINISHED'}

class ACOUSTIC_OT_generate_curve(bpy.types.Operator):
    bl_idname = "acoustic.generate_curve"
    bl_label = "Generate Curve from Frequency Response"
    bl_description = "Create or update a 2D curve representing the frequency response"

    def execute(self, context):
        node = context.node
        if not node or not hasattr(node, "points"):
            self.report({'ERROR'}, "No frequency response node selected")
            return {'CANCELLED'}

        # Gather points, sort by frequency
        pts = [(p.frequency, p.magnitude) for p in node.points]
        if not pts:
            self.report({'WARNING'}, "No frequency points defined")
            return {'CANCELLED'}

        pts.sort(key=lambda x: x[0])   # ascending frequency

        # Compute 3D coordinates: X = x_offset + x_scale * log10(freq)
        # (skip zero or negative frequencies)
        coords = []
        for freq, mag in pts:
            if freq <= 0:
                continue
            x = node.x_offset + node.x_scale * math.log10(freq)
            y = node.y_scale * mag
            coords.append(Vector((x, y, 0.0)))

        if len(coords) < 2:
            self.report({'WARNING'}, "Need at least two valid points to draw a curve")
            return {'CANCELLED'}

        # -------------------------------------------------------------------
        # Create or update the curve object
        # -------------------------------------------------------------------
        scene = context.scene
        curve_name = "FrequencyResponse"
        # Remove existing object with the same name if present (optional)
        if curve_name in bpy.data.objects:
            old_obj = bpy.data.objects[curve_name]
            bpy.data.objects.remove(old_obj, do_unlink=True)

        # Create new curve data
        curve_data = bpy.data.curves.new(name=curve_name, type='CURVE')
        curve_data.dimensions = '3D'

        # Add a spline and set its points
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(coords) - 1)
        for i, v in enumerate(coords):
            # Curve points use 4D coordinates (x, y, z, weight)
            spline.points[i].co = (v.x, v.y, v.z, 1.0)

        # Create object and link to collection
        curve_obj = bpy.data.objects.new(curve_name, curve_data)
        context.collection.objects.link(curve_obj)

        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        curve_obj.select_set(True)
        context.view_layer.objects.active = curve_obj

        self.report({'INFO'}, f"Curve '{curve_name}' created/updated")
        return {'FINISHED'}

# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------
classes = [
    AcousticFreqPoint,
    AcousticMaterialNodeTree,
    AcousticFreqResponseNode,
    ACOUSTIC_OT_point_add,
    ACOUSTIC_OT_point_remove,
    ACOUSTIC_OT_generate_curve,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    print("AcousticMaterialNodeTree with Frequency Response Shape node registered.")
