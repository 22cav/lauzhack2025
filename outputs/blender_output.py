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
sys.path.append('/Users/matte/MDS/Personal/lauzhack')

from core.event_system import Event, EventBus, EventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlenderOutput:
    """
    Blender integration handler.
    
    Subscribes to gesture and button events and sends commands to Blender
    for viewport manipulation, animation control, and object interaction.
    
    Communication Methods:
    1. Socket-based (current): Simple TCP socket for sending JSON commands
    2. Future: Blender addon with embedded gesture engine
    
    Example mappings:
    - PINCH_DRAG → Rotate viewport
    - OPEN_PALM → Play animation
    - CLOSED_FIST → Pause animation
    - POINTING → Select object
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        """
        Initialize Blender output.
        
        Args:
            event_bus: EventBus instance for subscribing to events
            config: Configuration dictionary with Blender settings
        """
        self.event_bus = event_bus
        self.config = config
        
        # Blender communication settings
        self.host = config.get('blender_host', 'localhost')
        self.port = config.get('blender_port', 8888)
        self.enabled = config.get('enabled', True)
        
        # Event mappings (from config)
        self.mappings = config.get('mappings', {
            'PINCH_DRAG': 'viewport_rotate',
            'OPEN_PALM': 'play_animation',
            'CLOSED_FIST': 'pause_animation',
            'POINTING': 'next_frame',
            'BUTTON_1_PRESS': 'toggle_edit_mode'
        })
        
        # Socket connection
        self.socket = None
        self.connected = False
        
        # Drag state for smooth viewport control
        self.drag_sensitivity = config.get('drag_sensitivity', 100.0)
        
        logger.info(f"BlenderOutput initialized (Blender at {self.host}:{self.port})")
    
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
        Handle incoming events and translate to Blender commands.
        
        Args:
            event: Event to handle
        """
        action = event.action
        
        # Check if we have a mapping for this action
        if action not in self.mappings:
            return
        
        blender_command = self.mappings[action]
        
        # Build command data
        command_data = {
            'command': blender_command,
            'timestamp': event.timestamp
        }
        
        # Add event-specific data
        if action == 'PINCH_DRAG':
            # Viewport rotation based on hand movement
            delta = event.data.get('delta', {})
            command_data['rotation'] = {
                'x': delta.get('dy', 0) * self.drag_sensitivity,  # Vertical mouse = X axis rotation
                'y': delta.get('dx', 0) * self.drag_sensitivity   # Horizontal mouse = Y axis rotation
            }
        elif action.startswith('BUTTON_'):
            # Pass button data
            command_data['button_id'] = event.data.get('button_id')
        
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
