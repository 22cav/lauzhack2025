#!/usr/bin/env python3
"""
Diagnostic Test - Run with full debug logging

This script runs the orchestrator with maximum logging to diagnose issues.
"""

import subprocess
import sys
import os

# Set debug mode
os.environ['PYTHONUNBUFFERED'] = '1'

print("="*70)
print("🔍 DIAGNOSTIC TEST - FULL DEBUG LOGGING")
print("="*70)
print("\nThis will show detailed logs of:")
print("  • Hand detection")
print("  • Quality validation")
print("  • Gesture detection")
print("  • Confidence validation")
print("\nPress Ctrl+C to stop")
print("="*70)
print()

try:
    # Run with debug flag
    proc = subprocess.run(
        [sys.executable, 'main_orchestrator.py', 
         '--config', 'config/blender_mode.yaml',
         '--debug'],
        check=False
    )
except KeyboardInterrupt:
    print("\n\n✓ Test stopped")

print("\n" + "="*70)
print("Review the logs above to see what's happening")
print("="*70)
