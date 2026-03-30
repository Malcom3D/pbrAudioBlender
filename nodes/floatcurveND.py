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
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from math import floor, ceil
import numpy as np

from bpy.props import StringProperty, PointerProperty
from bpy.types import Operator

from .baseND import AcousticMaterialNode

# ------------------------------------------------------------
# FloatCurve Data Structure
# ------------------------------------------------------------
class FloatCurvePoint:
    """Represents a point on the curve"""
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.selected = False
    
    def copy(self):
        return FloatCurvePoint(self.x, self.y)

class FloatCurve:
    """Main curve data structure"""
    def __init__(self):
        self.points = [
            FloatCurvePoint(0.0, 0.0),
            FloatCurvePoint(1.0, 1.0)
        ]
        self.selected_point = None
        self.clamp_x = (0.0, 1.0)
        self.clamp_y = (0.0, 1.0)
    
    def add_point(self, x, y):
        """Add a new point to the curve"""
        point = FloatCurvePoint(x, y)
        self.points.append(point)
        self.sort_points()
        return point
    
    def remove_point(self, point):
        """Remove a point from the curve"""
        if point in self.points and len(self.points) > 2:
            self.points.remove(point)
            if self.selected_point == point:
                self.selected_point = None
    
    def sort_points(self):
        """Sort points by x coordinate"""
        self.points.sort(key=lambda p: p.x)
    
    def evaluate(self, x):
        """Evaluate curve at position x using linear interpolation"""
        if not self.points:
            return 0.0
        
        # Clamp x to curve bounds
        x = max(self.clamp_x[0], min(self.clamp_x[1], x))
        
        # Find surrounding points
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            if p1.x <= x <= p2.x:
                if p1.x == p2.x:
                    return p1.y
                
                # Linear interpolation
                t = (x - p1.x) / (p2.x - p1.x)
                return p1.y + (p2.y - p1.y) * t
        
        # If x is outside bounds, return first or last point
        if x <= self.points[0].x:
            return self.points[0].y
        else:
            return self.points[-1].y
    
    def get_bounds(self):
        """Get bounding box of all points"""
        if not self.points:
            return (0, 0, 1, 1)
        
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))

