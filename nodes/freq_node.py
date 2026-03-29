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
import gpu
import blf
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy.types import Node, NodeTree
from bpy.props import FloatProperty, IntProperty, EnumProperty, FloatVectorProperty, BoolProperty
from bpy_extras import view3d_utils

from .baseND import AcousticMaterialNode

# Custom property group for curve points
class FrequencyResponsePoint(bpy.types.PropertyGroup):
    location: FloatVectorProperty(
        name="Location",
        size=2,
        default=(0.0, 0.0),
        min=-1.0,
        max=1.0
    )
    handle_left: FloatVectorProperty(
        name="Left Handle",
        size=2,
        default=(-0.1, 0.0)
    )
    handle_right: FloatVectorProperty(
        name="Right Handle",
        size=2,
        default=(0.1, 0.0)
    )
    handle_type: EnumProperty(
        name="Handle Type",
        items=[
            ('AUTO', "Auto", "Automatic handle"),
            ('VECTOR', "Vector", "Vector handle"),
            ('ALIGNED', "Aligned", "Aligned handle"),
            ('FREE', "Free", "Free handle")
        ],
        default='AUTO'
    )

# The main node class
class AcousticFrequencyResponseNode(AcousticMaterialNode):
    """Node for drawing 2D frequency response curves"""
    bl_idname = 'AcousticFrequencyResponseNode'
    bl_label = 'Frequency Response Curve'
    bl_icon = 'IPO_BEZIER'
    
    # Properties
    frequency_min: FloatProperty(
        name="Min Frequency",
        description="Minimum frequency in Hz",
        default=20.0,
        min=0.1,
        max=20000.0,
        soft_min=20.0,
        soft_max=20000.0
    )
    
    frequency_max: FloatProperty(
        name="Max Frequency",
        description="Maximum frequency in Hz",
        default=20000.0,
        min=0.1,
        max=200000.0,
        soft_min=20.0,
        soft_max=20000.0
    )
    
    amplitude_min: FloatProperty(
        name="Min Amplitude",
        description="Minimum amplitude in dB",
        default=-60.0,
        min=-120.0,
        max=60.0
    )
    
    amplitude_max: FloatProperty(
        name="Max Amplitude",
        description="Maximum amplitude in dB",
        default=20.0,
        min=-120.0,
        max=60.0
    )
    
    resolution: IntProperty(
        name="Resolution",
        description="Number of samples for evaluation",
        default=256,
        min=16,
        max=2048
    )
    
    show_grid: BoolProperty(
        name="Show Grid",
        description="Display grid in the node",
        default=True
    )
    
    show_handles: BoolProperty(
        name="Show Handles",
        description="Display curve handles",
        default=True
    )
    
    curve_width: FloatProperty(
        name="Curve Width",
        description="Width of the drawn curve",
        default=2.0,
        min=1.0,
        max=5.0
    )
    
    grid_color: FloatVectorProperty(
        name="Grid Color",
        description="Color of the grid lines",
        size=4,
        default=(0.3, 0.3, 0.3, 0.5),
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )
    
    curve_color: FloatVectorProperty(
        name="Curve Color",
        description="Color of the curve",
        size=4,
        default=(0.8, 0.2, 0.2, 1.0),
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )
    
    point_color: FloatVectorProperty(
        name="Point Color",
        description="Color of the control points",
        size=4,
        default=(0.2, 0.6, 0.9, 1.0),
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )
    
    # Collection of points
    points: bpy.props.CollectionProperty(type=FrequencyResponsePoint)
    active_point_index: bpy.props.IntProperty(default=0)
    
    # Drawing state
    is_dragging: BoolProperty(default=False)
    drag_point_index: bpy.props.IntProperty(default=-1)
    drag_handle: bpy.props.EnumProperty(
        items=[
            ('POINT', "Point", "Dragging point"),
            ('LEFT', "Left Handle", "Dragging left handle"),
            ('RIGHT', "Right Handle", "Dragging right handle")
        ]
    )
    
    def init(self, context):
        """Initialize the node with default sockets"""
        # Input sockets
        self.inputs.new('NodeSocketFloat', "Frequency").default_value = 1000.0
        self.inputs.new('NodeSocketFloat', "Amplitude Scale").default_value = 1.0
        
        # Output sockets
        self.outputs.new('NodeSocketFloat', "Amplitude")
        self.outputs.new('NodeSocketFloat', "Phase")
        
        # Add default points if empty
        if len(self.points) == 0:
            self.add_default_points()
    
    def add_default_points(self):
        """Add default curve points"""
        default_points = [
            ((0.0, -1.0), 'AUTO'),
            ((0.2, -0.33), 'AUTO'),
            ((0.5, 0.0), 'AUTO'),
            ((0.8, -0.17), 'AUTO'),
            ((1.0, -0.67), 'AUTO')
        ]
        
        for loc, handle_type in default_points:
            point = self.points.add()
            point.location = loc
            point.handle_type = handle_type
            self.update_handles(point)
    
    def update_handles(self, point):
        """Update handle positions based on handle type"""
        if point.handle_type == 'AUTO':
            # Simple auto handles
            point.handle_left = (point.location[0] - 0.05, point.location[1])
            point.handle_right = (point.location[0] + 0.05, point.location[1])
        elif point.handle_type == 'VECTOR':
            # Vector handles (aligned with axes)
            point.handle_left = (point.location[0] - 0.05, point.location[1])
            point.handle_right = (point.location[0] + 0.05, point.location[1])
    
    def draw_buttons(self, context, layout):
        """Draw node UI"""
        # Curve properties
        col = layout.column(align=True)
        col.prop(self, "frequency_min")
        col.prop(self, "frequency_max")
        col.prop(self, "amplitude_min")
        col.prop(self, "amplitude_max")
        col.prop(self, "resolution")
        
        # Display options
        row = layout.row()
        row.prop(self, "show_grid", toggle=True)
        row.prop(self, "show_handles", toggle=True)
        
        # Visual settings
        box = layout.box()
        box.label(text="Visual Settings")
        box.prop(self, "curve_width")
        box.prop(self, "grid_color")
        box.prop(self, "curve_color")
        box.prop(self, "point_color")
        
        # Point management
        box = layout.box()
        box.label(text="Curve Points")
        
        if len(self.points) > 0:
            row = box.row()
            row.template_list(
                "UI_UL_list", 
                "frequency_points", 
                self, 
                "points", 
                self, 
                "active_point_index",
                rows=3
            )
            
            col = row.column(align=True)
            col.operator("acoustic.add_point", text="", icon='ADD')
            col.operator("acoustic.remove_point", text="", icon='REMOVE')
            
            # Active point properties
            if 0 <= self.active_point_index < len(self.points):
                point = self.points[self.active_point_index]
                box.prop(point, "location", text="Location")
                box.prop(point, "handle_type", text="Handle Type")
                if point.handle_type == 'FREE':
                    box.prop(point, "handle_left", text="Left Handle")
                    box.prop(point, "handle_right", text="Right Handle")
        
        # Add/Remove buttons
        row = layout.row(align=True)
        row.operator("acoustic.add_point", text="Add Point")
        row.operator("acoustic.remove_point", text="Remove Point")
    
    def draw_buttons_ext(self, context, layout):
        """Draw extended UI in sidebar"""
        self.draw_buttons(context, layout)
        
        # Additional controls
        box = layout.box()
        box.label(text="Advanced")
        box.operator("acoustic.reset_curve", text="Reset Curve")
        box.operator("acoustic.normalize_curve", text="Normalize Curve")
    
    def draw_label(self):
        """Custom node label"""
        return "Frequency Response"
    
    # Bezier curve calculation
    def bezier_point(self, p0, p1, p2, p3, t):
        """Calculate point on cubic bezier curve"""
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t
        
        point = (uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0],
                 uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1])
        return point
    
    def evaluate_bezier_segment(self, p0, p1, p2, p3, num_segments=20):
        """Evaluate bezier segment and return list of points"""
        points = []
        for i in range(num_segments + 1):
            t = i / num_segments
            points.append(self.bezier_point(p0, p1, p2, p3, t))
        return points
    
    def get_curve_points(self):
        """GetGet all points along the curve for drawing"""
        if len(self.points) < 2:
            return []
        
        all_points = []
        
        for i in range(len(self.points) - 1):
            p0 = self.points[i].location
            p3 = self.points[i + 1].location
            
            # Control points
            p1 = (p0[0] + self.points[i].handle_right[0], 
                  p0[1] + self.points[i].handle_right[1])
            p2 = (p3[0] + self.points[i + 1].handle_left[0], 
                  p3[1] + self.points[i + 1].handle_left[1])
            
            segment_points = self.evaluate_bezier_segment(p0, p1, p2, p3, 20)
            all_points.extend(segment_points)
        
        return all_points
    
    def evaluate_curve(self, frequency):
        """Evaluate the curve at a given frequency"""
        if len(self.points) < 2:
            return 0.0
        
        # Normalize frequency to 0-1 range (log scale)
        freq_norm = (math.log10(max(frequency, 0.1)) - math.log10(self.frequency_min)) / \
                   (math.log10(self.frequency_max) - math.log10(self.frequency_min))
        freq_norm = max(0.0, min(1.0, freq_norm))
        
        # Find segment containing the frequency
        for i in range(len(self.points) - 1):
            p0 = self.points[i].location
            p3 = self.points[i + 1].location
            
            if p0[0] <= freq_norm <= p3[0]:
                # Bezier evaluation
                p1 = (p0[0] + self.points[i].handle_right[0], 
                      p0[1] + self.points[i].handle_right[1])
                p2 = (p3[0] + self.points[i + 1].handle_left[0], 
                      p3[1] + self.points[i + 1].handle_left[1])
                
                # Binary search for t value that gives desired x
                t_min, t_max = 0.0, 1.0
                for _ in range(10):  # 10 iterations gives good precision
                    t = (t_min + t_max) / 2
                    point = self.bezier_point(p0, p1, p2, p3, t)
                    if point[0] < freq_norm:
                        t_min = t
                    else:
                        t_max = t
                
                t = (t_min + t_max) / 2
                point = self.bezier_point(p0, p1, p2, p3, t)
                amplitude_norm = point[1]
                
                # Convert from normalized to actual amplitude
                amplitude_actual = self.amplitude_min + \
                                  (amplitude_norm + 1.0) * 0.5 * (self.amplitude_max - self.amplitude_min)
                return amplitude_actual
        
        return 0.0
    
    def process(self):
        """Process the node"""
        if not self.outputs[0].is_linked:
            return
        
        # Get input values
        frequency = self.inputs[0].default_value
        scale = self.inputs[1].default_value if len(self.inputs) > 1 else 1.0
        
        # Evaluate curve
        amplitude = self.evaluate_curve(frequency) * scale
        
        # Set output
        self.outputs[0].default_value = amplitude
        
        # Simple phase calculation (can be extended)
        phase = 0.0
        if len(self.outputs) > 1:
            self.outputs[1].default_value = phase
    
    # Drawing methods
    def get_draw_region(self):
        """Get the drawing region coordinates within the node"""
        # This is a simplified version - in reality you'd need to
        # calculate based on node dimensions and UI layout
        return {
            'x': 10,
            'y': 100,
            'width': 300,
            'height': 200
        }
    
    def screen_to_curve_space(self, screen_pos, region):
        """Convert screen coordinates to curve space (0-1)"""
        curve_x = (screen_pos[0] - region['x']) / region['width']
        curve_y = 1.0 - (screen_pos[1] - region['y']) / region['height']
        return (max(0.0, min(1.0, curve_x)), max(0.0, min(1.0, curve_y)))
    
    def curve_to_screen_space(self, curve_pos, region):
        """Convert curve space coordinates to screen space"""
        screen_x = region['x'] + curve_pos[0] * region['width']
        screen_y = region['y'] + (1.0 - curve_pos[1]) * region['height']
        return (screen_x, screen_y)
    
    def draw_curve(self, context):
        """Main drawing function called by Blender"""
        region = self.get_draw_region()
        
        # Setup shader
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width(self.curve_width)
        
        # Draw grid
        if self.show_grid:
            self.draw_grid(context, region, shader)
        
        # Draw curve
        curve_points = self.get_curve_points()
        if curve_points:
            self.draw_bezier_curve(curve_points, region, shader)
        
        # Draw control points and handles
        self.draw_control_points(region, shader)
        
        gpu.state.line_width(1.0)
        gpu.state.blend_set('NONE')
    
    def draw_grid(self, context, region, shader):
        """Draw grid lines"""
        # Vertical lines (frequency)
        for i in range(1, 10):
            x = region['x'] + (i / 10) * region['width']
            vertices = [(x, region['y']), (x, region['y'] + region['height'])]
            batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
            shader.bind()
            shader.uniform_float("color", self.grid_color)
            batch.draw(shader)
        
        # Horizontal lines (amplitude)
        for i in range(1, 10):
            y = region['y'] + (i / 10) * region['height']
            vertices = [(region['x'], y), (region['x'] + region['width'], y)]
            batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
            shader.bind()
            shader.uniform_float("color", self.grid_color)
            batch.draw(shader)
        
        # Border
        vertices = [
            (region['x'], region['y']),
            (region['x'] + region['width'], region['y']),
            (region['x'] + region['width'], region['y'] + region['height']),
            (region['x'], region['y'] + region['height']),
            (region['x'], region['y'])
        ]
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices})
        shader.bind()
        shader.uniform_float("color", (0.5, 0.5, 0.5, 1.0))
        batch.draw(shader)
    
    def draw_bezier_curve(self, curve_points, region, shader):
        """Draw the bezier curve"""
        screen_points = [self.curve_to_screen_space(p, region) for p in curve_points]
        
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": screen_points})
        shader.bind()
        shader.uniform_float("color", self.curve_color)
        batch.draw(shader)
    
    def draw_control_points(self, region, shader):
        """Draw control points and handles"""
        point_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        
        for i, point in enumerate(self.points):
            # Draw point
            screen_pos = self.curve_to_screen_space(point.location, region)
            self.draw_circle(screen_pos, 6, point_shader, 
                           (1.0, 1.0, 1.0, 1.0) if i == self.active_point_index else self.point_color)
            
            # Draw handles
            if self.show_handles and point.handle_type in ['FREE', 'ALIGNED']:
                left_handle = (point.location[0] + point.handle_left[0],
                              point.location[1] + point.handle_left[1])
                right_handle = (point.location[0] + point.handle_right[0],
                               point.location[1] + point.handle_right[1])
                
                left_screen = self.curve_to_screen_space(left_handle, region)
                right_screen = self.curve_to_screen_space(right_handle, region)
                
                # Handle lines
                vertices = [screen_pos, left_screen]
                batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
                shader.bind()
                shader.uniform_float("color", (0.7, 0.7, 0.7, 0.5))
                batch.draw(shader)
                
                vertices = [screen_pos, right_screen]
                batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
                batch.draw(shader)
                
                # Handle points
                self.draw_circle(left_screen, 4, point_shader, (0.8, 0.8, 0.2, 1.0))
                self.draw_circle(right_screen, 4, point_shader, (0.8, 0.8, 0.2, 1.0))
    
    def draw_circle(self, center, radius, shader, color):
        """Draw a circle at the given position"""
        vertices = []
        for i in range(32):
            angle = (i / 32) * 2 * math.pi
            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius
            vertices.append((x, y))
        
        batch = batch_for_shader(shader, 'LINE_LOOP', {"pos": vertices})
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
    
    # Mouse interaction
    def invoke(self, context, event):
        """Handle mouse clicks"""
        region = self.get_draw_region()
        
        # Check if click is in drawing region
        if (region['x'] <= event.mouse_region_x <= region['x'] + region['width'] and
            region['y'] <= event.mouse_region_y <= region['y'] + region['height']):
            
            click_pos = (event.mouse_region_x, event.mouse_region_y)
            curve_pos = self.screen_to_curve_space(click_pos, region)
            
            # Check if clicking on a point or handle
            for i, point in enumerate(self.points):
                point_screen = self.curve_to_screen_space(point.location, region)
                dist = math.hypot(point_screen[0] - click_pos[0], 
                                 point_screen[1] - click_pos[1])
                
                if dist < 10:  # Clicked on point
                    self.active_point_index = i
                    self.is_dragging = True
                    self.drag_point_index = i
                    self.drag_handle = 'POINT'
                    return {'RUNNING_MODAL'}
                
                # Check handles
                if self.show_handles:
                    left_handle = (point.location[0] + point.handle_left[0],
                                  point.location[1] + point.handle_left[1])
                    right_handle = (point.location[0] + point.handle_right[0],
                                   point.location[1] + point.handle_right[1])
                    
                    left_screen = self.curve_to_screen_space(left_handle, region)
                    right_screen = self.curve_to_screen_space(right_handle, region)
                    
                    if math.hypot(left_screen[0] - click_pos[0], 
                                 left_screen[1] - click_pos[1]) < 8:
                        self.active_point_index = i
                        self.is_dragging = True
                        self.drag_point_index = i
                        self.drag_handle = 'LEFT'
                        return {'RUNNING_MODAL'}
                    
                    if math.hypot(right_screen[0] - click_pos[0], 
                                 right_screen[1] - click_pos[1]) < 8:
                        self.active_point_index = i
                        self.is_dragging = True
                        self.drag_point_index = i
                        self.drag_handle = 'RIGHT'
                        return {'RUNNING_MODAL'}
            
            # If no point clicked, add new point
            self.add_point_at_location(curve_pos)
            return {'RUNNING_MODAL'}
        
        return {'PASS_THROUGH'}
    
    def modal(self, context, event, tweak):
        """Handle mouse drag"""
        if not self.is_dragging:
            return {'PASS_THROUGH'}
        
        if event.type == 'MOUSEMOVE':
            region = self.get_draw_region()
            curve_pos = self.screen_to_curve_space((event.mouse_region_x, event.mouse_region_y), region)
            
            if 0 <= self.drag_point_index < len(self.points):
                point = self.points[self.drag_point_index]
                
                if self.drag_handle == 'POINT':
                    point.location = curve_pos
                    self.update_handles(point)
                elif self.drag_handle == 'LEFT':
                    point.handle_left = (curve_pos[0] - point.location[0],
                                        curve_pos[1] - point.location[1])
                elif self.drag_handle == 'RIGHT':
                    point.handle_right = (curve_pos[0] - point.location[0],
                                         curve_pos[1] - point.location[1])
            
            # Redraw
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        
        elif event.type in {'LEFTMOUSE', 'ESC'}:
            self.is_dragging = False
            self.drag_point_index = -1
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
    
    def add_point_at_location(self, curve_pos):
        """Add a new point at the specified curve location"""
        # Find where to insert the point
        insert_index = 0
        for i, point in enumerate(self.points):
            if curve_pos[0] < point.location[0]:
                insert_index = i
                break
            insert_index = i + 1
        
        # Add new point
        new_point = self.points.add()
        new_point.location = curve_pos
        new_point.handle_type = = 'AUTO'
        self.update_handles(new_point)
        
        # Move to correct position
        self.points.move(len(self.points) - 1, insert_index)
        self.active_point_index = insert_index

