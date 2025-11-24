"""
Event System - Central event bus for routing events between components.

Simplified version for Blender addon use with comprehensive type annotations and Pydantic validation.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

import time
from typing import Callable, Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    """Types of events that can be published."""
    GESTURE = "GESTURE"
    SYSTEM = "SYSTEM"
    ERROR = "ERROR"


class Event(BaseModel):
    """
    Event data structure with Pydantic validation.
    
    Attributes:
        type: Type of event (GESTURE, SYSTEM, ERROR)
        source: Source identifier (e.g., 'gesture_engine')
        action: Action identifier (e.g., 'OPEN_PALM', 'PINCH_DRAG')
        data: Additional context data
        timestamp: Event creation time (Unix timestamp)
    """
    type: EventType
    source: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        frozen = True  # Make events immutable
    
    def __str__(self) -> str:
        return f"Event({self.type.value}, {self.source}, {self.action})"
    
    def __repr__(self) -> str:
        return f"Event(type={self.type.value}, source='{self.source}', action='{self.action}')"


class EventBus:
    """
    Central event bus for publish-subscribe event handling.
    
    Simplified for addon use - no threading since we run in Blender's main thread.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {
            EventType.GESTURE: [],
            EventType.SYSTEM: [],
            EventType.ERROR: [],
        }
        self._event_count: int = 0
    
    def subscribe(
        self, 
        event_type: EventType, 
        callback: Callable[[Event], None],
        filter_fn: Optional[Callable[[Event], bool]] = None
    ) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            callback: Function to call when event is published
            filter_fn: Optional filter function.
        """
        if filter_fn is not None:
            wrapper = self._create_filtered_callback(callback, filter_fn)
            self._subscribers[event_type].append(wrapper)
        else:
            self._subscribers[event_type].append(callback)
    
    def _create_filtered_callback(
        self, 
        callback: Callable[[Event], None], 
        filter_fn: Callable[[Event], bool]
    ) -> Callable[[Event], None]:
        """Create a wrapped callback that applies a filter."""
        def wrapper(event: Event) -> None:
            if filter_fn(event):
                callback(event)
        return wrapper
    
    def unsubscribe(
        self, 
        event_type: EventType, 
        callback: Callable[[Event], None]
    ) -> None:
        """Unsubscribe from events."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        self._event_count += 1
        
        # Get subscribers for this event type
        subscribers = self._subscribers[event.type].copy()
        
        # Call all subscribers
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"[3DX] Error in event subscriber: {e}")
    
    def clear_subscribers(self, event_type: Optional[EventType] = None) -> None:
        """Clear all subscribers."""
        if event_type is None:
            for et in EventType:
                self._subscribers[et].clear()
        else:
            self._subscribers[event_type].clear()
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get subscriber count."""
        return len(self._subscribers[event_type])
    
    def get_total_events(self) -> int:
        """Get total event count."""
        return self._event_count
