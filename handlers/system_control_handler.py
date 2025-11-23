"""
System Control Handler - Controls system-level functions.

Handles volume, media playback, and other OS-level controls.
"""

import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.gesture_handler import GestureHandler, HandlerContext

logger = logging.getLogger(__name__)


class SystemControlHandler(GestureHandler):
    """
    Handler for system-level controls.
    
    Supports:
    - Volume control (up/down/mute)
    - Media playback (play/pause/next/previous)
    - Application switching
    - Custom system commands
    
    Configuration:
        volume_step: Volume change step size (default: 5)
        enable_media: Enable media controls (default: True)
        enable_volume: Enable volume controls (default: True)
        custom_commands: Dict of gesture -> system command mappings
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize system control handler.
        
        Args:
            config: Handler configuration
        """
        super().__init__('system_control', config)
        
        # Handler-specific settings
        self.volume_step = config.get('volume_step', 5)
        self.enable_media = config.get('enable_media', True)
        self.enable_volume = config.get('enable_volume', True)
        self.custom_commands = config.get('custom_commands', {})
        
        # Default gesture-to-action mappings
        self.action_map = config.get('action_map', {
            'OPEN_PALM': 'volumeup',
            'CLOSED_FIST': 'volumedown',
            'POINTING': 'playpause',
            'THUMBS_UP': 'next_track',
            'THUMBS_DOWN': 'previous_track',
        })
        
        logger.info(f"SystemControlHandler initialized (media={self.enable_media}, volume={self.enable_volume})")
    
    def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
        """
        Handle system control gestures.
        
        Args:
            context: Handler execution context
        
        Returns:
            System command data or None
        """
        gesture = context.gesture
        
        # Check custom commands first
        if gesture in self.custom_commands:
            return {
                'command': 'custom',
                'action': self.custom_commands[gesture],
                'timestamp': context.timestamp
            }
        
        # Check action map
        if gesture not in self.action_map:
            return None
        
        action = self.action_map[gesture]
        
        # Filter based on enabled features
        if action in ['volumeup', 'volumedown', 'mute'] and not self.enable_volume:
            return None
        
        if action in ['playpause', 'next_track', 'previous_track'] and not self.enable_media:
            return None
        
        # Build result
        result = {
            'command': 'system_action',
            'action': action,
            'timestamp': context.timestamp
        }
        
        # Add volume step for volume commands
        if action in ['volumeup', 'volumedown']:
            result['step'] = self.volume_step
        
        logger.debug(f"System control: {action}")
        
        return result


def create_system_control_handler(config: Dict[str, Any]) -> SystemControlHandler:
    """
    Factory function for creating SystemControlHandler.
    
    Args:
        config: Handler configuration
    
    Returns:
        SystemControlHandler instance
    """
    return SystemControlHandler(config)
