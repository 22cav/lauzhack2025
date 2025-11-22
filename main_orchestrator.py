#!/usr/bin/env python3
"""
Main Orchestrator - Entry point for the multi-input gesture control system.

This script loads configuration, initializes the EventBus, and starts all
configured input and output modules.

Usage:
    python main_orchestrator.py [--config CONFIG_FILE]

Example:
    python main_orchestrator.py --config config/event_mappings.yaml
    python main_orchestrator.py --config config/blender_mode.yaml
"""

import argparse
import os
import signal
import sys
import time
import logging
import yaml
import platform
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.event_system import EventBus
# NOTE: inputs/outputs import cv2/mediapipe at module import time. We will
# import those modules later in main() after parsing args so we can set
# OPENCV_AVFOUNDATION_SKIP_AUTH before OpenCV loads (macOS specific).

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GestureControlOrchestrator:
    """
    Main orchestrator for the gesture control system.
    
    Manages the lifecycle of all input and output modules based on
    configuration file.
    """
    
    def __init__(self, config_path: str, camera_index_override: int = None):
        """
        Initialize orchestrator.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        # Optional override from CLI to pick a different camera than what's in YAML
        self.camera_index_override = camera_index_override

        # Core event bus
        self.event_bus = EventBus()

        # Module lists
        self.inputs = []
        self.outputs = []
        
        # Main thread gesture input (macOS)
        self.main_thread_gesture_input = None

        # Shutdown flag
        self.running = False
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration: {e}")
            sys.exit(1)
    
    def _initialize_inputs(self):
        """Initialize input modules based on configuration."""
        inputs_config = self.config.get('inputs', {})
        
        # Gesture input
        gesture_config = inputs_config.get('gesture', {})
        # If CLI override provided, inject it into the gesture config
        if self.camera_index_override is not None:
            gesture_config = dict(gesture_config)  # copy to avoid mutating loaded config
            gesture_config['camera_index'] = self.camera_index_override

        if gesture_config.get('enabled', False):
            try:
                # Platform-aware gesture input
                is_macos = platform.system() == "Darwin"
                show_preview = gesture_config.get('show_preview', True)
                use_production = gesture_config.get('use_production', True)
                
                if use_production:
                    # Use new production system with auto-detection
                    from inputs.gesture_input_production import create_gesture_input
                    gesture_input = create_gesture_input(self.event_bus, gesture_config)
                    
                    # Check if it's main-thread mode (macOS)
                    if hasattr(gesture_input, 'update'):
                        self.main_thread_gesture_input = gesture_input
                        logger.info("✓ Gesture input initialized (macOS main-thread mode)")
                    else:
                        self.inputs.append(gesture_input)
                        logger.info("✓ Gesture input initialized (threaded mode)")
                else:
                    # Legacy system (GestureInput is imported in main())
                    gesture_input = GestureInput(self.event_bus, gesture_config)
                    self.inputs.append(gesture_input)
                    logger.info("✓ Gesture input initialized (legacy)")
                    
            except Exception as e:
                logger.error(f"Failed to initialize gesture input: {e}")
                import traceback
                traceback.print_exc()
        
        # MX Console input
        mx_config = inputs_config.get('mx_console', {})
        if mx_config.get('enabled', False):
            try:
                mx_input = MXConsoleInput(self.event_bus, mx_config)
                self.inputs.append(mx_input)
                logger.info("✓ MX Console input initialized")
            except Exception as e:
                logger.error(f"Failed to initialize MX Console input: {e}")
    
    def _initialize_outputs(self):
        """Initialize output modules based on configuration."""
        outputs_config = self.config.get('outputs', {})
        
        # Blender output
        blender_config = outputs_config.get('blender', {})
        if blender_config.get('enabled', False):
            try:
                blender_output = BlenderOutput(self.event_bus, blender_config)
                self.outputs.append(blender_output)
                logger.info("✓ Blender output initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Blender output: {e}")
        
        # Loupedeck output
        loupedeck_config = outputs_config.get('loupedeck', {})
        if loupedeck_config.get('enabled', False):
            try:
                loupedeck_output = LoupedeckOutput(self.event_bus, loupedeck_config)
                self.outputs.append(loupedeck_output)
                logger.info("✓ Loupedeck output initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Loupedeck output: {e}")
        
        # System output
        system_config = outputs_config.get('system', {})
        if system_config.get('enabled', False):
            try:
                system_output = SystemOutput(self.event_bus, system_config)
                self.outputs.append(system_output)
                logger.info("✓ System output initialized")
            except Exception as e:
                logger.error(f"Failed to initialize system output: {e}")
    
    def start(self):
        """Start all modules."""
        logger.info("=" * 60)
        logger.info("🎮 Gesture Control System Starting")
        logger.info("=" * 60)
        
        # Initialize modules
        self._initialize_inputs()
        self._initialize_outputs()
        
        # Start all inputs
        logger.info("\n📥 Starting input modules...")
        for inp in self.inputs:
            try:
                inp.start()
            except Exception as e:
                logger.error(f"Failed to start input: {e}")
        
        # Start main-thread gesture input if present
        if self.main_thread_gesture_input:
            try:
                self.main_thread_gesture_input.start()
            except Exception as e:
                logger.error(f"Failed to start main-thread gesture input: {e}")
        
        # Start all outputs
        logger.info("\n📤 Starting output modules...")
        for out in self.outputs:
            try:
                out.start()
            except Exception as e:
                logger.error(f"Failed to start output: {e}")
        
        self.running = True
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ System running")
        logger.info("⌨️  Press Ctrl+C to exit")
        logger.info("=" * 60 + "\n")
    
    def stop(self):
        """Stop all modules."""
        logger.info("\n🛑 Shutting down...")
        
        self.running = False
        
        # Stop all inputs
        for inp in self.inputs:
            try:
                inp.stop()
            except Exception as e:
                logger.error(f"Error stopping input: {e}")
        
        # Stop all outputs
        for out in self.outputs:
            try:
                out.stop()
            except Exception as e:
                logger.error(f"Error stopping output: {e}")
        
        logger.info("✓ Shutdown complete")
    
    def run(self):
        """Run the orchestrator (blocking)."""
        # Start system
        self.start()
        
        # Run until interrupted
        try:
            if self.main_thread_gesture_input:
                # macOS main-thread mode: call update() in loop
                logger.info("Running in main-thread mode (macOS)")
                import cv2
                while self.running:
                    if not self.main_thread_gesture_input.update():
                        break  # User pressed ESC or error
                    time.sleep(0.001)  # Minimal sleep
            else:
                # Standard threaded mode
                while self.running:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("\nReceived keyboard interrupt")
        finally:
            self.stop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gesture Control System - Multi-input event orchestrator"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/event_mappings.yaml',
        help='Path to configuration file (default: config/event_mappings.yaml)'
    )
    parser.add_argument(
        '--camera-index',
        type=int,
        default=None,
        help='Optional: override the gesture input camera index from the config (e.g. 0,1,2)'
    )
    parser.add_argument(
        '--skip-avfound-auth',
        action='store_true',
        help='Set OPENCV_AVFOUNDATION_SKIP_AUTH=1 before loading OpenCV (macOS)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    # If requested, set the OpenCV AVFoundation auth-skip env var before importing
    # any module that may import OpenCV (cv2). This must happen here, early.
    if args.skip_avfound_auth:
        os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'

    if args.debug:
        # raise logging level to DEBUG for all loggers
        logging.getLogger().setLevel(logging.DEBUG)

    # Import input/output modules now that OPENCV env var is set (if any).
    # Assign into module globals so other classes (defined above) can reference
    # the symbols by name.
    from inputs.gesture_input import GestureInput as _GestureInput
    from inputs.mx_console_input import MXConsoleInput as _MXConsoleInput
    from outputs.blender_output import BlenderOutput as _BlenderOutput
    from outputs.loupedeck_output import LoupedeckOutput as _LoupedeckOutput
    from outputs.system_output import SystemOutput as _SystemOutput
    globals()['GestureInput'] = _GestureInput
    globals()['MXConsoleInput'] = _MXConsoleInput
    globals()['BlenderOutput'] = _BlenderOutput
    globals()['LoupedeckOutput'] = _LoupedeckOutput
    globals()['SystemOutput'] = _SystemOutput
    
    # Create and run orchestrator (pass optional camera index override)
    orchestrator = GestureControlOrchestrator(args.config, camera_index_override=args.camera_index)
    orchestrator.run()


if __name__ == '__main__':
    main()
