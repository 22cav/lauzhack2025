import bpy
import sys
import os
import config

# ------------------------------------------------------------------------
# BLENDER PROPERTIES
# ------------------------------------------------------------------------

from bpy.props import (
    IntProperty,
    FloatProperty,
    BoolProperty,
    StringProperty,
    PointerProperty
)
from bpy.types import AddonPreferences, PropertyGroup

class GestureAddonPreferences(AddonPreferences):
    """
    Addon preferences - user settings that persist across sessions.
    """
    # The bl_idname must match the addon module name for Preferences to show up
    # If running as a script in Text Editor, we use __name__
    bl_idname = __package__ if __package__ else __name__
    
    # ========================================================================
    # Camera Settings
    # ========================================================================
    
    camera_index: IntProperty(
        name="Camera Index",
        description="Which camera to use (0 = default, 1 = secondary, etc.)",
        default=config.DEFAULT_SETTINGS["camera_index"],
        min=0,
        max=10
    )
    
    # ========================================================================
    # Gesture Sensitivity
    # ========================================================================
    
    rotation_sensitivity: FloatProperty(
        name="Rotation Sensitivity",
        description="How sensitive rotation gestures are (higher = more sensitive)",
        default=config.DEFAULT_SETTINGS["rotation_sensitivity"],
        min=0.01,
        max=5.0,
        precision=2
    )
    
    pan_sensitivity: FloatProperty(
        name="Pan Sensitivity",
        description="How sensitive panning gestures are (higher = more sensitive)",
        default=config.DEFAULT_SETTINGS["pan_sensitivity"],
        min=0.01,
        max=2.0,
        precision=2
    )
    
    # ========================================================================
    # Display Options
    # ========================================================================
    
    show_preview: BoolProperty(
        name="Show Camera Preview",
        description="Display camera feed in Blender (performance impact)",
        default=config.DEFAULT_SETTINGS["show_preview"]
    )
    
    show_debug: BoolProperty(
        name="Show Debug Info",
        description="Display debug information in console",
        default=config.DEFAULT_SETTINGS["show_debug"]
    )
    
    # ========================================================================
    # Gesture Toggles
    # ========================================================================
    
    enable_pinch: BoolProperty(
        name="Enable Pinch Rotation",
        description="Enable pinch gesture for viewport rotation",
        default=config.DEFAULT_SETTINGS["enable_pinch"]
    )
    
    enable_v_gesture: BoolProperty(
        name="Enable V Navigation",
        description="Enable V gesture for viewport panning",
        default=config.DEFAULT_SETTINGS["enable_v_gesture"]
    )
    
    enable_palm: BoolProperty(
        name="Enable Palm (Play)",
        description="Enable open palm gesture to play animation",
        default=config.DEFAULT_SETTINGS["enable_palm"]
    )
    
    enable_fist: BoolProperty(
        name="Enable Fist (Stop)",
        description="Enable closed fist gesture to stop animation",
        default=config.DEFAULT_SETTINGS["enable_fist"]
    )
    
    # ========================================================================
    # Advanced Settings
    # ========================================================================
    
    frame_rate: IntProperty(
        name="Frame Rate",
        description="Camera processing frame rate (lower = better performance)",
        default=config.DEFAULT_SETTINGS["frame_rate"],
        min=10,
        max=60
    )
    
    min_confidence: FloatProperty(
        name="Min Confidence",
        description="Minimum confidence threshold for gesture detection",
        default=config.DEFAULT_SETTINGS["min_confidence"],
        min=0.1,
        max=1.0,
        precision=2
    )
    
    def draw(self, context):
        layout = self.layout
        
        # Camera
        box = layout.box()
        box.label(text="Camera", icon='CAMERA_DATA')
        box.prop(self, "camera_index")
        
        # Sensitivity
        box = layout.box()
        box.label(text="Sensitivity", icon='DRIVER')
        box.prop(self, "rotation_sensitivity")
        box.prop(self, "pan_sensitivity")
        
        # Display
        box = layout.box()
        box.label(text="Display", icon='WINDOW')
        box.prop(self, "show_preview")
        box.prop(self, "show_debug")
        
        # Gestures
        box = layout.box()
        box.label(text="Enable Gestures", icon='HAND')
        box.prop(self, "enable_pinch")
        box.prop(self, "enable_v_gesture")
        box.prop(self, "enable_palm")
        box.prop(self, "enable_fist")
        
        # Advanced
        box = layout.box()
        box.label(text="Advanced", icon='PREFERENCES')
        box.prop(self, "frame_rate")
        box.prop(self, "min_confidence")


class GestureRuntimeState(PropertyGroup):
    """
    Runtime state - temporary data that doesn't persist.
    Stores current gesture control state, statistics, and status information.
    """
    
    # ========================================================================
    # Control State
    # ========================================================================
    
    is_running: BoolProperty(
        name="Is Running",
        description="Whether gesture control is currently active",
        default=False
    )
    
    is_paused: BoolProperty(
        name="Is Paused",
        description="Whether gesture control is paused",
        default=False
    )
    
    # ========================================================================
    # Camera State
    # ========================================================================
    
    camera_ready: BoolProperty(
        name="Camera Ready",
        description="Whether camera is initialized and ready",
        default=False
    )
    
    camera_error: StringProperty(
        name="Camera Error",
        description="Last camera error message",
        default=""
    )
    
    # ========================================================================
    # Gesture State
    # ========================================================================
    
    last_gesture: StringProperty(
        name="Last Gesture",
        description="Name of last detected gesture",
        default="None"
    )
    
    last_confidence: FloatProperty(
        name="Last Confidence",
        description="Confidence of last detected gesture",
        default=0.0,
        min=0.0,
        max=1.0
    )
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    frames_processed: IntProperty(
        name="Frames Processed",
        description="Total frames processed since start",
        default=0,
        min=0
    )
    
    current_fps: FloatProperty(
        name="Current FPS",
        description="Current frames per second",
        default=0.0,
        min=0.0,
        precision=1
    )
    
    gestures_detected: IntProperty(
        name="Gestures Detected",
        description="Total gestures detected since start",
        default=0,
        min=0
    )


# ============================================================================
# Registration
# ============================================================================

classes = (
    GestureAddonPreferences,
    GestureRuntimeState,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gesture_state = PointerProperty(type=GestureRuntimeState)


def unregister():
    if hasattr(bpy.types.Scene, 'gesture_state'):
        del bpy.types.Scene.gesture_state
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()