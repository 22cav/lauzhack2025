#!/usr/bin/env python3
"""
Test script for the modular gesture handler system.

Tests handler registration, configuration, and execution.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.gesture_handler import (
    GestureHandler, HandlerRegistry, HandlerManager,
    HandlerContext, HandlerPriority
)
from core.event_system import Event, EventType
from handlers.blender_viewport_handler import create_blender_viewport_handler
from handlers.blender_animation_handler import create_blender_animation_handler
from handlers.system_control_handler import create_system_control_handler


def test_handler_registration():
    """Test handler registration and retrieval."""
    print("=" * 60)
    print("TEST: Handler Registration")
    print("=" * 60)
    
    registry = HandlerRegistry()
    
    # Register factories
    registry.register_factory('blender_viewport', create_blender_viewport_handler)
    registry.register_factory('blender_animation', create_blender_animation_handler)
    registry.register_factory('system_control', create_system_control_handler)
    
    # Create handlers from config
    viewport_config = {
        'enabled': True,
        'priority': 75,
        'gestures': ['PINCH_DRAG', 'ROTATE'],
        'sensitivity': 1.5
    }
    
    animation_config = {
        'enabled': True,
        'priority': 50,
        'gestures': ['OPEN_PALM', 'CLOSED_FIST'],
        'cooldown': 0.5
    }
    
    registry.create_from_config('blender_viewport', viewport_config)
    registry.create_from_config('blender_animation', animation_config)
    
    # Verify registration
    handlers = registry.list_handlers()
    print(f"✓ Registered handlers: {handlers}")
    
    # Test retrieval
    viewport_handler = registry.get('blender_viewport')
    print(f"✓ Retrieved viewport handler: {viewport_handler.name}")
    print(f"  - Priority: {viewport_handler.priority}")
    print(f"  - Gestures: {viewport_handler.gestures}")
    
    # Test gesture filtering
    rotate_handlers = registry.get_for_gesture('ROTATE')
    print(f"✓ Handlers for ROTATE: {[h.name for h in rotate_handlers]}")
    
    print()


def test_handler_execution():
    """Test handler execution through manager."""
    print("=" * 60)
    print("TEST: Handler Execution")
    print("=" * 60)
    
    registry = HandlerRegistry()
    registry.register_factory('blender_viewport', create_blender_viewport_handler)
    registry.register_factory('blender_animation', create_blender_animation_handler)
    
    # Create handlers
    viewport_config = {
        'enabled': True,
        'priority': 75,
        'gestures': ['PINCH_DRAG'],
        'sensitivity': 2.0
    }
    
    animation_config = {
        'enabled': True,
        'priority': 50,
        'gestures': ['OPEN_PALM'],
        'cooldown': 0.0
    }
    
    registry.create_from_config('blender_viewport', viewport_config)
    registry.create_from_config('blender_animation', animation_config)
    
    # Create manager
    manager = HandlerManager(registry)
    
    # Test viewport rotation event
    print("\nTest 1: PINCH_DRAG event")
    event = Event(
        type=EventType.GESTURE,
        source='test',
        action='PINCH_DRAG',
        data={'dx': 0.1, 'dy': 0.05}
    )
    
    results = manager.process_event(event)
    print(f"✓ Processed by {len(results)} handler(s)")
    for result in results:
        print(f"  - Handler: {result['handler']}")
        print(f"    Command: {result['result'].get('command')}")
        print(f"    dx: {result['result'].get('dx')}")
        print(f"    dy: {result['result'].get('dy')}")
    
    # Test animation event
    print("\nTest 2: OPEN_PALM event")
    event = Event(
        type=EventType.GESTURE,
        source='test',
        action='OPEN_PALM',
        data={}
    )
    
    results = manager.process_event(event)
    print(f"✓ Processed by {len(results)} handler(s)")
    for result in results:
        print(f"  - Handler: {result['handler']}")
        print(f"    Command: {result['result'].get('command')}")
    
    # Test unhandled gesture
    print("\nTest 3: Unhandled gesture")
    event = Event(
        type=EventType.GESTURE,
        source='test',
        action='UNKNOWN_GESTURE',
        data={}
    )
    
    results = manager.process_event(event)
    print(f"✓ Processed by {len(results)} handler(s) (expected 0)")
    
    print()


def test_priority_ordering():
    """Test handler priority ordering."""
    print("=" * 60)
    print("TEST: Priority Ordering")
    print("=" * 60)
    
    registry = HandlerRegistry()
    
    # Create handlers with different priorities
    registry.register_factory('blender_viewport', create_blender_viewport_handler)
    registry.register_factory('blender_animation', create_blender_animation_handler)
    
    high_priority_config = {
        'enabled': True,
        'priority': 100,
        'gestures': ['TEST_GESTURE']
    }
    
    low_priority_config = {
        'enabled': True,
        'priority': 25,
        'gestures': ['TEST_GESTURE']
    }
    
    registry.create_from_config('blender_viewport', high_priority_config)
    registry.create_from_config('blender_animation', low_priority_config)
    
    # Get handlers for gesture
    handlers = registry.get_for_gesture('TEST_GESTURE')
    
    print(f"✓ Handlers ordered by priority:")
    for i, handler in enumerate(handlers):
        print(f"  {i+1}. {handler.name} (priority={handler.priority})")
    
    # Verify ordering
    assert handlers[0].priority >= handlers[1].priority, "Priority ordering failed!"
    print("✓ Priority ordering verified")
    
    print()


def test_enable_disable():
    """Test handler enable/disable functionality."""
    print("=" * 60)
    print("TEST: Enable/Disable")
    print("=" * 60)
    
    registry = HandlerRegistry()
    registry.register_factory('blender_viewport', create_blender_viewport_handler)
    
    config = {
        'enabled': True,
        'gestures': ['PINCH_DRAG']
    }
    
    registry.create_from_config('blender_viewport', config)
    manager = HandlerManager(registry)
    
    # Test enabled
    event = Event(type=EventType.GESTURE, source='test', action='PINCH_DRAG', data={'dx': 0.1, 'dy': 0.1})
    results = manager.process_event(event)
    print(f"✓ Enabled: {len(results)} handler(s) executed")
    
    # Disable handler
    manager.disable_handler('blender_viewport')
    results = manager.process_event(event)
    print(f"✓ Disabled: {len(results)} handler(s) executed")
    
    # Re-enable handler
    manager.enable_handler('blender_viewport')
    results = manager.process_event(event)
    print(f"✓ Re-enabled: {len(results)} handler(s) executed")
    
    print()


def test_statistics():
    """Test execution statistics."""
    print("=" * 60)
    print("TEST: Execution Statistics")
    print("=" * 60)
    
    registry = HandlerRegistry()
    registry.register_factory('blender_viewport', create_blender_viewport_handler)
    
    config = {
        'enabled': True,
        'gestures': ['PINCH_DRAG'],
        'cooldown': 0.0
    }
    
    registry.create_from_config('blender_viewport', config)
    manager = HandlerManager(registry)
    
    # Execute multiple times
    event = Event(type=EventType.GESTURE, source='test', action='PINCH_DRAG', data={'dx': 0.1, 'dy': 0.1})
    
    for i in range(5):
        manager.process_event(event)
    
    stats = manager.get_stats()
    print(f"✓ Execution statistics:")
    for handler_name, count in stats.items():
        print(f"  - {handler_name}: {count} executions")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GESTURE HANDLER SYSTEM TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_handler_registration()
        test_handler_execution()
        test_priority_ordering()
        test_enable_disable()
        test_statistics()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
