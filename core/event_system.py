"""
Event System - Central event bus for routing events between components.

Simplified version for Blender addon use with comprehensive type annotations.
"""

import time
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class EventType(str, Enum):
    """Types of events that can be published."""
    GESTURE = "GESTURE"
    SYSTEM = "SYSTEM"
    ERROR = "ERROR"


@dataclass
class Event:
    """Event data structure."""
    type: EventType
    source: str
    action: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        if not isinstance(self.type, EventType):
            raise TypeError(f"type must be EventType, got {type(self.type)}")


class EventBus:
    """Central event bus for publish-subscribe event handling."""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {
            EventType.GESTURE: [],
            EventType.SYSTEM: [],
            EventType.ERROR: [],
        }
        self._event_count: int = 0
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        self._subscribers[event_type].append(callback)
    
    def publish(self, event: Event) -> None:
        self._event_count += 1
        subscribers = self._subscribers[event.type].copy()
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"[3DX] Error in event subscriber: {e}")
