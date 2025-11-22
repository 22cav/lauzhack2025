#!/usr/bin/env python3
"""
Quick Test - Production Gesture System with Camera

Runs the production system briefly to verify camera works.
Press Ctrl+C to stop.
"""

import subprocess
import sys

print("="*70)
print("🧪 QUICK CAMERA TEST")
print("="*70)
print("\nRunning orchestrator for 30 seconds...")
print("You should see:")
print("  ✓ Camera window opening")
print("  ✓ Skeleton tracking visible")
print("  ✓ Gesture detection working")
print("\nPress Ctrl+C to stop anytime, or wait 30 seconds")
print("="*70)
print()

try:
    # Run orchestrator with timeout
    proc = subprocess.Popen(
        [sys.executable, 'main_orchestrator.py', '--config', 'config/blender_mode.yaml'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Stream output
    import time
    start_time = time.time()
    for line in proc.stdout:
        print(line, end='')
        
        # Auto-stop after 30 seconds
        if time.time() - start_time > 30:
            proc.terminate()
            break
            
except KeyboardInterrupt:
    print("\n\n✓ Test stopped by user")
    proc.terminate()

print("\n" + "="*70)
print("✅ Test complete!")
print("="*70)