# Operators for point management
class AddFrequencyPoint(bpy.types.Operator):
    """Add a new point to the frequency response curve"""
    bl_idname = "acoustic.add_point"
    bl_label = "Add Point"
    
    @classmethod
    def poll(cls, context):
        return context.active_node and context.active_node.bl_idname == 'AcousticFrequencyResponseNode'
    
    def execute(self, context):
        node = context.active_node
        
        # Add new point at the middle of existing points or at (0.5, 0.0)
        if len(node.points) > 0:
            last_point = node.points[-1]
            new_loc = (min(last_point.location[0] + 0.1, 1.0), 0.0)
        else:
            new_loc = (0.5, 0.0)
        
        point = node.points.add()
        point.location = new_loc
        point.handle_type = 'AUTO'
        node.update_handles(point)
        
        node.active_point_index = len(node.points) - 1
        return {'FINISHED'}

class RemoveFrequencyPoint(bpy.types.Operator):
    """Remove the active point from the frequency response curve"""
    bl_idname = "acoustic.remove_point"
    bl_label = "Remove Point"
    
    @classmethod
    def poll(cls, context):
        node = context.active_node
        return node and node.bl_idname == 'AcousticFrequencyResponseNode' and len(node.points) > 0
    
    def execute(self, context):
        node = context.active_node
        
        if 0 <= node.active_point_index < len(node.points):
            node.points.remove(node.active_point_index)
            node.active_point_index = max(0, node.active_point_index - 1)
        
        return {'FINISHED'}

