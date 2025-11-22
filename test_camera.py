#!/usr/bin/env python3
"""
Quick Camera Test - See gesture recognition with visual feedback

This shows ONLY the camera window with landmarks and gestures.
No Blender integration - just pure visual feedback.

Usage:
    python test_camera.py

Press ESC to exit.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.event_system import EventBus
from inputs.gesture_input import GestureInput

def main():
    print("="*60)
    print("📹 Camera Gesture Recognition Test")
    print("="*60)
    print("\n🎬 Starting camera...")
    print("   Look for the camera window to open!")
    print("\n🤏 Try these gestures:")
    print("   • Open Palm (🖐️)")
    print("   • Closed Fist (✊)")
    print("   • Pointing (👆)")
    print("   • Pinch (🤏) - Bring thumb and index together")
    print("   • Pinch + Drag - Move hand while pinching")
    print("\n⌨️  Press ESC in the camera window to exit")
    print("="*60)
    print()
    
    # Create event bus (gestures will be published but not consumed)
    event_bus = EventBus()
    
    # Configure gesture input with preview enabled
    config = {
        'camera_index': 0,
        'min_detection_confidence': 0.5,
        'min_tracking_confidence': 0.5,
        'pinch_threshold': 0.05,
        'show_preview': True  # IMPORTANT: Shows the camera window
    }
    
    # Create and start gesture input
    gesture_input = GestureInput(event_bus, config)
    
    print("\n🚀 Starting gesture recognition...")
    gesture_input.start()
    
    print("✅ Camera should be open now!")
    print("   If you don't see it, check your Dock or Mission Control\n")
    
    # Wait for the thread to finish (when user presses ESC)
    try:
        gesture_input.thread.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