# ------------------------------------------------------------
# Custom UI Drawing
# ------------------------------------------------------------
class FloatCurveUI:
    """Handles drawing and interaction with the curve"""
    
    def __init__(self, region_width, region_height, padding=20):
        self.region_width = region_width
        self.region_height = region_height
        self.padding = padding
        
        # View transform
        self.view_x = 0.0
        self.view_y = 0.0
        self.view_scale = 1.0
        
        # Interaction state
        self.dragging = False
        self.drag_start = None
        self.hover_point = None
        
        # Colors
        self.colors = {
            'grid': (0.3, 0.3, 0.3, 0.5),
            'axis': (0.8, 0.8, 0.8, 1.0),
            'curve': (0.0, 0.6, 1.0, 1.0),
            'point': (1.0, 1.0, 1.0, 1.0),
            'point_selected': (1.0, 0.5, 0.0, 1.0),
            'point_hover': (1.0, 0.8, 0.0, 1.0),
            'background': (0.1, 0.1, 0.1, 0.8),
            'text': (0.9, 0.9, 0.9, 1.0)
        }
    
    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (x - self.view_x) * self.view_scale + self.padding
        screen_y = (y - self.view_y) * self.view_scale + self.padding
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.padding) / self.view_scale + self.view_x
        world_y = (screen_y - self.padding) / self.view_scale + self.view_y
        return world_x, world_y
    
    def draw_grid(self, curve):
        """Draw grid and axes"""
        # Get visible bounds
        visible_min_x, visible_min_y = self.screen_to_world(0, 0)
        visible_max_x, visible_max_y = self.screen_to_world(
            self.region_width - 2 * self.padding,
            self.region_height - 2 * self.padding
        )
        
        # Draw background
        vertices = [
            (self.padding, self.padding),
            (self.region_width - self.padding, self.padding),
            (self.region_width - self.padding, self.region_height - self.padding),
            (self.padding, self.region_height - self.padding)
        ]
        
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})
        shader.bind()
        shader.uniform_float("color", self.colors['background'])
        batch.draw(shader)
        
        # Draw grid lines
        grid_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        
        # Calculate grid spacing
        grid_size = 0.1 * self.view_scale
        if grid_size < 0.01:
            grid_size = 0.01
        elif grid_size > 0.5:
            grid_size = 0.5
        
        # Vertical grid lines
        start_x = ceil(visible_min_x / grid_size) * grid_size
        for x in np.arange(start_x, visible_max_x, grid_size):
            sx1, sy1 = self.world_to_screen(x, visible_min_y)
            sx2, sy2 = self.world_to_screen(x, visible_max_y)
            
            vertices = [(sx1, sy1), (sx2, sy2)]
            batch = batch_for_shader(grid_shader, 'LINES', {"pos": vertices})
            grid_shader.bind()
            grid_shader.uniform_float("color", self.colors['grid'])
            batch.draw(grid_shader)
        
        # Horizontal grid lines
        start_y = ceil(visible_min_y / grid_size) * grid_size
        for y in np.arange(start_y, visible_max_y, grid_size):
            sx1, sy1 = self.world_to_screen(visible_min_x, y)
            sx2, sy2 = self.world_to_screen(visible_max_x, y)
            
            vertices = [(sx1, sy1), (sx2, sy2)]
            batch = batch_for_shader(grid_shader, 'LINES', {"pos": vertices})
            grid_shader.bind()
            grid_shader.uniform_float("color", self.colors['grid'])
            batch.draw(grid_shader)
        
        # Draw axes
        # X axis
        if visible_min_y <= 0 <= visible_max_y:
            sx1, sy1 = self.world_to_screen(visible_min_x, 0)
            sx2, sy2 = self.world_to_screen(visible_max_x, 0)
            vertices = [(sx1, sy1), (sx2, sy2)]
            batch = batch_for_shader(grid_shader, 'LINES', {"pos": vertices})
            grid_shader.uniform_float("color", self.colors['axis'])
            batch.draw(grid_shader)
        
        # Y axis
        if visible_min_x <= 0 <= visible_max_x:
            sx1, sy1 = self.world_to_screen(0, visible_min_y)
            sx2, sy2 = self.world_to_screen(0, visible_max_y)
            vertices = [(sx1, sy1), (sx2, sy2)]
            batch = batch_for_shader(grid_shader, 'LINES', {"pos": vertices})
            grid_shader.uniform_float("color", self.colors['axis'])
            batch.draw(grid_shader)
    
    def draw_curve(self, curve):
        """Draw the curve line"""
        if len(curve.points) < 2:
            return
        
        # Create vertices for curve
        vertices = []
        for i in range(len(curve.points) - 1):
            p1 = curve.points[i]
            p2 = curve.points[i + 1]
            
            # Add some intermediate points for smoother appearance
            steps = max(2, int(abs(p2.x - p1.x) * 100))
            for j in range(steps):
                t = j / (steps - 1) if steps > 1 else 0
                x = p1.x + (p2.x - p1.x) * t
                y = curve.evaluate(x)
                sx, sy = self.world_to_screen(x, y)
                vertices.append((sx, sy))
        
        if vertices:
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
            shader.bind()
            shader.uniform_float("color", self.colors['curve'])
            bgl.glLineWidth(2.0)
            batch.draw(shader)
            bgl.glLineWidth(1.0)
    
    def draw_points(self, curve):
        """Draw curve points"""
        point_radius = 5.0
        
        for point in curve.points:
            sx, sy = self.world_to_screen(point.x, point.y)
            
            # Determine point color
            if point == curve.selected_point:
                color = self.colors['point_selected']
            elif point == self.hover_point:
                color = self.colors['point_hover']
            else:
                color = self.colors['point']
            
            # Draw point as a circle
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            
            # Create circle vertices
            vertices = []
            segments = 16
            for i in range(segments):
                angle = (i / segments) * 2 * 3.14159
                vx = sx + point_radius * np.cos(angle)
                vy = sy + point_radius * np.sin(angle)
                vertices.append((vx, vy))
            
            batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)
    
    def draw_info(self, curve, mouse_pos):
        """Draw coordinate info"""
        if mouse_pos:
            world_x, world_y = self.screen_to_world(mouse_pos[0], mouse_pos[1])
            value = curve.evaluate(world_x)
            
            # Draw text
            font_id = 0
            blf.size(font_id, 11, 72)
            blf.color(font_id, *self.colors['text'])
            
            info = f"X: {world_x:.3f}, Y: {value:.3f}"
            blf.position(font_id, 10, self.region_height - 25, 0)
            blf.draw(font_id, info)
    
    def find_point_at(self, curve, screen_x, screen_y, radius=10):
        """Find point near screen coordinates"""
        for point in curve.points:
            px, py = self.world_to_screen(point.x, point.y)
            distance = ((px - screen_x) ** 2 + (py - screen_y) ** 2) ** 0.5
            if distance < radius:
                return point
        return None
    
    def handle_event(self, event, curve, context):
        """Handle mouse events"""
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # Find if we clicked on a point
                clicked_point = self.find_point_at(curve, event.mouse_region_x, event.mouse_region_y)
                
                if clicked_point:
                    # Select and start dragging point
                    curve.selected_point = clicked_point
                    self.dragging = True
                    self.drag_start = (event.mouse_region_x, event.mouse_region_y)
                    return {'RUNNING_MODAL'}
                else:
                    # Add new point
                    world_x, world_y = self.screen_to_world(
                        event.mouse_region_x,
                        event.mouse_region_y
                    )
                    new_point = curve.add_point(world_x, world_y)
                    curve.selected_point = new_point
                    self.dragging = True
                    self.drag_start = (event.mouse_region_x, event.mouse_region_y)
                    return {'RUNNING_MODAL'}
            
            elif event.value == 'RELEASE':
                self.dragging = False
                return {'RUNNING_MODAL'}
        
        elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            # Remove point on right click
            clicked_point = self.find_point_at(curve, event.mouse_region_x, event.mouse_region_y)
            if clicked_point and len(curve.points) > 2:
                curve.remove_point(clicked_point)
                return {'RUNNING_MODAL'}
        
        elif event.type == 'MOUSEMOVE':
            # Update hover point
            self.hover_point = self.find_point_at(curve, event.mouse_region_x, event.mouse_region_y)
            
            # Handle dragging
            if self.dragging and curve.selected_point:
                world_x, world_y = self.screen_to_world(
                    event.mouse_region_x,
                    event.mouse_region_y
                )
                
                # Clamp to bounds
                world_x = max(curve.clamp_x[0], min(curve.clamp_x[1], world_x))
                world_y = max(curve.clamp_y[0], min(curve.clamp_y[1], world_y))
                
                # Update point position
                curve.selected_point.x = world_x
                curve.selected_point.y = world_y
                curve.sort_points()
                
                return {'RUNNING_MODAL'}
        
        elif event.type == 'WHEELUPMOUSE':
            # Zoom in
            self.view_scale *= 1.1
            return {'RUNNING_MODAL'}
        
        elif event.type == 'WHEELDOWNMOUSE':
            # Zoom out
            self.view_scale /= 1.1
            return {'RUNNING_MODAL'}
        
        elif event.type == 'MIDDLEMOUSE':
            if event.value == 'PRESS':
                # Start panning
                self.dragging = True
                self.drag_start = (event.mouse_region_x, event.mouse_region_y)
                return {'RUNNING_MODAL'}
            elif event.value == 'RELEASE':
                self.dragging = False
                return {'RUNNING_MODAL'}
        
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            # Cancel
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}

