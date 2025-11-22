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
import signal
import sys
import time
import logging
import yaml
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.event_system import EventBus
from inputs.gesture_input import GestureInput
from inputs.mx_console_input import MXConsoleInput
from outputs.blender_output import BlenderOutput
from outputs.loupedeck_output import LoupedeckOutput
from outputs.system_output import SystemOutput

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
    
    def __init__(self, config_path: str):
        """
        Initialize orchestrator.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Core event bus
        self.event_bus = EventBus()
        
        # Module lists
        self.inputs = []
        self.outputs = []
        
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
        if gesture_config.get('enabled', False):
            try:
                gesture_input = GestureInput(self.event_bus, gesture_config)
                self.inputs.append(gesture_input)
                logger.info("✓ Gesture input initialized")
            except Exception as e:
                logger.error(f"Failed to initialize gesture input: {e}")
        
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
    
    args = parser.parse_args()
    
    # Create and run orchestrator
    orchestrator = GestureControlOrchestrator(args.config)
    orchestrator.run()


if __name__ == '__main__':
    main()
