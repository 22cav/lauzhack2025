"""
Production Gesture Recognition System

A modular, robust gesture detection system with:
- Multiple gesture types (basic, pinch, movement, compound)
- Smoothing and filtering for precision
- Confidence scoring and validation
- Extensible gesture registry
"""

from .detector import GestureDetector, GestureResult
from .registry import GestureRegistry, Gesture
from .filters import LandmarkFilter, MovementFilter
from .validators import ConfidenceValidator, QualityValidator

__all__ = [
    'GestureDetector',
    'GestureResult',
    'GestureRegistry',
    'Gesture',
    'LandmarkFilter',
    'MovementFilter',
    'ConfidenceValidator',
    'QualityValidator',
]
