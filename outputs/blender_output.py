"""
Blender Output Module - Send gesture events to Blender for 3D manipulation.

This module translates gesture events into Blender commands for controlling
the viewport, timeline, and scene objects.
"""

import socket
import json
import logging
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.event_system import Event, EventBus, EventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlenderOutput:
    """
    Blender integration handler with modular gesture processing.
    
    Uses the handler system to process gestures through configurable
    handlers instead of hardcoded mappings.
    
    Communication Methods:
    1. Socket-based (current): Simple TCP socket for sending JSON commands
    2. Future: Blender addon with embedded gesture engine
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any], handler_manager=None):
        """
        Initialize Blender output.
        
        Args:
            event_bus: EventBus instance for subscribing to events
            config: Configuration dictionary with Blender settings
            handler_manager: Optional HandlerManager instance (created if not provided)
        """
        self.event_bus = event_bus
        self.config = config
        
        # Blender communication settings
        self.host = config.get('blender_host', 'localhost')
        self.port = config.get('blender_port', 8888)
        self.enabled = config.get('enabled', True)
        
        # Socket connection
        self.socket = None
        self.connected = False
        
        # Handler system
        self.handler_manager = handler_manager
        if self.handler_manager is None:
            # Create handler system if not provided
            self._initialize_handlers()
        
        logger.info(f"BlenderOutput initialized (Blender at {self.host}:{self.port})")
    
    def _initialize_handlers(self):
        """Initialize handler system with Blender handlers."""
        from core.gesture_handler import HandlerRegistry, HandlerManager
        from handlers.blender_viewport_handler import create_blender_viewport_handler
        from handlers.blender_animation_handler import create_blender_animation_handler
        
        # Create registry and manager
        registry = HandlerRegistry()
        
        # Register handler factories
        registry.register_factory('blender_viewport', create_blender_viewport_handler)
        registry.register_factory('blender_animation', create_blender_animation_handler)
        
        # Load handler configuration
        handler_config = self.config.get('handlers', {})
        
        # Create handlers from config
        for handler_name, handler_cfg in handler_config.items():
            if handler_cfg.get('enabled', True):
                registry.create_from_config(handler_name, handler_cfg)
        
        # Create manager
        self.handler_manager = HandlerManager(registry)
        
        logger.info(f"Initialized {len(registry.list_handlers())} handlers")
    
    def start(self):
        """Start listening to events and attempt Blender connection."""
        if not self.enabled:
            logger.info("BlenderOutput disabled in config")
            return
        
        # Subscribe to events
        self.event_bus.subscribe(EventType.GESTURE, self._handle_event)
        self.event_bus.subscribe(EventType.BUTTON, self._handle_event)
        
        # Attempt to connect to Blender
        self._connect()
        
        logger.info("BlenderOutput started")
    
    def stop(self):
        """Stop event handling and close Blender connection."""
        self._disconnect()
        logger.info("BlenderOutput stopped")
    
    def _connect(self):
        """Attempt to connect to Blender socket server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
        except (ConnectionRefusedError, OSError) as e:
            logger.warning(f"Could not connect to Blender: {e}")
            logger.warning("Blender commands will be logged but not sent.")
            self.connected = False
            self.socket = None
    
    def _disconnect(self):
        """Disconnect from Blender socket server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False
    
    def _handle_event(self, event: Event):
        """
        Handle incoming events through the handler system.
        
        Args:
            event: Event to handle
        """
        # Process event through handler system
        results = self.handler_manager.process_event(event)
        
        # Send each result to Blender
        for result in results:
            handler_name = result['handler']
            command_data = result['result']
            
            logger.debug(f"Handler '{handler_name}' produced command: {command_data.get('command')}")
            
            # Send to Blender
            self._send_command(command_data)
    
    def _send_command(self, command_data: Dict[str, Any]):
        """
        Send command to Blender.
        
        Args:
            command_data: Command dictionary to send as JSON
        """
        json_data = json.dumps(command_data)
        logger.info(f"Blender command: {json_data}")
        
        if not self.connected:
            logger.debug("Not connected to Blender - command not sent")
            return
        
        try:
            message = (json_data + '\n').encode('utf-8')
            self.socket.sendall(message)
        except (BrokenPipeError, OSError) as e:
            logger.error(f"Error sending to Blender: {e}")
            self._disconnect()
            # Try to reconnect
            self._connect()


# Blender addon helper script that would run inside Blender
BLENDER_ADDON_TEMPLATE = '''
"""
Blender Gesture Control Listener
Install this as a Blender addon to receive gesture commands.
"""

import bpy
import socket
import threading
import json

class GestureListener(bpy.types.Operator):
    bl_idname = "view3d.gesture_listener"
    bl_label = "Gesture Control Listener"
    
    _timer = None
    _socket = None
    _thread = None
    _running = False
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            # Process any received commands
            pass
        
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        
        # Start socket listener thread
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()
        
        return {'RUNNING_MODAL'}
    
    def _listen(self):
        """Listen for gesture commands on port 8888."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 8888))
        server.listen(1)
        
        while self._running:
            try:
                client, addr = server.accept()
                while self._running:
                    data = client.recv(1024)
                    if not data:
                        break
                    
                    # Parse command
                    command = json.loads(data.decode('utf-8'))
                    self._execute_command(command)
            except:
                pass
    
    def _execute_command(self, command):
        """Execute Blender command from gesture."""
        cmd_type = command.get('command')
        
        if cmd_type == 'viewport_rotate':
            rotation = command.get('rotation', {})
            # Rotate viewport (requires bpy context manipulation)
            pass
        elif cmd_type == 'play_animation':
            bpy.ops.screen.animation_play()
        elif cmd_type == 'pause_animation':
            bpy.ops.screen.animation_cancel()
        elif cmd_type == 'toggle_edit_mode':
            bpy.ops.object.mode_set(mode='EDIT' if bpy.context.mode == 'OBJECT' else 'OBJECT')

def register():
    bpy.utils.register_class(GestureListener)

def unregister():
    bpy.utils.unregister_class(GestureListener)
'''
