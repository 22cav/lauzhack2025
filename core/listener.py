"""
Event Listener Service

Subscribes to the event bus and routes gesture events to appropriate handlers.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from typing import List, Dict, Any, Optional
from bpy.types import Context
from pydantic import BaseModel, Field

from core.event_system import EventBus, Event, EventType
from handlers.handler_base import BaseHandler
import config


class ListenerConfig(BaseModel):
    """Configuration for the event listener."""
    debug_mode: bool = False
    log_events: bool = False


class EventListener:
    """
    Event listener that subscribes to the event bus and routes events to handlers.
    
    This service acts as the central dispatcher between the gesture detection system
    and the Blender manipulation handlers.
    """
    
    def __init__(self, context: Context, event_bus: EventBus, config: Optional[ListenerConfig] = None):
        """
        Initialize the event listener.
        
        Args:
            context: Blender context
            event_bus: Event bus to subscribe to
            config: Listener configuration
        """
        self.context = context
        self.event_bus = event_bus
        self.config = config or ListenerConfig()
        
        self.handlers: List[BaseHandler] = []
        self._subscribed = False
        
        # Statistics
        self.events_processed = 0
        self.events_handled = 0
        self.events_failed = 0
    
    def register_handler(self, handler: BaseHandler) -> None:
        """
        Register a gesture handler.
        
        Args:
            handler: Handler instance to register
        """
        if handler not in self.handlers:
            self.handlers.append(handler)
            if self.config.debug_mode:
                print(f"[3DX Listener] Registered handler: {type(handler).__name__}")
    
    def unregister_handler(self, handler: BaseHandler) -> None:
        """
        Unregister a gesture handler.
        
        Args:
            handler: Handler instance to unregister
        """
        if handler in self.handlers:
            self.handlers.remove(handler)
            if self.config.debug_mode:
                print(f"[3DX Listener] Unregistered handler: {type(handler).__name__}")
    
    def start(self) -> None:
        """
        Start listening to events by subscribing to the event bus.
        """
        if self._subscribed:
            return
        
        # Subscribe to gesture events
        self.event_bus.subscribe(
            EventType.GESTURE,
            self._handle_gesture_event
        )
        
        # Subscribe to system events
        self.event_bus.subscribe(
            EventType.SYSTEM,
            self._handle_system_event
        )
        
        # Subscribe to error events
        self.event_bus.subscribe(
            EventType.ERROR,
            self._handle_error_event
        )
        
        self._subscribed = True
        
        if self.config.debug_mode:
            print("[3DX Listener] Started listening to events")
    
    def stop(self) -> None:
        """
        Stop listening to events by unsubscribing from the event bus.
        """
        if not self._subscribed:
            return
        
        # Unsubscribe from all events
        self.event_bus.clear_subscribers(EventType.GESTURE)
        self.event_bus.clear_subscribers(EventType.SYSTEM)
        self.event_bus.clear_subscribers(EventType.ERROR)
        
        self._subscribed = False
        
        if self.config.debug_mode:
            print(f"[3DX Listener] Stopped listening. Stats: {self.events_processed} processed, "
                  f"{self.events_handled} handled, {self.events_failed} failed")
    
    def _handle_gesture_event(self, event: Event) -> None:
        """
        Handle a gesture event by routing it to appropriate handlers.
        
        Args:
            event: Gesture event to handle
        """
        self.events_processed += 1
        
        if self.config.log_events:
            print(f"[3DX Listener] Gesture event: {event.action}")
        
        # Find handlers that can handle this gesture
        handled = False
        for handler in self.handlers:
            try:
                if handler.can_handle(event.action):
                    # Handler will validate data with pydantic
                    handler.handle(self.context, event.action, event.data)
                    handled = True
                    
                    if self.config.debug_mode:
                        print(f"[3DX Listener] Handler {type(handler).__name__} handled {event.action}")
                        
            except Exception as e:
                self.events_failed += 1
                print(f"[3DX Listener] Error in handler {type(handler).__name__}: {e}")
                
                # Publish error event back to bus
                error_event = Event(
                    type=EventType.ERROR,
                    source="listener",
                    action="handler_error",
                    data={
                        "handler": type(handler).__name__,
                        "gesture": event.action,
                        "error": str(e)
                    }
                )
                self.event_bus.publish(error_event)
        
        if handled:
            self.events_handled += 1
        elif self.config.debug_mode:
            print(f"[3DX Listener] No handler found for gesture: {event.action}")
    
    def _handle_system_event(self, event: Event) -> None:
        """
        Handle a system event.
        
        Args:
            event: System event to handle
        """
        self.events_processed += 1
        
        if self.config.log_events:
            print(f"[3DX Listener] System event: {event.action}")
        
        # Handle system events (e.g., pause, resume, reset)
        if event.action == "pause":
            self._on_pause()
        elif event.action == "resume":
            self._on_resume()
        elif event.action == "reset":
            self._on_reset()
    
    def _handle_error_event(self, event: Event) -> None:
        """
        Handle an error event.
        
        Args:
            event: Error event to handle
        """
        self.events_processed += 1
        
        # Log errors
        print(f"[3DX Listener] Error event from {event.source}: {event.data.get('error', 'Unknown error')}")
    
    def _on_pause(self) -> None:
        """Handle pause system event."""
        if self.config.debug_mode:
            print("[3DX Listener] System paused")
    
    def _on_resume(self) -> None:
        """Handle resume system event."""
        if self.config.debug_mode:
            print("[3DX Listener] System resumed")
    
    def _on_reset(self) -> None:
        """Handle reset system event."""
        self.events_processed = 0
        self.events_handled = 0
        self.events_failed = 0
        
        if self.config.debug_mode:
            print("[3DX Listener] Statistics reset")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get listener statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "events_processed": self.events_processed,
            "events_handled": self.events_handled,
            "events_failed": self.events_failed,
            "handlers_registered": len(self.handlers)
        }