# ------------------------------------------------------------
# Node Implementation
# ------------------------------------------------------------
class FloatCurveNode(AcousticMaterialNode):
    """Custom Float Curve Node"""
    bl_idname = 'CustomFloatCurveNode'
    bl_label = 'Float Curve'
    bl_icon = 'GRAPH'
    
    # Properties
    curve_data: StringProperty(
        name="Curve Data",
        default=""
    )
    
    def init(self, context):
        """Initialize the node"""
        self.inputs.new('NodeSocketFloat', 'Input')
        self.outputs.new('NodeSocketFloat', 'Output')
        
        # Initialize curve
        self.curve = FloatCurve()
    
    def draw_buttons(self, context, layout):
        """Draw node buttons"""
        row = layout.row()
        op = row.operator("node.float_curve_editor", text="Edit Curve")
        op.curve = self.curve
        op.node_name = self.name
        op.tree_name = self.id_data.name
        
        # Display current value if connected
        if self.inputs[0].is_linked:
            input_value = self.inputs[0].default_value
            output_value = self.curve.evaluate(input_value)
            row = layout.row()
            row.label(text=f"Input: {input_value:.3f} → Output: {output_value:.3f}")
    
    def draw_buttons_ext(self, context, layout):
        """Draw additional buttons in sidebar"""
        layout.prop(self, "curve_data")
        
        # Curve operations
        row = layout.row()
        op = row.operator("node.float_curve_reset", text="Reset")
        op.node_name = self.name
        op.tree_name = self.id_data.name
    
    def free(self):
        """Clean up when node is removed"""
        self.curve = None
    
    def copy(self, node):
        """Copy curve data when node is duplicated"""
        self.curve = FloatCurve()
        # Copy points from original node
        for point in node.curve.points:
            self.curve.points.append(point.copy())
    
    def update(self):
        """Update node output"""
        if self.inputs[0].is_linked:
            input_value = self.inputs[0].default_value
            output_value = self.curve.evaluate(input_value)
            self.outputs[0].default_value = output_value

