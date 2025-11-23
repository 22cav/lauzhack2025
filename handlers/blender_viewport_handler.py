"""
Blender Viewport Handler - Controls Blender viewport manipulation.

Handles rotation, panning, and zooming gestures for Blender's 3D viewport.
"""

import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.gesture_handler import GestureHandler, HandlerContext

logger = logging.getLogger(__name__)


class BlenderViewportHandler(GestureHandler):
    """
    Handler for Blender viewport manipulation.
    
    Supports:
    - PINCH_DRAG / ROTATE: Rotate viewport (yaw + pitch)
    - V_GESTURE / NAVIGATE: Pan viewport
    - Future: Zoom gestures
    
    Configuration:
        sensitivity: Movement sensitivity multiplier (default: 1.0)
        invert_x: Invert horizontal movement (default: False)
        invert_y: Invert vertical movement (default: False)
        smooth_factor: Smoothing factor for movements (default: 1.0)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize viewport handler.
        
        Args:
            config: Handler configuration
        """
        # Set default gestures if not specified
        if 'gestures' not in config:
            config['gestures'] = ['PINCH_DRAG', 'ROTATE', 'V_GESTURE', 'NAVIGATE']
        
        super().__init__('blender_viewport', config)
        
        # Handler-specific settings
        self.sensitivity = config.get('sensitivity', 1.0)
        self.invert_x = config.get('invert_x', False)
        self.invert_y = config.get('invert_y', False)
        self.smooth_factor = config.get('smooth_factor', 1.0)
        
        logger.info(f"BlenderViewportHandler initialized (sensitivity={self.sensitivity})")
    
    def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
        """
        Handle viewport manipulation gestures.
        
        Args:
            context: Handler execution context
        
        Returns:
            Command data for Blender or None
        """
        gesture = context.gesture
        data = context.data
        
        # Extract movement data
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        
        # Apply inversions
        if self.invert_x:
            dx = -dx
        if self.invert_y:
            dy = -dy
        
        # Apply sensitivity and smoothing
        dx *= self.sensitivity * self.smooth_factor
        dy *= self.sensitivity * self.smooth_factor
        
        # Determine command type
        if gesture in ['PINCH_DRAG', 'ROTATE']:
            command = 'rotate_viewport'
        elif gesture in ['V_GESTURE', 'NAVIGATE']:
            command = 'pan_viewport'
        else:
            return None
        
        # Build result
        result = {
            'command': command,
            'dx': dx,
            'dy': dy,
            'timestamp': context.timestamp
        }
        
        logger.debug(f"Viewport {command}: dx={dx:.3f}, dy={dy:.3f}")
        
        return result


def create_blender_viewport_handler(config: Dict[str, Any]) -> BlenderViewportHandler:
    """
    Factory function for creating BlenderViewportHandler.
    
    Args:
        config: Handler configuration
    
    Returns:
        BlenderViewportHandler instance
    """
    return BlenderViewportHandler(config)
