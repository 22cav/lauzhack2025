"""
Configuration and Constants

Default settings, gesture mappings, and configuration constants for the 3DX addon.
Pydantic models for configuration validation.
"""

from typing import Dict, Any, Final
from pydantic import BaseModel, Field

# Addon Information

ADDON_NAME: Final[str] = "3DX"
ADDON_VERSION: Final[tuple] = (1, 0, 0)
BLENDER_VERSION_MIN: Final[tuple] = (3, 0, 0)

# Configuration Models

class CameraSettings(BaseModel):
    """
    Camera settings for the addon.
    """
    index: int = Field(0, ge=0)
    width: int = Field(640, gt=0)
    height: int = Field(480, gt=0)
    fps: int = Field(30, gt=0)

class SensitivitySettings(BaseModel):
    """
    Sensitivity settings for the addon.
    """
    rotation: float = Field(0.5, gt=0.0)
    pan: float = Field(0.1, gt=0.0)

class DetectionSettings(BaseModel):
    """
    Detection settings for the addon.
    """
    frame_rate: int = Field(30, ge=1, le=120)
    min_confidence: float = Field(0.6, ge=0.0, le=1.0)

class DisplaySettings(BaseModel):
    """
    Display settings for the addon.
    """
    show_preview: bool = True
    show_debug: bool = False

class GestureToggles(BaseModel):
    """
    Gesture toggles for the addon.
    """
    enable_pinch: bool = True
    enable_v_gesture: bool = True
    enable_palm: bool = True
    enable_fist: bool = True

class AddonConfig(BaseModel):
    """
    Master configuration model.
    """
    camera: CameraSettings = Field(default_factory=CameraSettings)
    sensitivity: SensitivitySettings = Field(default_factory=SensitivitySettings)
    detection: DetectionSettings = Field(default_factory=DetectionSettings)
    display: DisplaySettings = Field(default_factory=DisplaySettings)
    gestures: GestureToggles = Field(default_factory=GestureToggles)

# Default Settings (Dict for Blender Props)

DEFAULT_SETTINGS: Final[Dict[str, Any]] = {
    # Camera
    "camera_index": 0,
    
    # Gesture Sensitivity
    "rotation_sensitivity": 0.1,
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

# Gesture Mappings

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

# Performance Settings

TIMER_INTERVAL: Final[float] = 0.033
GESTURE_COOLDOWN: Final[float] = 0.1
MAX_GESTURE_HISTORY: Final[int] = 30