# ------------------------------------------------------------
# Operators
# ------------------------------------------------------------
class NODE_OT_float_curve_editor(Operator):
    """Open Float Curve Editor"""
    bl_idname = "node.float_curve_editor"
    bl_label = "Float Curve Editor"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties
    curve: PointerProperty(type=FloatCurve)
    node_name: StringProperty()
    tree_name: StringProperty()
    
    def invoke(self, context, event):
        # Find the node
        node_tree = bpy.data.node_groups.get(self.tree_name)
        if not node_tree:
            self.report({'ERROR'}, "Node tree not found")
            return {'CANCELLED'}
    
        node = node_tree.nodes.get(self.node_name)
        if not node or not isinstance(node, FloatCurveNode):
            self.report({'ERROR'}, "FloatCurve node not found")
            return {'CANCELLED'}
        
        # Store reference to node
        self.node = node
        
        # Create UI handler
        self.ui = FloatCurveUI(
            context.region.width,
            context.region.height
        )
        
        # Set up modal handler
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        # Handle events
        result = self.ui.handle_event(event, self.node.curve, context)
        
        if result == {'RUNNING_MODAL'}:
            # Redraw
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        elif result == {'CANCELLED'}:
            return {'CANCELLED'}
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        return {'FINISHED'}

class NODE_OT_float_curve_reset(Operator):
    """Reset Curve to Default"""
    bl_idname = "node.float_curve_reset"
    bl_label = "Reset Curve"
    
    node_name: StringProperty()
    tree_name: StringProperty()
    
    def execute(self, context):
        node_tree = bpy.data.node_groups.get(self.tree_name)
        if node_tree:
            node = node_tree.nodes.get(self.node_name)
            if node and isinstance(node, FloatCurveNode):
                node.curve = FloatCurve()
                node.update()
        
        return {'FINISHED'}

# ------------------------------------------------------------
# Registration
# ------------------------------------------------------------
classes = [
    FloatCurveNode,
    NODE_OT_float_curve_editor,
    NODE_OT_float_curve_reset
]

#def register():
#    for cls in classes:
#        bpy.utils.register_class(cls)
#    
#    # Register node category
#    from nodeitems_utils import NodeCategory, register_node_categories, unregister_node_categories
#    from nodeitems_builtins import node_categories
#    
#    class CustomNodeCategory(NodeCategory):
#        @classmethod
#        def poll(cls, context):
#            return context.space_data.tree_type == 'ShaderNodeTree'
#    
#    node_categories.append(CustomNodeCategory(
#        "CUSTOM_NODES",
#        "Custom Nodes",
#        items=[(FloatCurveNode.bl_idname, FloatCurveNode.bl_label, "", FloatCurveNode.bl_icon)]
#    ))
#
#def unregister():
#    for cls in classes:
#        bpy.utils.unregister_class(cls)
#    
#    # Unregister node category
#    from nodeitems_utils import unregister_node_categories
#    unregister_node_categories("CUSTOM_NODES")
#
#if __name__ == "__main__":
#    register()
