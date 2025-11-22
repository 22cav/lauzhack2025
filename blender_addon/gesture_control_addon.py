"""
Blender Gesture Control Addon

This addon runs inside Blender and receives gesture commands from the orchestrator,
executing them to control the viewport, timeline, and objects.

Installation:
1. Save this file as gesture_control_addon.py
2. In Blender: Edit → Preferences → Add-ons → Install
3. Select this file and enable the addon
4. The gesture listener will start automatically

Usage:
- Run main_orchestrator.py with Blender config
- Perform gestures in front of camera
- Watch Blender respond in real-time
"""

bl_info = {
    "name": "Gesture Control Listener",
    "author": "Lauzhack Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
    "description": "Receive gesture commands and control Blender viewport/timeline",
    "category": "3D View",
}

import bpy
import socket
import threading
import json
import mathutils
from bpy.app.handlers import persistent


class GestureControlPreferences(bpy.types.AddonPreferences):
    """Addon preferences for gesture control settings."""
    bl_idname = __name__
    
    port: bpy.props.IntProperty(
        name="Port",
        description="Port to listen for gesture commands",
        default=8888,
        min=1024,
        max=65535
    )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "port")


class GestureControlListener:
    """Handles socket communication and command execution."""
    
    def __init__(self, port=8888):
        self.port = port
        self.server = None
        self.running = False
        self.thread = None
        self.last_command = "None"
        self.command_count = 0
        
    def start(self):
        """Start the gesture listener server."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        print(f"[Gesture Control] Listener started on port {self.port}")
        
    def stop(self):
        """Stop the gesture listener server."""
        self.running = False
        if self.server:
            try:
                self.server.close()
            except:
                pass
        print("[Gesture Control] Listener stopped")
        
    def _listen(self):
        """Listen for incoming gesture commands."""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('localhost', self.port))
            self.server.listen(5)
            print(f"[Gesture Control] Listening on localhost:{self.port}")
            
            while self.running:
                try:
                    client, addr = self.server.accept()
                    print(f"[Gesture Control] Client connected: {addr}")
                    
                    while self.running:
                        data = client.recv(1024)
                        if not data:
                            break
                        
                        # Parse JSON command
                        try:
                            command = json.loads(data.decode('utf-8'))
                            self._execute_command(command)
                        except json.JSONDecodeError:
                            print(f"[Gesture Control] Invalid JSON: {data}")
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[Gesture Control] Error: {e}")
                        
        except Exception as e:
            print(f"[Gesture Control] Server error: {e}")
            
    def _execute_command(self, command):
        """Execute a gesture command in Blender."""
        cmd_type = command.get('command')
        self.last_command = cmd_type
        self.command_count += 1
        
        print(f"[Gesture Control] Command #{self.command_count}: {cmd_type}")
        
        # Schedule command execution in main thread
        bpy.app.timers.register(lambda: self._execute_in_main_thread(cmd_type, command), first_interval=0.0)
        
    def _execute_in_main_thread(self, cmd_type, command):
        """Execute command in Blender's main thread (required for operators)."""
        try:
            if cmd_type == 'viewport_rotate':
                self._rotate_viewport(command)
            elif cmd_type == 'play_animation':
                self._play_animation()
            elif cmd_type == 'pause_animation':
                self._pause_animation()
            elif cmd_type == 'next_frame':
                self._next_frame()
            elif cmd_type == 'previous_frame':
                self._previous_frame()
            elif cmd_type == 'toggle_edit_mode':
                self._toggle_edit_mode()
            else:
                print(f"[Gesture Control] Unknown command: {cmd_type}")
                
        except Exception as e:
            print(f"[Gesture Control] Execution error: {e}")
            
        # Return None to not repeat this timer
        return None
        
    def _rotate_viewport(self, command):
        """Rotate the 3D viewport based on hand movement."""
        rotation = command.get('rotation', {})
        rx = rotation.get('x', 0)
        ry = rotation.get('y', 0)
        
        # Get active 3D view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        # Get the region 3D
                        space = area.spaces.active
                        rv3d = space.region_3d
                        
                        # Apply rotation (convert to radians and scale)
                        rotation_x = mathutils.Euler((rx * 0.01, 0, 0))
                        rotation_y = mathutils.Euler((0, 0, ry * 0.01))
                        
                        # Update view rotation
                        rv3d.view_rotation = rv3d.view_rotation @ rotation_x.to_quaternion()
                        rv3d.view_rotation = rv3d.view_rotation @ rotation_y.to_quaternion()
                        
                        # Force redraw
                        area.tag_redraw()
                        break
                        
        print(f"[Gesture Control] Viewport rotated: x={rx:.2f}, y={ry:.2f}")
        
    def _play_animation(self):
        """Start animation playback."""
        if not bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
            print("[Gesture Control] Animation playing")
        
    def _pause_animation(self):
        """Pause animation playback."""
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel()
            print("[Gesture Control] Animation paused")
        
    def _next_frame(self):
        """Advance one frame forward."""
        bpy.context.scene.frame_current += 1
        print(f"[Gesture Control] Frame: {bpy.context.scene.frame_current}")
        
    def _previous_frame(self):
        """Go back one frame."""
        bpy.context.scene.frame_current -= 1
        print(f"[Gesture Control] Frame: {bpy.context.scene.frame_current}")
        
    def _toggle_edit_mode(self):
        """Toggle between object and edit mode."""
        if bpy.context.active_object:
            if bpy.context.mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='EDIT')
                print("[Gesture Control] Switched to EDIT mode")
            else:
                bpy.ops.object.mode_set(mode='OBJECT')
                print("[Gesture Control] Switched to OBJECT mode")


