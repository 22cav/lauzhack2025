"""
Configuration and Constants

Default settings, gesture mappings, and configuration constants for the 3DX addon.
"""

from typing import Dict, Any, Final

# ============================================================================
# Addon Information
# ============================================================================

ADDON_NAME: Final[str] = "3DX"
ADDON_VERSION: Final[tuple] = (1, 0, 0)
BLENDER_VERSION_MIN: Final[tuple] = (3, 0, 0)

# ============================================================================
# Default Settings
# ============================================================================

DEFAULT_SETTINGS: Final[Dict[str, Any]] = {
    # Camera
    "camera_index": 0,
    
    # Gesture Sensitivity
    "rotation_sensitivity": 0.5,
    "pan_sensitivity": 0.1,
    
    # Detection
    "frame_rate": 30,
    "min_confidence": 0.6,
    
    # Display
    "show_preview": True,
    "show_debug": False,
    
    # Gesture Toggles
    "enable_pinch": True,
    "enable_v_gesture": True,
    "enable_palm": True,
    "enable_fist": True,
}

# ============================================================================
# Gesture Mappings
# ============================================================================

GESTURE_MAPPINGS: Final[Dict[str, str]] = {
    "PINCH_DRAG": "rotate_viewport",
    "V_GESTURE_MOVE": "pan_viewport",
    "OPEN_PALM": "play_animation",
    "CLOSED_FIST": "stop_animation",
}

# Gesture names
GESTURE_PINCH: Final[str] = "PINCH_DRAG"
GESTURE_V_MOVE: Final[str] = "V_GESTURE_MOVE"
GESTURE_PALM: Final[str] = "OPEN_PALM"
GESTURE_FIST: Final[str] = "CLOSED_FIST"

# ============================================================================
# Camera Settings
# ============================================================================

CAMERA_WIDTH: Final[int] = 640
CAMERA_HEIGHT: Final[int] = 480
CAMERA_FPS: Final[int] = 30

# ============================================================================
# MediaPipe Settings
# ============================================================================

MP_MIN_DETECTION_CONFIDENCE: Final[float] = 0.5
MP_MIN_TRACKING_CONFIDENCE: Final[float] = 0.5
MP_MAX_NUM_HANDS: Final[int] = 2

# ============================================================================
# Performance Settings
# ============================================================================

# Modal operator timer interval (seconds)
TIMER_INTERVAL: Final[float] = 0.033  # ~30 FPS

# Gesture cooldown (seconds) - prevent rapid repeated triggers
GESTURE_COOLDOWN: Final[float] = 0.1

# Maximum history size for gesture filters
MAX_GESTURE_HISTORY: Final[int] = 30
