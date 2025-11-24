"""
UI Panels

All UI panels for gesture control with type-safe layout code.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

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
        Draw main control panel with enhanced visual feedback.
        
        Args:
            context: Blender context
        """
        layout: UILayout = self.layout
        state = context.scene.gesture_state
        
        # Enhanced Status Section
        box = layout.box()
        col = box.column(align=True)
        
        # Status header with icon and color
        if state.is_running:
            if state.is_paused:
                col.label(text="PAUSED", icon='PAUSE')
                row = col.row()
                row.scale_y = 0.8
                row.label(text="Gesture recognition is paused")
            else:
                col.label(text="ACTIVE", icon='PLAY')
                row = col.row()
                row.scale_y = 0.8
                row.label(text="Detecting gestures...")
            
            # Camera status
            col.separator(factor=0.5)
            if state.camera_ready:
                row = col.row()
                row.label(text="Camera: Ready", icon='CHECKMARK')
            else:
                row = col.row()
                row.label(text="Camera: Error", icon='ERROR')
                if state.camera_error:
                    row = col.row()
                    row.scale_y = 0.7
                    row.label(text=state.camera_error)
        else:
            col.label(text="STOPPED", icon='SNAP_FACE')
            row = col.row()
            row.scale_y = 0.8
            row.label(text="Press Start to begin")
        
        layout.separator()
        
        # Control Buttons Section
        box = layout.box()
        if not state.is_running:
            # Big start button when not running
            row = box.row()
            row.scale_y = 2.0
            row.operator("gesture.start", icon='PLAY', text="Start Gesture Control")
        else:
            # Control buttons when running
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.5
            
            # Stop button
            stop_btn = row.operator("gesture.stop", icon='SNAP_FACE', text="Stop")
            
            # Pause/Resume button
            if state.is_paused:
                pause_btn = row.operator("gesture.toggle_pause", icon='PLAY', text="Resume")
            else:
                pause_btn = row.operator("gesture.toggle_pause", icon='PAUSE', text="Pause")
        
        # Live Statistics (when running)
        if state.is_running:
            layout.separator()
            box = layout.box()
            col = box.column(align=True)
            
            # Header
            row = col.row()
            row.label(text="Live Statistics", icon='INFO')
            
            col.separator(factor=0.5)
            
            # Statistics grid
            split = col.split(factor=0.4, align=True)
            split.label(text="FPS:")
            split.label(text=f"{state.current_fps:.1f}")
            
            split = col.split(factor=0.4, align=True)
            split.label(text="Frames:")
            split.label(text=f"{state.frames_processed}")
            
            if state.last_gesture != "None":
                col.separator(factor=0.5)
                split = col.split(factor=0.4, align=True)
                split.label(text="Last Gesture:")
                split.label(text=state.last_gesture, icon='HAND')
                
                split = col.split(factor=0.4, align=True)
                split.label(text="Confidence:")
                # Color-coded confidence
                row = split.row()
                if state.last_confidence >= 0.8:
                    row.label(text=f"{state.last_confidence:.0%}", icon='CHECKMARK')
                elif state.last_confidence >= 0.6:
                    row.label(text=f"{state.last_confidence:.0%}", icon='DOT')
                else:
                    row.label(text=f"{state.last_confidence:.0%}", icon='ERROR')
            
            if state.gestures_detected > 0:
                col.separator(factor=0.5)
                split = col.split(factor=0.4, align=True)
                split.label(text="Detected:")
                split.label(text=f"{state.gestures_detected} total")



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
        Draw settings panel with improved organization.
        
        Args:
            context: Blender context
        """
        layout: UILayout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        
        # Camera Settings
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.label(text="Camera", icon='CAMERA_DATA')
        
        col.separator(factor=0.3)
        col.prop(prefs, "camera_index")
        
        row = col.row()
        row.scale_y = 1.2
        row.operator("gesture.test_camera", icon='PLAY', text="Test Camera")
        
        layout.separator()
        
        # Sensitivity Settings
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.label(text="Sensitivity", icon='DRIVER')
        
        col.separator(factor=0.3)
        col.prop(prefs, "rotation_sensitivity", slider=True)
        col.prop(prefs, "pan_sensitivity", slider=True)
        
        layout.separator()
        
        # Gesture Toggles
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.label(text="Enable Gestures", icon='HAND')
        
        col.separator(factor=0.3)
        
        # Use split for better alignment
        split = col.split(factor=0.7, align=True)
        split.prop(prefs, "enable_pinch", text="Pinch (Rotate)")
        split.label(text="🤏", icon='NONE')
        
        split = col.split(factor=0.7, align=True)
        split.prop(prefs, "enable_v_gesture", text="V-Gesture (Pan)")
        split.label(text="✌️", icon='NONE')
        
        split = col.split(factor=0.7, align=True)
        split.prop(prefs, "enable_palm", text="Palm (Play)")
        split.label(text="🖐️", icon='NONE')
        
        split = col.split(factor=0.7, align=True)
        split.prop(prefs, "enable_fist", text="Fist (Stop)")
        split.label(text="✊", icon='NONE')
        
        layout.separator()
        
        # Display Options
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.label(text="Display", icon='WINDOW')
        
        col.separator(factor=0.3)
        col.prop(prefs, "show_preview")
        col.prop(prefs, "show_debug")
        
        layout.separator()
        
        # Actions
        row = layout.row()
        row.scale_y = 1.3
        row.operator("gesture.reset_settings", icon='LOOP_BACK', text="Reset to Defaults")



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