class ResetFrequencyCurve(bpy.types.Operator):
    """Reset the frequency response curve to default"""
    bl_idname = "acoustic.reset_curve"
    bl_label = "Reset Curve"
    
    @classmethod
    def poll(cls, context):
        return context.active_node and context.active_node.bl_idname == 'AcousticFrequencyResponseNode'
    
    def execute(self, context):
        node = context.active_node
        
        # Clear existing points
        node.points.clear()
        
        # Add default points
        node.add_default_points()
        
        return {'FINISHED'}

class NormalizeFrequencyCurve(bpy.types.Operator):
    """Normalize the curve to fit within amplitude range"""
    bl_idname = "acoustic.normalize_curve"
    bl_label = "Normalize Curve"
    
    @classmethod
    def poll(cls, context):
        return context.active_node and context.active_node.bl_idname == 'AcousticFrequencyResponseNode'
    
    def execute(self, context):
        node = context.active_node
        
        if len(node.points) < 2:
            return {'CANCELLED'}
        
        # Find min and max y values
        y_values = [p.location[1] for p in node.points]
        y_min = min(y_values)
        y_max = max(y_values)
        
        if y_max == y_min:
            return {'CANCELLED'}
        
        # Normalize all points to -1 to 1 range
        for point in node.points:
            normalized_y = -1.0 + 2.0 * ((point.location[1] - y_min) / (y_max - y_min))
            point.location = (point.location[0],], normalized_y)
            node.update_handles(point)
        
        return {'FINISHED'}

