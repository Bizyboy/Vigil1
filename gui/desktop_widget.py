"""
Vigil Desktop Widget - Flying Mascot
=====================================

A small, animated widget that flies around the screen representing Vigil.
Always on top, semi-transparent, and interactive.
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import math
import time
from typing import Optional, Callable


# Widget appearance constants
class WidgetConfig:
    """Configuration constants for the desktop widget."""
    WIDTH = 120
    HEIGHT = 120
    OPACITY_NORMAL = 0.9
    OPACITY_HOVER = 1.0
    
    # Colors
    BG_OUTER = '#1a1a2e'
    BG_INNER = '#16213e'
    CIRCLE_OUTER = '#0f3460'
    CIRCLE_INNER = '#533483'
    V_FILL = '#e94560'
    V_OUTLINE = '#ff6b9d'
    EYE_COLOR = '#00ffff'
    STATUS_COLOR_1 = '#00ff00'
    STATUS_COLOR_2 = '#00ffff'
    
    # Animation
    ANIMATION_SPEED = 0.05
    ANIMATION_FRAME_MS = 50
    EYE_PULSE_MULTIPLIER = 2
    IDLE_MOVEMENT_INTERVAL = 100  # frames
    IDLE_MOVEMENT_RANGE = 30  # pixels
    
    # Physics
    MOVEMENT_ACCELERATION = 0.001
    MOVEMENT_FRICTION = 0.95


class VigilDesktopWidget:
    """
    A desktop widget that represents Vigil as a small flying mascot.
    
    Features:
    - Floats around the screen with gentle movement
    - Always stays on top
    - Semi-transparent
    - Draggable
    - Click to open chat or settings
    - Animated idle behaviors
    """
    
    def __init__(
        self,
        on_click: Optional[Callable] = None,
        on_right_click: Optional[Callable] = None,
        parent: Optional[tk.Tk] = None,
    ):
        """Initialize the desktop widget."""
        self.on_click = on_click
        self.on_right_click = on_right_click
        
        # Create window - use Toplevel if parent provided, else Tk
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("Vigil")
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.attributes('-topmost', True)  # Always on top
        self.window.attributes('-alpha', WidgetConfig.OPACITY_NORMAL)  # Semi-transparent
        
        # Set window size
        self.width = WidgetConfig.WIDTH
        self.height = WidgetConfig.HEIGHT
        self.window.geometry(f'{self.width}x{self.height}')
        
        # Configure transparent background
        self.window.configure(bg=WidgetConfig.BG_OUTER)
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(
            self.window,
            width=self.width,
            height=self.height,
            bg='#1a1a2e',
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Movement state
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.target_x = 0
        self.target_y = 0
        self.current_x = 0
        self.current_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Animation state
        self.animation_phase = 0
        self.idle_animation_counter = 0
        
        # Canvas item references for efficient updates
        self.eye_item = None
        self.status_indicator_item = None
        
        # Draw Vigil mascot once
        self._draw_mascot_static()
        self._create_animated_elements()
        
        # Bind events
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.canvas.bind('<Button-3>', self._on_right_mouse_click)
        self.canvas.bind('<Enter>', self._on_mouse_enter)
        self.canvas.bind('<Leave>', self._on_mouse_leave)
        
        # Position window
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.current_x = screen_width - self.width - 100
        self.current_y = 100
        self.target_x = self.current_x
        self.target_y = self.current_y
        self._update_position()
        
        # Start animation loop
        self.is_running = True
        self._animate()
        
    def _draw_mascot_static(self):
        """Draw the static parts of the Vigil mascot on the canvas (called once)."""
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Outer glow circle
        self.canvas.create_oval(
            center_x - 50, center_y - 50,
            center_x + 50, center_y + 50,
            fill='#16213e',
            outline='#0f3460',
            width=2,
        )
        
        # Inner circle
        self.canvas.create_oval(
            center_x - 40, center_y - 40,
            center_x + 40, center_y + 40,
            fill='#0f3460',
            outline='#533483',
            width=2,
        )
        
        # Draw "V" shape
        v_points = [
            center_x - 15, center_y - 15,  # Top left
            center_x, center_y + 15,        # Bottom center
            center_x + 15, center_y - 15,   # Top right
            center_x + 10, center_y - 15,   # Inner top right
            center_x, center_y + 5,         # Inner bottom
            center_x - 10, center_y - 15,   # Inner top left
        ]
        self.canvas.create_polygon(
            v_points,
            fill='#e94560',
            outline='#ff6b9d',
            width=1,
        )
    
    def _create_animated_elements(self):
        """Create animated elements that will be updated each frame."""
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Create eye (will be moved each frame)
        self.eye_item = self.canvas.create_oval(
            center_x - 3, center_y - 20,
            center_x + 3, center_y - 14,
            fill='#00ffff',
            outline='',
        )
        
        # Create status indicator (will change color each frame)
        self.status_indicator_item = self.canvas.create_oval(
            center_x + 35, center_y - 35,
            center_x + 42, center_y - 28,
            fill=WidgetConfig.STATUS_COLOR_1,
            outline='',
        )
    
    def _update_animated_elements(self):
        """Update only the animated elements for better performance."""
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Update eye position (gentle bobbing)
        eye_offset = math.sin(self.animation_phase) * 2
        self.canvas.coords(
            self.eye_item,
            center_x - 3, center_y - 20 + eye_offset,
            center_x + 3, center_y - 14 + eye_offset,
        )
        
        # Update status indicator color (pulsing)
        pulse = (math.sin(self.animation_phase * WidgetConfig.EYE_PULSE_MULTIPLIER) + 1) / 2
        indicator_color = self._interpolate_color(
            WidgetConfig.STATUS_COLOR_1, 
            WidgetConfig.STATUS_COLOR_2, 
            pulse
        )
        self.canvas.itemconfig(self.status_indicator_item, fill=indicator_color)
        
    def _interpolate_color(self, color1: str, color2: str, t: float) -> str:
        """Interpolate between two hex colors."""
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def _on_mouse_down(self, event):
        """Handle mouse button press."""
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def _on_mouse_drag(self, event):
        """Handle mouse drag."""
        if self.is_dragging:
            # Calculate new position
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            self.current_x += dx
            self.current_y += dy
            self.target_x = self.current_x
            self.target_y = self.current_y
            
            self._update_position()
            
    def _on_mouse_up(self, event):
        """Handle mouse button release."""
        if self.is_dragging:
            self.is_dragging = False
        else:
            # If not dragging, this was a click
            if self.on_click:
                self.on_click()
                
    def _on_right_mouse_click(self, event):
        """Handle right mouse click."""
        if self.on_right_click:
            self.on_right_click()
            
    def _on_mouse_enter(self, event):
        """Handle mouse entering the widget."""
        self.window.attributes('-alpha', WidgetConfig.OPACITY_HOVER)
        
    def _on_mouse_leave(self, event):
        """Handle mouse leaving the widget."""
        self.window.attributes('-alpha', WidgetConfig.OPACITY_NORMAL)
        
    def _update_position(self):
        """Update window position."""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Keep within screen bounds
        self.current_x = max(0, min(self.current_x, screen_width - self.width))
        self.current_y = max(0, min(self.current_y, screen_height - self.height))
        
        self.window.geometry(f'{self.width}x{self.height}+{int(self.current_x)}+{int(self.current_y)}')
        
    def _animate(self):
        """Animation loop - optimized to only update what changes."""
        if not self.is_running:
            return
            
        # Update animation phase
        self.animation_phase += WidgetConfig.ANIMATION_SPEED
        
        # Gentle floating movement when not being dragged
        if not self.is_dragging:
            self.idle_animation_counter += 1
            
            # Every few seconds, pick a new gentle target nearby
            if self.idle_animation_counter > WidgetConfig.IDLE_MOVEMENT_INTERVAL:
                self.idle_animation_counter = 0
                offset_x = random.uniform(-WidgetConfig.IDLE_MOVEMENT_RANGE, WidgetConfig.IDLE_MOVEMENT_RANGE)
                offset_y = random.uniform(-WidgetConfig.IDLE_MOVEMENT_RANGE, WidgetConfig.IDLE_MOVEMENT_RANGE)
                self.target_x = self.current_x + offset_x
                self.target_y = self.current_y + offset_y
                
            # Smooth movement toward target
            dx = self.target_x - self.current_x
            dy = self.target_y - self.current_y
            
            self.velocity_x += dx * WidgetConfig.MOVEMENT_ACCELERATION
            self.velocity_y += dy * WidgetConfig.MOVEMENT_ACCELERATION
            
            # Apply friction
            self.velocity_x *= WidgetConfig.MOVEMENT_FRICTION
            self.velocity_y *= WidgetConfig.MOVEMENT_FRICTION
            
            # Update position
            self.current_x += self.velocity_x
            self.current_y += self.velocity_y
            
            self._update_position()
        
        # Update only the animated elements (much more efficient than redrawing everything)
        self._update_animated_elements()
        
        # Schedule next frame
        self.window.after(WidgetConfig.ANIMATION_FRAME_MS, self._animate)
        
    def show(self):
        """Show the widget."""
        self.window.deiconify()
        
    def hide(self):
        """Hide the widget."""
        self.window.withdraw()
        
    def run(self):
        """Start the widget's main loop."""
        self.window.mainloop()
        
    def stop(self):
        """Stop the widget."""
        self.is_running = False
        self.window.quit()
        self.window.destroy()


# Test the widget
if __name__ == '__main__':
    def on_click():
        print("Widget clicked!")
        
    def on_right_click():
        print("Widget right-clicked!")
        
    widget = VigilDesktopWidget(
        on_click=on_click,
        on_right_click=on_right_click,
    )
    widget.run()
