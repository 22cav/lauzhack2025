"""
Gesture Handler System - Modular, plugin-based gesture handling.

This module provides the core infrastructure for creating modular gesture
handlers that can be easily added, removed, and configured.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import logging
from enum import Enum

from .event_system import Event, EventType

logger = logging.getLogger(__name__)


class HandlerPriority(Enum):
    """Handler execution priority levels."""
    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100


@dataclass
class HandlerContext:
    """
    Context passed to gesture handlers during execution.
    
    Attributes:
        event: The original gesture event
        gesture: Gesture name (e.g., "PINCH_DRAG", "OPEN_PALM")
        data: Gesture-specific data (e.g., dx/dy, confidence)
        timestamp: Event timestamp
        metadata: Additional context metadata
    """
    event: Event
    gesture: str
    data: Dict[str, Any]
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class GestureHandler(ABC):
    """
    Abstract base class for gesture handlers.
    
    Handlers process specific gestures and execute corresponding actions.
    Each handler should focus on a single responsibility (e.g., viewport
    control, animation control, system commands).
    
    Example:
        class MyHandler(GestureHandler):
            def __init__(self, config):
                super().__init__("my_handler", config)
                self.gestures = ["THUMBS_UP"]
            
            def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
                if context.gesture == "THUMBS_UP":
                    return {"action": "like"}
                return None
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize handler.
        
        Args:
            name: Unique handler identifier
            config: Handler-specific configuration
        """
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        self.priority = config.get('priority', HandlerPriority.NORMAL.value)
        self.gestures = config.get('gestures', [])
        self.cooldown = config.get('cooldown', 0.0)
        self._last_execution = 0.0
        
        logger.debug(f"Handler '{name}' initialized (priority={self.priority})")
    
    @abstractmethod
    def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
        """
        Handle a gesture event.
        
        Args:
            context: Handler execution context
        
        Returns:
            Optional result dictionary with handler-specific data,
            or None if gesture was not handled
        """
        pass
    
    def can_handle(self, gesture: str) -> bool:
        """
        Check if this handler can process the given gesture.
        
        Args:
            gesture: Gesture name to check
        
        Returns:
            True if handler supports this gesture
        """
        if not self.enabled:
            return False
        
        # Empty gestures list means handle all gestures
        if not self.gestures:
            return True
        
        return gesture in self.gestures
    
    def should_execute(self, current_time: float) -> bool:
        """
        Check if handler should execute based on cooldown.
        
        Args:
            current_time: Current timestamp
        
        Returns:
            True if cooldown period has passed
        """
        if current_time - self._last_execution >= self.cooldown:
            self._last_execution = current_time
            return True
        return False
    
    def on_enable(self):
        """Called when handler is enabled."""
        pass
    
    def on_disable(self):
        """Called when handler is disabled."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get handler metadata.
        
        Returns:
            Dictionary with handler information
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'priority': self.priority,
            'gestures': self.gestures,
            'cooldown': self.cooldown
        }


