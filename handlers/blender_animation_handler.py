"""
Blender Animation Handler - Controls Blender animation playback.

Handles play, pause, stop, and frame navigation gestures.
"""

import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.gesture_handler import GestureHandler, HandlerContext

logger = logging.getLogger(__name__)


class BlenderAnimationHandler(GestureHandler):
    """
    Handler for Blender animation control.
    
    Supports:
    - OPEN_PALM / PLAY: Play animation
    - CLOSED_FIST / STOP: Stop animation
    - POINTING: Next frame
    - Future: Frame scrubbing, timeline control
    
    Configuration:
        auto_loop: Enable animation looping (default: True)
        frame_step: Number of frames to skip with POINTING (default: 1)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize animation handler.
        
        Args:
            config: Handler configuration
        """
        # Set default gestures if not specified
        if 'gestures' not in config:
            config['gestures'] = ['OPEN_PALM', 'PLAY', 'CLOSED_FIST', 'STOP', 'POINTING']
        
        super().__init__('blender_animation', config)
        
        # Handler-specific settings
        self.auto_loop = config.get('auto_loop', True)
        self.frame_step = config.get('frame_step', 1)
        
        # State tracking
        self.is_playing = False
        
        logger.info(f"BlenderAnimationHandler initialized (auto_loop={self.auto_loop})")
    
    def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
        """
        Handle animation control gestures.
        
        Args:
            context: Handler execution context
        
        Returns:
            Command data for Blender or None
        """
        gesture = context.gesture
        
        # Determine command
        command = None
        extra_data = {}
        
        if gesture in ['OPEN_PALM', 'PLAY']:
            command = 'play_animation'
            self.is_playing = True
            extra_data['loop'] = self.auto_loop
            
        elif gesture in ['CLOSED_FIST', 'STOP']:
            command = 'stop_animation'
            self.is_playing = False
            
        elif gesture == 'POINTING':
            command = 'next_frame'
            extra_data['step'] = self.frame_step
        
        if command is None:
            return None
        
        # Build result
        result = {
            'command': command,
            'timestamp': context.timestamp,
            **extra_data
        }
        
        logger.debug(f"Animation control: {command}")
        
        return result
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get handler metadata including state."""
        metadata = super().get_metadata()
        metadata['is_playing'] = self.is_playing
        return metadata


def create_blender_animation_handler(config: Dict[str, Any]) -> BlenderAnimationHandler:
    """
    Factory function for creating BlenderAnimationHandler.
    
    Args:
        config: Handler configuration
    
    Returns:
        BlenderAnimationHandler instance
    """
    return BlenderAnimationHandler(config)
