"""
Gesture Engine

Main gesture detection and processing engine with Pydantic configuration.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from typing import Optional, Dict, Any, Tuple
import time
import bpy
from bpy.types import Context
from pydantic import BaseModel, Field

from core.event_system import EventBus, Event, EventType
from core.listener import EventListener, ListenerConfig
import config
from config import AddonConfig


class EngineState(BaseModel):
    """Runtime state of the engine."""
    running: bool = False
    camera_ready: bool = False
    frame_count: int = 0
    last_frame_time: float = 0.0
    fps: float = 0.0


class GestureEngine:
    """
    Main gesture detection and processing engine.
    
    Manages camera capture, hand detection, gesture recognition,
    and event publishing to handlers.
    """
    
    def __init__(self, context: Context):
        self.context = context
        self.state = EngineState()
        
        # Components (will be initialized in start())
        self.camera: Optional[Any] = None
        self.hands: Optional[Any] = None
        self.detector: Optional[Any] = None
        self.event_bus = EventBus()
        self.listener: Optional[EventListener] = None
        
        # Handlers (will be registered with listener)
        self.viewport_handler: Optional[Any] = None
        self.animation_handler: Optional[Any] = None
        
        # Configuration
        self.config: Optional[AddonConfig] = None
        
        # FPS tracking
        self.frame_times = []
        self.max_frame_times = 30
    
    def _load_config(self) -> None:
        """Load configuration from Blender preferences into Pydantic model."""
        prefs = self.context.preferences.addons[__package__].preferences
        
        # Create Pydantic config object from preferences
        self.config = AddonConfig(
            camera={
                "index": prefs.camera_index,
                "width": 640,
                "height": 480,
                "fps": 30
            },
            sensitivity={
                "rotation": prefs.rotation_sensitivity,
                "pan": prefs.pan_sensitivity
            },
            detection={
                "frame_rate": prefs.frame_rate,
                "min_confidence": prefs.min_confidence
            },
            display={
                "show_preview": prefs.show_preview,
                "show_debug": prefs.show_debug
            },
            gestures={
                "enable_pinch": prefs.enable_pinch,
                "enable_v_gesture": prefs.enable_v_gesture,
                "enable_palm": prefs.enable_palm,
                "enable_fist": prefs.enable_fist
            }
        )
    
    def start(self) -> Tuple[bool, str]:
        """Start camera and gesture detection."""
        try:
            # Load configuration
            self._load_config()
            
            if self.config.display.show_debug:
                print("[3DX Engine] Starting gesture engine...")
            
            # Initialize camera
            from camera.capture import CameraCapture, CameraConfig
            
            camera_config = CameraConfig(**self.config.camera.dict())
            self.camera = CameraCapture(camera_config)
            
            if not self.camera.open():
                return False, "Failed to open camera"
            
            if self.config.display.show_debug:
                print(f"[3DX Engine] Camera opened: {camera_config.index}")
            
            # Initialize MediaPipe Hands
            import mediapipe as mp
            
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=self.config.detection.min_confidence,
                min_tracking_confidence=self.config.detection.min_confidence
            )
            
            if self.config.display.show_debug:
                print("[3DX Engine] MediaPipe Hands initialized")
            
            # Initialize gesture detector
            from gestures.detector import GestureDetector
            from gestures.library.basic import OpenPalmGesture, ClosedFistGesture
            from gestures.library.navigation import PinchGesture, VGesture
            
            self.detector = GestureDetector(min_confidence=self.config.detection.min_confidence)
            
            # Register enabled gestures
            if self.config.gestures.enable_pinch:
                self.detector.register(PinchGesture())
            
            if self.config.gestures.enable_v_gesture:
                self.detector.register(VGesture())
            
            if self.config.gestures.enable_palm:
                self.detector.register(OpenPalmGesture())
            
            if self.config.gestures.enable_fist:
                self.detector.register(ClosedFistGesture())
            
            if self.config.display.show_debug:
                print(f"[3DX Engine] Registered {len(self.detector.gestures)} gestures")
            
            # Initialize event listener
            listener_config = ListenerConfig(
                debug_mode=self.config.display.show_debug,
                log_events=self.config.display.show_debug
            )
            self.listener = EventListener(self.context, self.event_bus, listener_config)
            
            # Initialize and register handlers
            from handlers.viewport_handler import ViewportHandler
            from handlers.animation_handler import AnimationHandler
            from handlers.handler_base import HandlerConfig
            
            handler_config = HandlerConfig(enabled=True)
            
            self.viewport_handler = ViewportHandler(handler_config)
            self.animation_handler = AnimationHandler(handler_config)
            
            self.listener.register_handler(self.viewport_handler)
            self.listener.register_handler(self.animation_handler)
            
            # Start listener
            self.listener.start()
            
            if self.config.display.show_debug:
                print("[3DX Engine] Event listener started with handlers")
            
            # Mark as running
            self.state.running = True
            self.state.camera_ready = True
            
            return True, "Started successfully"
            
        except Exception as e:
            # Cleanup on error
            self.stop()
            return False, f"Startup error: {str(e)}"
    
    def stop(self) -> None:
        """Stop and cleanup."""
        if self.config and self.config.display.show_debug:
            print("[3DX Engine] Stopping gesture engine...")
        
        # Stop listener
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
        
        # Release MediaPipe
        if self.hands:
            self.hands.close()
            self.hands = None
        
        # Clear event bus
        self.event_bus.clear_subscribers()
        
        # Reset state
        self.state.running = False
        self.state.camera_ready = False
        self.state.frame_count = 0
        self.frame_times.clear()
        
        if self.config and self.config.display.show_debug:
            print("[3DX Engine] Stopped")
    
    def process_frame(self, context: Context) -> None:
        """
        Process one camera frame.
        
        Reads frame, detects hands, recognizes gestures, and publishes events.
        """
        if not self.state.running:
            return
        
        try:
            # Track frame time for FPS
            frame_start = time.time()
            
            # Read frame from camera
            ret, frame = self.camera.read_frame()
            
            if not ret or frame is None:
                return
            
            # Convert BGR to RGB for MediaPipe
            import cv2
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.hands.process(frame_rgb)
            
            # Update state
            state = context.scene.gesture_state
            self.state.frame_count += 1
            state.frames_processed = self.state.frame_count
            
            # Detect gestures if hands are found
            if results.multi_hand_landmarks:
                # Get first hand
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Detect gesture
                gesture_result = self.detector.detect_best(hand_landmarks.landmark, {})
                
                if gesture_result:
                    # Update UI state
                    state.last_gesture = gesture_result.name
                    state.last_confidence = gesture_result.confidence
                    state.gestures_detected += 1
                    
                    # Publish gesture event
                    event = Event(
                        type=EventType.GESTURE,
                        source="gesture_engine",
                        action=gesture_result.name,
                        data=gesture_result.data
                    )
                    self.event_bus.publish(event)
                    
                    if self.config.display.show_debug:
                        print(f"[3DX Engine] Detected: {gesture_result.name} "
                              f"({gesture_result.confidence:.2f})")
            
            # Calculate FPS
            frame_end = time.time()
            frame_time = frame_end - frame_start
            
            self.frame_times.append(frame_time)
            if len(self.frame_times) > self.max_frame_times:
                self.frame_times.pop(0)
            
            if self.frame_times:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.state.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
                state.current_fps = self.state.fps
            
        except Exception as e:
            print(f"[3DX Engine] Frame processing error: {e}")
            
            # Publish error event
            error_event = Event(
                type=EventType.ERROR,
                source="gesture_engine",
                action="processing_error",
                data={"error": str(e)}
            )
            self.event_bus.publish(error_event)

