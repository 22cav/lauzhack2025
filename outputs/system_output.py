"""
System Output Module - Execute system-level actions (volume, media controls, etc.).

This module translates events into system actions using pyautogui,
maintaining the functionality from the original standalone script.
"""

import time
import logging
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.event_system import Event, EventBus, EventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui not installed. System actions disabled. Install with: pip install pyautogui")


class SystemOutput:
    """
    System-level action handler.
    
    Subscribes to gesture and button events and executes system actions
    like volume control, media playback, and keyboard shortcuts.
    
    Example mappings:
    - OPEN_PALM → Volume up
    - CLOSED_FIST → Volume down
    - POINTING → Play/pause media
    - BUTTON_1_PRESS → Volume up
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        """
        Initialize system output.
        
        Args:
            event_bus: EventBus instance for subscribing to events
            config: Configuration dictionary with action mappings
        """
        self.event_bus = event_bus
        self.config = config
        
        # Settings
        self.enabled = config.get('enabled', True)
        self.cooldown = config.get('cooldown', 1.0)  # Seconds between actions
        
        # Event mappings (from config)
        self.mappings = config.get('mappings', {
            'OPEN_PALM': 'volumeup',
            'CLOSED_FIST': 'volumedown',
            'POINTING': 'playpause',
            'BUTTON_1_PRESS': 'volumeup',
            'BUTTON_2_PRESS': 'volumedown',
            'BUTTON_3_PRESS': 'playpause'
        })
        
        # State
        self.last_action_time = 0
        
        if not PYAUTOGUI_AVAILABLE:
            logger.error("Cannot initialize SystemOutput: pyautogui not available")
            return
        
        logger.info("SystemOutput initialized")
    
    def start(self):
        """Start listening to events."""
        if not self.enabled:
            logger.info("SystemOutput disabled in config")
            return
        
        if not PYAUTOGUI_AVAILABLE:
            logger.error("Cannot start SystemOutput: pyautogui not available")
            return
        
        # Subscribe to gesture and button events
        self.event_bus.subscribe(EventType.GESTURE, self._handle_event)
        self.event_bus.subscribe(EventType.BUTTON, self._handle_event)
        
        logger.info("SystemOutput started")
    
    def stop(self):
        """Stop event handling."""
        logger.info("SystemOutput stopped")
    
    def _handle_event(self, event: Event):
        """
        Handle incoming events and execute system actions.
        
        Args:
            event: Event to handle
        """
        action = event.action
        
        # Ignore PINCH_DRAG and other continuous gestures
        if action in ['PINCH_DRAG', 'PINCH_START', 'PINCH_RELEASE', 'UNKNOWN']:
            return
        
        # Check if we have a mapping for this action
        if action not in self.mappings:
            return
        
        # Apply cooldown
        current_time = time.time()
        if current_time - self.last_action_time < self.cooldown:
            return
        
        # Execute action
        system_action = self.mappings[action]
        self._execute_action(system_action)
        
        self.last_action_time = current_time
    
    def _execute_action(self, action: str):
        """
        Execute a system action.
        
        Args:
            action: Action string (pyautogui key name or hotkey combo)
        """
        if not PYAUTOGUI_AVAILABLE:
            return
        
        try:
            # Check if it's a hotkey combo (e.g., "command+c")
            if '+' in action:
                keys = action.split('+')
                pyautogui.hotkey(*keys)
                logger.info(f"🎹 System action: {action}")
            else:
                # Single key press
                pyautogui.press(action)
                
                # Log with emoji based on action type
                emoji = '🔊'
                if 'volume' in action:
                    emoji = '🔊' if 'up' in action else '🔉'
                elif 'play' in action:
                    emoji = '⏯️'
                elif 'next' in action:
                    emoji = '⏭️'
                elif 'prev' in action:
                    emoji = '⏮️'
                
                logger.info(f"{emoji} System action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing system action '{action}': {e}")