# Node drawing handler
def draw_frequency_response_node(self, context):
    """Custom draw function for the node"""
    layout = self.layout
    
    # Draw the curve area
    row = layout.row()
    row.label(text="Frequency Response Curve")
    
    # Create a custom UI element for drawing
    row = layout.row()
    row.scale_y = 2.0
    
    # This creates an empty space where we'll draw
    # The actual drawing happens in the node's draw_curve method
    row.label(text="")  # Empty label to create space
    
    # Add frequency labels
    row = layout.row()
    col = row.column()
    col.label(text=f"{self.frequency_min:.0f}Hz")
    col = row.column()
    col.alignment = 'CENTER'
    col.label(text="Frequency (log)")
    col = row.column()
    col.alignment = 'RIGHT'
    col.label(text=f"{self.frequency_max:.0f}Hz")
    
    # Add amplitude labels
    row = layout.row()
    col = row.column()
    col.label(text=f"{self.amplitude_max:.0f}dB")
    col = row.column()
    col.alignment = 'CENTER'
    col.label(text="Amplitude")
    col = row.column()
    col.alignment = 'RIGHT'
    col.label(text=f"{self.amplitude_min:.0f}dB")

# Handler to draw all frequency response nodes
@bpy.app.handlers.persistent
def draw_frequency_response_nodes():
    """Draw all frequency response nodes in the node editor"""
    context = bpy.context
    
    if not (context.area and context.area.type == 'NODE_EDITOR'):
        return
    
    for region in context.area.regions:
        if region.type == 'WINDOW':
            # # Set up OpenGL for 2D drawing
            gpu.state.blend_set('ALPHA')
            
            # Find and draw all frequency response nodes
            for node_tree in bpy.data.node_groups:
                if node_tree.bl_idname == 'AcousticMaterialNodeTree':
                    for node in node_tree.nodes:
                        if node.bl_idname == 'AcousticFrequencyResponseNode':
                            # Temporarily set context
                            old_region = context.region
                            context.region = region
                            
                            # Draw the node
                            node.draw_curve(context)
                            
                            # Restore context
                            context.region = old_region
            
            gpu.state.blend_set('NONE')

# Registration
classes = [
    FrequencyResponsePoint,
    AcousticFrequencyResponseNode,
    AddFrequencyPoint,
    RemoveFrequencyPoint,
    ResetFrequencyCurve,
    NormalizeFrequencyCurve
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add draw handler to the node
    AcousticFrequencyResponseNode.draw = draw_frequency_response_node
    
    # Add handler for drawing nodes
    if draw_frequency_response_nodes not in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.append(draw_frequency_response_nodes)

def unregister():
    # Remove handler
    if draw_frequency_response_nodes in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(draw_frequency_response_nodes)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# For testing
if __name__ == "__main__":
    register()
