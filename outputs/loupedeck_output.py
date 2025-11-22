"""
Loupedeck Output Module - Send events to C# Loupedeck plugin via WebSocket.

This module maintains backward compatibility with the existing C# plugin
by acting as a WebSocket client that sends gesture messages.
"""

import socket
import time
import logging
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.event_system import Event, EventBus, EventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoupedeckOutput:
    """
    Loupedeck/Logitech plugin output handler.
    
    Subscribes to gesture events and sends them to the C# plugin via TCP socket.
    Maintains the existing protocol: plain text gesture names with newline terminator.
    
    This provides backward compatibility with the existing GestureServer.cs implementation.
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        """
        Initialize Loupedeck output.
        
        Args:
            event_bus: EventBus instance for subscribing to events
            config: Configuration dictionary with connection settings
        """
        self.event_bus = event_bus
        self.config = config
        
        # Connection settings
        self.host = config.get('loupedeck_host', 'localhost')
        self.port = config.get('loupedeck_port', 5000)
        self.enabled = config.get('enabled', True)
        
        # Event mappings (gesture action -> message)
        self.mappings = config.get('mappings', {
            'OPEN_PALM': 'OPEN_PALM',
            'CLOSED_FIST': 'CLOSED_FIST',
            'POINTING': 'POINTING'
        })
        
        # Socket connection
        self.socket = None
        self.connected = False
        
        logger.info(f"LoupedeckOutput initialized (C# plugin at {self.host}:{self.port})")
    
    def start(self):
        """Start listening to events and connect to C# plugin."""
        if not self.enabled:
            logger.info("LoupedeckOutput disabled in config")
            return
        
        # Subscribe only to gesture events (C# plugin expects gestures)
        self.event_bus.subscribe(EventType.GESTURE, self._handle_gesture)
        
        # Connect to C# plugin server
        self._connect()
        
        logger.info("LoupedeckOutput started")
    
    def stop(self):
        """Stop event handling and close connection."""
        self._disconnect()
        logger.info("LoupedeckOutput stopped")
    
    def _connect(self):
        """Connect to C# plugin WebSocket server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to C# plugin at {self.host}:{self.port}")
        except ConnectionRefusedError:
            logger.warning(f"Could not connect to C# plugin at {self.host}:{self.port}")
            logger.warning("Running in offline mode - gestures will not be sent to Loupedeck")
            self.connected = False
            self.socket = None
        except Exception as e:
            logger.error(f"Socket error: {e}")
            self.connected = False
            self.socket = None
    
    def _disconnect(self):
        """Disconnect from C# plugin server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False
    
    def _handle_gesture(self, event: Event):
        """
        Handle gesture events and send to C# plugin.
        
        Args:
            event: Gesture event
        """
        action = event.action
        
        # Only send mapped gestures
        if action not in self.mappings:
            return
        
        message = self.mappings[action]
        self._send_message(message)
    
    def _send_message(self, message: str):
        """
        Send message to C# plugin.
        
        Args:
            message: Message string (gesture name)
        """
        if not self.connected:
            return
        
        try:
            data = f"{message}\n".encode('utf-8')
            self.socket.sendall(data)
            logger.info(f"Sent to Loupedeck: {message}")
        except Exception as e:
            logger.error(f"Error sending to C# plugin: {e}")
            self._disconnect()
            # Try to reconnect
            time.sleep(1)
            self._connect()
