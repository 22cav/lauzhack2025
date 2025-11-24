"""
UI Panels

All UI panels for gesture control with type-safe layout code.
"""

from typing import Optional
import bpy
from bpy.types import Panel, Context, UILayout


class VIEW3D_PT_GestureControl(Panel):
    """Main gesture control panel"""
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = "3DX"
    bl_label: str = "Gesture Control"
    
    def draw(self, context: Context) -> None:
        """
        Draw main control panel.
        
        Args:
            context: Blender context
            
        #TODO: Implement panel layout
        Layout structure:
        1. Status box (running/stopped, camera status)
        2. Start/Stop/Pause buttons
        3. Live statistics (FPS, last gesture, confidence)
        4. Quick settings access
        """
        layout: UILayout = self.layout
        state = context.scene.gesture_state
        
        # Status
        box = layout.box()
        if state.is_running:
            if state.is_paused:
                box.label(text="Status: PAUSED", icon='PAUSE')
            else:
                box.label(text="Status: ACTIVE", icon='PLAY')
            
            if state.camera_ready:
                box.label(text="Camera: Ready", icon='CAMERA_DATA')
            else:
                box.label(text="Camera: Error", icon='ERROR')
        else:
            box.label(text="Status: STOPPED", icon='SNAP_FACE')
        
        # Control buttons
        row = layout.row()
        if not state.is_running:
            row.scale_y = 1.5
            row.operator("gesture.start", icon='PLAY', text="Start")
        else:
            col = row.column()
            col.operator("gesture.stop", icon='SNAP_FACE', text="Stop")
            col = row.column()
            if state.is_paused:
                col.operator("gesture.toggle_pause", icon='PLAY', text="Resume")
            else:
                col.operator("gesture.toggle_pause", icon='PAUSE', text="Pause")
        
        # Statistics (when running)
        if state.is_running:
            layout.separator()
            box = layout.box()
            box.label(text="Statistics", icon='INFO')
            
            row = box.row()
            row.label(text=f"FPS: {state.current_fps:.1f}")
            
            row = box.row()
            row.label(text=f"Last: {state.last_gesture}")
            
            if state.last_gesture != "None":
                row = box.row()
                row.label(text=f"Conf: {state.last_confidence:.2f}")
            
            row = box.row()
            row.label(text=f"Frames: {state.frames_processed}")


class VIEW3D_PT_GestureSettings(Panel):
    """Gesture settings panel"""
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = "3DX"
    bl_label: str = "Settings"
    bl_parent_id: str = "VIEW3D_PT_GestureControl"
    bl_options: set = {'DEFAULT_CLOSED'}
    
    def draw(self, context: Context) -> None:
        """
        Draw settings panel.
        
        Args:
            context: Blender context
        """
        layout: UILayout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        
        # Camera
        box = layout.box()
        box.label(text="Camera", icon='CAMERA_DATA')
        box.prop(prefs, "camera_index")
        box.operator("gesture.test_camera", icon='CAMERA_DATA')
        
        # Sensitivity
        box = layout.box()
        box.label(text="Sensitivity", icon='DRIVER')
        box.prop(prefs, "rotation_sensitivity", slider=True)
        box.prop(prefs, "pan_sensitivity", slider=True)
        
        # Gestures
        box = layout.box()
        box.label(text="Enable Gestures", icon='HAND')
        box.prop(prefs, "enable_pinch")
        box.prop(prefs, "enable_v_gesture")
        box.prop(prefs, "enable_palm")
        box.prop(prefs, "enable_fist")
        
        # Display
        box = layout.box()
        box.label(text="Display", icon='WINDOW')
        box.prop(prefs, "show_preview")
        box.prop(prefs, "show_debug")
        
        # Actions
        layout.separator()
        layout.operator("gesture.reset_settings", icon='LOOP_BACK')


class VIEW3D_PT_GestureHelp(Panel):
    """Help and documentation panel"""
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = "3DX"
    bl_label: str = "Help"
    bl_parent_id: str = "VIEW3D_PT_GestureControl"
    bl_options: set = {'DEFAULT_CLOSED'}
    
    def draw(self, context: Context) -> None:
        """
        Draw help panel.
        
        Args:
            context: Blender context
        """
        layout: UILayout = self.layout
        
        # Gesture reference
        box = layout.box()
        box.label(text="Gestures", icon='INFO')
        box.label(text="🤏 Pinch - Rotate viewport")
        box.label(text="✌️ V-Gesture - Pan camera")
        box.label(text="🖐️ Palm - Play animation")
        box.label(text="✊ Fist - Stop animation")
        
        layout.separator()
        
        # Tips
        box = layout.box()
        box.label(text="Tips", icon='LIGHT')
        box.label(text="• Ensure good lighting")
        box.label(text="• Keep hand visible")
        box.label(text="• Adjust sensitivity")
        
        layout.separator()
        
        # Documentation
        layout.operator("gesture.show_help", icon='HELP')


# ============================================================================
# Registration
# ============================================================================

classes: tuple = (
    VIEW3D_PT_GestureControl,
    VIEW3D_PT_GestureSettings,
    VIEW3D_PT_GestureHelp,
)


def register() -> None:
    """Register panel classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister panel classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
