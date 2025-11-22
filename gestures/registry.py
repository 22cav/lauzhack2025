"""
Gesture Registry for Dynamic Loading and Management

Provides a centralized registry for gesture definitions with
plugin-style loading capabilities.
"""

from typing import List, Dict, Type
import logging
from .detector import Gesture

logger = logging.getLogger(__name__)


class GestureRegistry:
    """
    Central registry for gesture definitions.
    
    Allows dynamic loading of gesture sets and provides
    metadata about available gestures.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._gestures: Dict[str, Type[Gesture]] = {}
        self._sets: Dict[str, List[str]] = {}
    
    def register_gesture(self, gesture_class: Type[Gesture], set_name: str = "default"):
        """
        Register a gesture class.
        
        Args:
            gesture_class: Gesture class to register
            set_name: Set name for grouping (e.g., "basic", "advanced")
        """
        if not issubclass(gesture_class, Gesture):
            raise TypeError(f"Expected Gesture subclass, got {gesture_class}")
        
        # Create temporary instance to get name
        temp_instance = gesture_class()
        name = temp_instance.name
        
        self._gestures[name] = gesture_class
        
        # Add to set
        if set_name not in self._sets:
            self._sets[set_name] = []
        self._sets[set_name].append(name)
        
        logger.debug(f"Registered {name} in set '{set_name}'")
    
    def get_gesture(self, name: str) -> Type[Gesture]:
        """Get gesture class by name."""
        if name not in self._gestures:
            raise KeyError(f"Gesture '{name}' not found in registry")
        return self._gestures[name]
    
    def create_gesture(self, name: str) -> Gesture:
        """Create gesture instance by name."""
        gesture_class = self.get_gesture(name)
        return gesture_class()
    
    def get_set(self, set_name: str) -> List[Gesture]:
        """
        Get all gestures in a set.
        
        Args:
            set_name: Name of the gesture set
        
        Returns:
            List of Gesture instances
        """
        if set_name not in self._sets:
            raise KeyError(f"Gesture set '{set_name}' not found")
        
        return [self.create_gesture(name) for name in self._sets[set_name]]
    
    def list_gestures(self) -> List[str]:
        """List all registered gesture names."""
        return list(self._gestures.keys())
    
    def list_sets(self) -> List[str]:
        """List all gesture set names."""
        return list(self._sets.keys())
    
    def get_metadata(self, name: str) -> Dict[str, any]:
        """Get gesture metadata."""
        gesture = self.create_gesture(name)
        return {
            'name': gesture.name,
            'priority': gesture.priority,
            'description': gesture.description,
        }
    
    def clear(self):
        """Clear all registered gestures."""
        self._gestures.clear()
        self._sets.clear()
        logger.info("Registry cleared")


# Global registry instance
_global_registry = GestureRegistry()


def get_registry() -> GestureRegistry:
    """Get the global gesture registry."""
    return _global_registry


def register(set_name: str = "default"):
    """
    Decorator for registering gesture classes.
    
    Usage:
        @register("basic")
        class OpenPalm(Gesture):
            ...
    """
    def decorator(gesture_class: Type[Gesture]):
        _global_registry.register_gesture(gesture_class, set_name)
        return gesture_class
    return decorator
