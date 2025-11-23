"""
Example Custom Handler - Template for creating your own gesture handlers.

This is a fully documented example showing how to create custom handlers
for your specific use cases.
"""

import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.gesture_handler import GestureHandler, HandlerContext, HandlerPriority

logger = logging.getLogger(__name__)


class ExampleCustomHandler(GestureHandler):
    """
    Example custom gesture handler.
    
    This handler demonstrates:
    - Basic gesture handling
    - Configuration management
    - State tracking
    - Custom logic implementation
    
    Configuration Example:
        handlers:
          example_custom:
            enabled: true
            priority: 50
            gestures:
              - THUMBS_UP
              - PEACE_SIGN
            cooldown: 1.0
            custom_setting: "my_value"
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize custom handler.
        
        Args:
            config: Handler configuration dictionary
        """
        # Set default gestures if not specified
        if 'gestures' not in config:
            config['gestures'] = ['THUMBS_UP', 'PEACE_SIGN']
        
        # Initialize base class
        super().__init__('example_custom', config)
        
        # Extract custom settings from config
        self.custom_setting = config.get('custom_setting', 'default_value')
        self.threshold = config.get('threshold', 0.8)
        
        # Initialize handler state
        self.activation_count = 0
        self.last_gesture = None
        
        logger.info(f"ExampleCustomHandler initialized with custom_setting={self.custom_setting}")
    
    def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
        """
        Handle gesture events.
        
        This is the main method where you implement your custom logic.
        
        Args:
            context: Handler execution context containing:
                - event: Original Event object
                - gesture: Gesture name (e.g., "THUMBS_UP")
                - data: Gesture-specific data (e.g., confidence, position)
                - timestamp: Event timestamp
                - metadata: Additional context
        
        Returns:
            Dictionary with result data, or None if gesture not handled
        """
        gesture = context.gesture
        data = context.data
        
        # Example: Check gesture confidence if available
        confidence = data.get('confidence', 1.0)
        if confidence < self.threshold:
            logger.debug(f"Gesture {gesture} below confidence threshold")
            return None
        
        # Example: Different actions for different gestures
        if gesture == 'THUMBS_UP':
            result = self._handle_thumbs_up(context)
        elif gesture == 'PEACE_SIGN':
            result = self._handle_peace_sign(context)
        else:
            # Gesture not handled by this handler
            return None
        
        # Update state
        self.activation_count += 1
        self.last_gesture = gesture
        
        logger.info(f"Custom handler processed {gesture} (count={self.activation_count})")
        
        return result
    
    def _handle_thumbs_up(self, context: HandlerContext) -> Dict[str, Any]:
        """
        Handle THUMBS_UP gesture.
        
        Example: Send a "like" action
        """
        return {
            'action': 'like',
            'custom_data': self.custom_setting,
            'timestamp': context.timestamp
        }
    
    def _handle_peace_sign(self, context: HandlerContext) -> Dict[str, Any]:
        """
        Handle PEACE_SIGN gesture.
        
        Example: Send a "peace" action with position data
        """
        # Extract position data if available
        position = context.data.get('position', {'x': 0, 'y': 0})
        
        return {
            'action': 'peace',
            'position': position,
            'timestamp': context.timestamp
        }
    
    def on_enable(self):
        """
        Called when handler is enabled.
        
        Use this to initialize resources, start timers, etc.
        """
        logger.info(f"Handler {self.name} enabled")
        # Example: Reset state when enabled
        self.activation_count = 0
    
    def on_disable(self):
        """
        Called when handler is disabled.
        
        Use this to cleanup resources, stop timers, etc.
        """
        logger.info(f"Handler {self.name} disabled (processed {self.activation_count} gestures)")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get handler metadata including custom state.
        
        Returns:
            Dictionary with handler information
        """
        metadata = super().get_metadata()
        metadata.update({
            'activation_count': self.activation_count,
            'last_gesture': self.last_gesture,
            'custom_setting': self.custom_setting
        })
        return metadata


def create_example_custom_handler(config: Dict[str, Any]) -> ExampleCustomHandler:
    """
    Factory function for creating ExampleCustomHandler.
    
    This factory function is used by the HandlerRegistry to create
    handler instances from configuration.
    
    Args:
        config: Handler configuration dictionary
    
    Returns:
        ExampleCustomHandler instance
    """
    return ExampleCustomHandler(config)


# ============================================================================
# QUICK START GUIDE
# ============================================================================
"""
To create your own custom handler:

1. Copy this file and rename it (e.g., my_handler.py)

2. Rename the class (e.g., MyCustomHandler)

3. Update the __init__ method:
   - Set your handler name: super().__init__('my_handler', config)
   - Define which gestures you want to handle
   - Extract any custom configuration

4. Implement the handle() method:
   - Add your custom logic
   - Return a result dictionary or None

5. Create a factory function:
   def create_my_handler(config):
       return MyCustomHandler(config)

6. Register your handler in the configuration (config/handler_config.yaml):
   handlers:
     my_handler:
       enabled: true
       priority: 50
       gestures:
         - MY_GESTURE
       my_custom_setting: value

7. Register the factory in your output module or orchestrator:
   registry.register_factory('my_handler', create_my_handler)

That's it! Your handler will now process the specified gestures.
"""
