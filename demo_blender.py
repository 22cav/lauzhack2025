#!/usr/bin/env python3
"""
Blender Gesture Control Demo

This script launches a complete demo showing:
1. Camera feed with gesture detection and visual feedback
2. Blender responding to gestures in real-time

Usage:
    python demo_blender.py

Requirements:
    - Blender installed and in PATH (or modify BLENDER_PATH below)
    - Gesture control addon installed in Blender
    - Camera connected

Controls:
    - ESC: Exit demo
    - Gestures:
        🤏 Pinch + Drag → Rotate Blender viewport
        🖐️ Open Palm → Play animation
        ✊ Closed Fist → Pause animation
        👆 Pointing → Next frame
"""

import subprocess
import time
import sys
import os
from pathlib import Path

# Blender executable path - reads from environment variable or uses default
BLENDER_PATH = os.environ.get('BLENDER_PATH', 'blender')

# Common Blender paths for auto-detection
COMMON_BLENDER_PATHS = [
    '/Applications/Blender.app/Contents/MacOS/Blender',  # macOS
    'C:\\Program Files\\Blender Foundation\\Blender\\blender.exe',  # Windows
    '/usr/bin/blender',  # Linux
]

# Project paths
PROJECT_ROOT = Path(__file__).parent
ADDON_PATH = PROJECT_ROOT / "blender_addon" / "gesture_control_addon.py"
CONFIG_PATH = PROJECT_ROOT / "config" / "blender_mode.yaml"


def check_blender():
    """Check if Blender is installed and accessible."""
    global BLENDER_PATH
    
    # Try the configured path first
    try:
        result = subprocess.run(
            [BLENDER_PATH, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ Found {version} at {BLENDER_PATH}")
            return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Try common installation paths
    print(f"⚠️  Blender not found at: {BLENDER_PATH}")
    print("   Trying common installation paths...")
    
    for path in COMMON_BLENDER_PATHS:
        if os.path.exists(path):
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0]
                    print(f"✓ Found {version} at {path}")
                    BLENDER_PATH = path  # Update global
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
    
    # Not found anywhere
    print("\n❌ Blender not found!")
    print("\nPlease either:")
    print("  1. Install Blender from https://www.blender.org/download/")
    print("  2. Set BLENDER_PATH environment variable:")
    print("     export BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender")
    print("  3. Add Blender to your PATH")
    return False


def check_addon():
    """Check if the gesture control addon file exists."""
    if not ADDON_PATH.exists():
        print(f"❌ Addon not found: {ADDON_PATH}")
        return False
    
    print(f"✓ Addon found: {ADDON_PATH}")
    return True


def check_config():
    """Check if the Blender config exists."""
    if not CONFIG_PATH.exists():
        print(f"❌ Config not found: {CONFIG_PATH}")
        return False
    
    print(f"✓ Config found: {CONFIG_PATH}")
    return True


def install_addon_instructions():
    """Print instructions for installing the Blender addon."""
    print("\n" + "="*60)
    print("📦 BLENDER ADDON INSTALLATION")
    print("="*60)
    print("\n1. Open Blender")
    print("2. Go to: Edit → Preferences → Add-ons")
    print("3. Click 'Install...' button")
    print(f"4. Navigate to and select: {ADDON_PATH}")
    print("5. Enable the 'Gesture Control Listener' addon")
    print("6. The listener will start automatically")
    print("\nAlternatively, in Blender run:")
    print("  - Open Scripting workspace")
    print(f"  - Load script: {ADDON_PATH}")
    print("  - Run script (Alt+P)")
    print("\n" + "="*60)


def start_blender():
    """Start Blender with a default scene."""
    print("\n🚀 Starting Blender...")
    print("   (This will open Blender in a new window)")
    
    try:
        # Start Blender (non-blocking)
        process = subprocess.Popen(
            [BLENDER_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print("✓ Blender started")
        print(f"✓ Process ID: {process.pid}")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Blender: {e}")
        return None


def start_orchestrator():
    """Start the gesture control orchestrator."""
    print("\n🎮 Starting Gesture Control Orchestrator...")
    
    try:
        # Start orchestrator
        process = subprocess.Popen(
            [sys.executable, "main_orchestrator.py", "--config", str(CONFIG_PATH)],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print("✓ Orchestrator started")
        print(f"✓ Process ID: {process.pid}")
        
        # Show initial output
        print("\n" + "="*60)
        print("ORCHESTRATOR OUTPUT:")
        print("="*60)
        
        # Print output in real-time
        try:
            for i, line in enumerate(process.stdout):
                print(line, end='')
                
                # Stop after initial startup messages
                if i > 20 or "System running" in line:
                    break
        except:
            pass
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start orchestrator: {e}")
        return None


def main():
    """Main demo function."""
    print("="*60)
    print("🎨 BLENDER GESTURE CONTROL DEMO")
    print("="*60)
    
    # Pre-flight checks
    print("\n📋 Pre-flight checks...")
    
    if not check_blender():
        return 1
    
    if not check_addon():
        return 1
    
    if not check_config():
        return 1
    
    # Show installation instructions
    install_addon_instructions()
    
    input("\nPress ENTER when addon is installed in Blender...")
    
    # Start Blender
    blender_process = start_blender()
    if not blender_process:
        return 1
    
    # Wait for Blender to initialize
    print("\n⏳ Waiting for Blender to initialize (5 seconds)...")
    time.sleep(5)
    
    # Start orchestrator
    orchestrator_process = start_orchestrator()
    if not orchestrator_process:
        if blender_process:
            blender_process.terminate()
        return 1
    
    # Demo is running
    print("\n" + "="*60)
    print("✅ DEMO RUNNING!")
    print("="*60)
    print("\n📹 Camera window should be open showing gesture detection")
    print("🎨 Blender should be responding to your gestures")
    print("\n🤏 Try these gestures:")
    print("   • Pinch + Drag → Rotate Blender viewport")
    print("   • Open Palm (🖐️) → Play animation")
    print("   • Closed Fist (✊) → Pause animation")
    print("   • Pointing (👆) → Next frame")
    print("\n⌨️  Press Ctrl+C to exit")
    print("="*60)
    
    # Wait for user interruption
    try:
        orchestrator_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        
        # Terminate orchestrator
        if orchestrator_process:
            orchestrator_process.terminate()
            orchestrator_process.wait(timeout=3)
        
        # Note: Blender will remain open
        print("✓ Orchestrator stopped")
        print("✓ Blender is still running (close manually if desired)")
    
    print("\n👋 Demo complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
