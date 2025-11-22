# tests/test_outputs.py
"""Tests for output modules (BlenderOutput and LoupedeckOutput).

These tests mock the socket communication to verify that gestures are sent
correctly according to the configured mappings and that graceful handling
occurs when the socket cannot connect.
"""

import unittest
from unittest.mock import patch, MagicMock

# Import the output classes
from outputs.blender_output import BlenderOutput
from outputs.loupedeck_output import LoupedeckOutput
from core.event_system import EventBus, Event, EventType

class TestBlenderOutput(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.config = {
            "blender_host": "localhost",
            "blender_port": 8888,
            "enabled": True,
            "mappings": {
                "PINCH_DRAG": "viewport_rotate",
                "OPEN_PALM": "play_animation"
            }
        }
        self.blender = BlenderOutput(self.event_bus, self.config)

    @patch('socket.socket')
    def test_send_mapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        # Simulate successful connection
        self.blender._connect()
        # Publish a mapped gesture event
        event = Event(type=EventType.GESTURE, source="test", action="OPEN_PALM")
        self.blender._handle_event(event)
        # Verify that sendall was called with JSON containing the command
        expected_json = {"command": "play_animation", "timestamp": event.timestamp}
        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0]
        self.assertIn(b'play_animation', sent_data)

    @patch('socket.socket')
    def test_ignore_unmapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        self.blender._connect()
        event = Event(type=EventType.GESTURE, source="test", action="UNKNOWN_GESTURE")
        self.blender._handle_event(event)
        mock_socket.sendall.assert_not_called()

    @patch('socket.socket', side_effect=ConnectionRefusedError)
    def test_connection_failure(self, mock_socket_cls):
        # Connection should fail gracefully and not raise
        self.blender._connect()
        self.assertFalse(self.blender.connected)

class TestLoupedeckOutput(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.config = {
            "loupedeck_host": "localhost",
            "loupedeck_port": 5000,
            "enabled": True,
            "mappings": {
                "OPEN_PALM": "OPEN_PALM",
                "CLOSED_FIST": "CLOSED_FIST"
            }
        }
        self.loupedeck = LoupedeckOutput(self.event_bus, self.config)

    @patch('socket.socket')
    def test_send_mapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        self.loupedeck._connect()
        event = Event(type=EventType.GESTURE, source="test", action="CLOSED_FIST")
        self.loupedeck._handle_gesture(event)
        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0]
        self.assertTrue(sent_data.startswith(b'CLOSED_FIST'))

    @patch('socket.socket')
    def test_ignore_unmapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        self.loupedeck._connect()
        event = Event(type=EventType.GESTURE, source="test", action="UNKNOWN")
        self.loupedeck._handle_gesture(event)
        mock_socket.sendall.assert_not_called()

    @patch('socket.socket', side_effect=ConnectionRefusedError)
    def test_connection_failure(self, mock_socket_cls):
        self.loupedeck._connect()
        self.assertFalse(self.loupedeck.connected)

if __name__ == "__main__":
    unittest.main()
