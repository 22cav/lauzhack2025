"""
Event System - Central event bus for routing events between inputs and outputs.

This module provides a publish-subscribe event system that decouples input sources
(gesture recognition, button presses) from output handlers (Blender, system actions).
"""

import time
import threading
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can be published."""
    GESTURE = "GESTURE"
    BUTTON = "BUTTON"
    SYSTEM = "SYSTEM"


@dataclass
class Event:
    """
    Event data structure.
    
    Attributes:
        type: Type of event (GESTURE, BUTTON, SYSTEM)
        source: Source identifier (e.g., 'gesture_engine', 'mx_console')
        action: Action identifier (e.g., 'OPEN_PALM', 'BUTTON_1_PRESS')
        data: Additional context data (optional)
        timestamp: Event creation time (Unix timestamp)
    """
    type: EventType
    source: str
    action: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def __str__(self):
        return f"Event({self.type.value}, {self.source}, {self.action}, {self.data})"


class EventBus:
    """
    Central event bus for publish-subscribe event handling.
    
    Thread-safe event bus that allows components to publish events and subscribe
    to events based on type and optional filtering criteria.
    
    Example:
        bus = EventBus()
        
        # Subscribe to all gesture events
        def on_gesture(event):
            print(f"Gesture: {event.action}")
        
        bus.subscribe(EventType.GESTURE, on_gesture)
        
        # Publish an event
        event = Event(
            type=EventType.GESTURE,
            source="gesture_engine",
            action="OPEN_PALM"
        )
        bus.publish(event)
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EventType, List[Callable]] = {
            EventType.GESTURE: [],
            EventType.BUTTON: [],
            EventType.SYSTEM: []
        }
        self._lock = threading.Lock()
        self._event_count = 0
        
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None],
                  filter_fn: Optional[Callable[[Event], bool]] = None) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            callback: Function to call when event is published
            filter_fn: Optional filter function. If provided, callback is only
                      called if filter_fn(event) returns True
        """
        with self._lock:
            wrapper = callback if filter_fn is None else self._create_filtered_callback(callback, filter_fn)
            self._subscribers[event_type].append(wrapper)
            logger.info(f"Subscribed to {event_type.value} events")
    
    def _create_filtered_callback(self, callback: Callable, filter_fn: Callable) -> Callable:
        """Create a wrapped callback that applies a filter."""
        def wrapper(event: Event):
            if filter_fn(event):
                callback(event)
        return wrapper
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Type of events to unsubscribe from
            callback: The callback function to remove
        """
        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logger.info(f"Unsubscribed from {event_type.value} events")
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        with self._lock:
            self._event_count += 1
            event_id = self._event_count
            subscribers = self._subscribers[event.type].copy()
        
        logger.debug(f"Publishing event #{event_id}: {event}")
        
        # Call subscribers outside of lock to prevent deadlock
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}", exc_info=True)
    
    def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously (non-blocking).
        
        Args:
            event: Event to publish
        """
        thread = threading.Thread(target=self.publish, args=(event,), daemon=True)
        thread.start()
    
    def clear_subscribers(self, event_type: Optional[EventType] = None) -> None:
        """
        Clear all subscribers for a specific event type or all types.
        
        Args:
            event_type: Type to clear, or None to clear all types
        """
        with self._lock:
            if event_type is None:
                for et in EventType:
                    self._subscribers[et].clear()
                logger.info("Cleared all subscribers")
            else:
                self._subscribers[event_type].clear()
                logger.info(f"Cleared {event_type.value} subscribers")
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """
        Get the number of subscribers for an event type.
        
        Args:
            event_type: Type to check
            
        Returns:
            Number of subscribers
        """
        with self._lock:
            return len(self._subscribers[event_type])
    
    def get_total_events(self) -> int:
        """
        Get the total number of events published.
        
        Returns:
            Total event count
        """
        return self._event_count