# Global listener instance
gesture_listener = None


class VIEW3D_PT_GestureControl(bpy.types.Panel):
    """UI panel for gesture control."""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gesture"
    bl_label = "Gesture Control"
    
    def draw(self, context):
        layout = self.layout
        
        global gesture_listener
        
        if gesture_listener and gesture_listener.running:
            layout.label(text="Status: Listening", icon='PLAY')
            layout.label(text=f"Port: {gesture_listener.port}")
            layout.label(text=f"Last Command: {gesture_listener.last_command}")
            layout.label(text=f"Commands: {gesture_listener.command_count}")
            layout.operator("gesture.stop_listener", text="Stop Listener", icon='PAUSE')
        else:
            layout.label(text="Status: Stopped", icon='PAUSE')
            layout.operator("gesture.start_listener", text="Start Listener", icon='PLAY')


class GESTURE_OT_StartListener(bpy.types.Operator):
    """Start the gesture control listener."""
    bl_idname = "gesture.start_listener"
    bl_label = "Start Gesture Listener"
    
    def execute(self, context):
        global gesture_listener
        
        prefs = context.preferences.addons[__name__].preferences
        
        if gesture_listener is None:
            gesture_listener = GestureControlListener(port=prefs.port)
        
        gesture_listener.start()
        self.report({'INFO'}, f"Gesture listener started on port {prefs.port}")
        return {'FINISHED'}


class GESTURE_OT_StopListener(bpy.types.Operator):
    """Stop the gesture control listener."""
    bl_idname = "gesture.stop_listener"
    bl_label = "Stop Gesture Listener"
    
    def execute(self, context):
        global gesture_listener
        
        if gesture_listener:
            gesture_listener.stop()
            self.report({'INFO'}, "Gesture listener stopped")
        
        return {'FINISHED'}


@persistent
def load_handler(dummy):
    """Auto-start listener when Blender starts."""
    global gesture_listener
    
    # Auto-start in 2 seconds (give Blender time to initialize)
    bpy.app.timers.register(auto_start_listener, first_interval=2.0)


def auto_start_listener():
    """Auto-start the gesture listener."""
    global gesture_listener
    
    try:
        prefs = bpy.context.preferences.addons[__name__].preferences
        
        if gesture_listener is None:
            gesture_listener = GestureControlListener(port=prefs.port)
        
        if not gesture_listener.running:
            gesture_listener.start()
            print("[Gesture Control] Auto-started listener")
    except Exception as e:
        print(f"[Gesture Control] Auto-start failed: {e}")
    
    return None  # Don't repeat


# Registration
classes = (
    GestureControlPreferences,
    VIEW3D_PT_GestureControl,
    GESTURE_OT_StartListener,
    GESTURE_OT_StopListener,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.app.handlers.load_post.append(load_handler)
    
    # Auto-start on registration
    bpy.app.timers.register(auto_start_listener, first_interval=1.0)


def unregister():
    global gesture_listener
    
    if gesture_listener:
        gesture_listener.stop()
    
    bpy.app.handlers.load_post.remove(load_handler)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
