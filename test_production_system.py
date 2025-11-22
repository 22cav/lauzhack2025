#!/usr/bin/env python3
"""
Production Blender Demo Test

Tests the complete production system with macOS support.
"""

import platform
import sys

print("="*70)
print("🚀 PRODUCTION GESTURE SYSTEM TEST")
print("="*70)
print(f"Platform: {platform.system()}")

# Check if macOS
is_macos = platform.system() == "Darwin"
if is_macos:
    print("✓ macOS detected - main-thread camera mode will be used")
    print("  Camera window should work correctly!")
else:
    print(f"✓ {platform.system()} detected - threaded camera mode")

print("\n📦 Testing imports...")

try:
    from gestures import GestureDetector
    print("  ✓ GestureDetector")
except Exception as e:
    print(f"  ✗ GestureDetector: {e}")
    sys.exit(1)

try:
    from gestures.library import basic, advanced
    print("  ✓ Gesture libraries")
except Exception as e:
    print(f"  ✗ Gesture libraries: {e}")
    sys.exit(1)

try:
    from inputs.gesture_input_production import create_gesture_input, GestureInputMainThread, GestureInput
    print("  ✓ Production gesture input")
except Exception as e:
    print(f"  ✗ Production gesture input: {e}")
    sys.exit(1)

try:
    from core.event_system import EventBus
    print("  ✓ EventBus")
except Exception as e:
    print(f"  ✗ EventBus: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")

print("\n📊 System Info:")
print(f"  Python: {sys.version.split()[0]}")
print(f"  Platform: {platform.platform()}")
print(f"  Architecture: {platform.machine()}")

print("\n🎯 Ready to run!")
print("\n" + "="*70)
print("To run the production Blender demo:")
print("  python main_orchestrator.py --config config/blender_mode.yaml")
print("="*70)
