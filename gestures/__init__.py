"""
Gestures Module

Provides gesture detection, filtering, and validation functionality.
"""

from gestures.detector import Gesture, GestureResult, GestureDetector
from gestures.validators import GestureValidator, ValidatorConfig
from gestures.filters import OneEuroFilter, FilterConfig, LowPassFilter

# Import all gesture implementations
from gestures.library.basic import OpenPalmGesture, ClosedFistGesture
from gestures.library.navigation import PinchGesture, VGesture
from gestures.library.advanced import PointingGesture, ThumbsUpGesture

__all__ = [
    # Core components
    'Gesture',
    'GestureResult',
    'GestureDetector',
    'GestureValidator',
    'ValidatorConfig',
    'OneEuroFilter',
    'FilterConfig',
    'LowPassFilter',
    
    # Gesture implementations
    'OpenPalmGesture',
    'ClosedFistGesture',
    'PinchGesture',
    'VGesture',
    'PointingGesture',
    'ThumbsUpGesture',
]