class HandlerRegistry:
    """
    Registry for managing gesture handlers.
    
    Provides registration, discovery, and retrieval of handlers.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._handlers: Dict[str, GestureHandler] = {}
        self._factories: Dict[str, Callable] = {}
        logger.debug("HandlerRegistry initialized")
    
    def register(self, handler: GestureHandler):
        """
        Register a handler instance.
        
        Args:
            handler: Handler to register
        """
        if handler.name in self._handlers:
            logger.warning(f"Handler '{handler.name}' already registered, replacing")
        
        self._handlers[handler.name] = handler
        logger.info(f"✓ Registered handler: {handler.name}")
    
    def register_factory(self, name: str, factory: Callable[[Dict[str, Any]], GestureHandler]):
        """
        Register a handler factory function.
        
        Args:
            name: Handler name
            factory: Factory function that creates handler from config
        """
        self._factories[name] = factory
        logger.debug(f"Registered factory for handler: {name}")
    
    def create_from_config(self, name: str, config: Dict[str, Any]) -> Optional[GestureHandler]:
        """
        Create and register handler from configuration.
        
        Args:
            name: Handler name
            config: Handler configuration
        
        Returns:
            Created handler instance or None if factory not found
        """
        if name not in self._factories:
            logger.error(f"No factory registered for handler: {name}")
            return None
        
        try:
            handler = self._factories[name](config)
            self.register(handler)
            return handler
        except Exception as e:
            logger.error(f"Failed to create handler '{name}': {e}")
            return None
    
    def get(self, name: str) -> Optional[GestureHandler]:
        """Get handler by name."""
        return self._handlers.get(name)
    
    def get_all(self) -> List[GestureHandler]:
        """Get all registered handlers."""
        return list(self._handlers.values())
    
    def get_for_gesture(self, gesture: str) -> List[GestureHandler]:
        """
        Get all handlers that can process a gesture.
        
        Args:
            gesture: Gesture name
        
        Returns:
            List of handlers sorted by priority (highest first)
        """
        handlers = [h for h in self._handlers.values() if h.can_handle(gesture)]
        return sorted(handlers, key=lambda h: h.priority, reverse=True)
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a handler.
        
        Args:
            name: Handler name
        
        Returns:
            True if handler was removed
        """
        if name in self._handlers:
            handler = self._handlers.pop(name)
            handler.on_disable()
            logger.info(f"Unregistered handler: {name}")
            return True
        return False
    
    def clear(self):
        """Clear all handlers."""
        for handler in self._handlers.values():
            handler.on_disable()
        self._handlers.clear()
        logger.info("Registry cleared")
    
    def list_handlers(self) -> List[str]:
        """List all registered handler names."""
        return list(self._handlers.keys())


class HandlerManager:
    """
    Manages handler execution and lifecycle.
    
    Coordinates the execution of multiple handlers for gesture events,
    respecting priority and cooldown settings.
    """
    
    def __init__(self, registry: HandlerRegistry):
        """
        Initialize handler manager.
        
        Args:
            registry: Handler registry to use
        """
        self.registry = registry
        self._execution_stats: Dict[str, int] = {}
        logger.debug("HandlerManager initialized")
    
    def process_event(self, event: Event) -> List[Dict[str, Any]]:
        """
        Process an event through all applicable handlers.
        
        Args:
            event: Event to process
        
        Returns:
            List of results from handlers that processed the event
        """
        gesture = event.action
        
        # Get handlers for this gesture
        handlers = self.registry.get_for_gesture(gesture)
        
        if not handlers:
            logger.debug(f"No handlers for gesture: {gesture}")
            return []
        
        # Create context
        context = HandlerContext(
            event=event,
            gesture=gesture,
            data=event.data,
            timestamp=event.timestamp
        )
        
        # Execute handlers
        results = []
        for handler in handlers:
            if not handler.should_execute(event.timestamp):
                logger.debug(f"Handler '{handler.name}' on cooldown")
                continue
            
            try:
                result = handler.handle(context)
                if result is not None:
                    results.append({
                        'handler': handler.name,
                        'result': result
                    })
                    
                    # Update stats
                    self._execution_stats[handler.name] = \
                        self._execution_stats.get(handler.name, 0) + 1
                    
                    logger.debug(f"Handler '{handler.name}' processed {gesture}")
            
            except Exception as e:
                logger.error(f"Handler '{handler.name}' error: {e}", exc_info=True)
        
        return results
    
    def enable_handler(self, name: str) -> bool:
        """
        Enable a handler.
        
        Args:
            name: Handler name
        
        Returns:
            True if handler was enabled
        """
        handler = self.registry.get(name)
        if handler:
            handler.enabled = True
            handler.on_enable()
            logger.info(f"Enabled handler: {name}")
            return True
        return False
    
    def disable_handler(self, name: str) -> bool:
        """
        Disable a handler.
        
        Args:
            name: Handler name
        
        Returns:
            True if handler was disabled
        """
        handler = self.registry.get(name)
        if handler:
            handler.enabled = False
            handler.on_disable()
            logger.info(f"Disabled handler: {name}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get handler execution statistics."""
        return self._execution_stats.copy()
    
    def reset_stats(self):
        """Reset execution statistics."""
        self._execution_stats.clear()
