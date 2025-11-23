# Gesture Handler Development Guide

## Overview

The gesture handler system provides a modular, plugin-based architecture for processing gestures and executing actions. This guide will help you create custom handlers for your specific use cases.

## Architecture

### Core Components

```
┌─────────────────┐
│  Gesture Input  │
└────────┬────────┘
         │ Events
         ▼
┌─────────────────┐
│   Event Bus     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Handler Manager │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Handler Registry                   │
│  ┌──────────────────────────────┐  │
│  │  Blender Viewport Handler    │  │
│  │  Blender Animation Handler   │  │
│  │  System Control Handler      │  │
│  │  Your Custom Handler         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Key Classes

- **`GestureHandler`**: Abstract base class for all handlers
- **`HandlerRegistry`**: Manages handler registration and discovery
- **`HandlerManager`**: Coordinates handler execution
- **`HandlerContext`**: Contains event data passed to handlers

## Creating a Custom Handler

### Step 1: Create Handler Class

Create a new file in the `handlers/` directory:

```python
# handlers/my_custom_handler.py

from typing import Dict, Any, Optional
from core.gesture_handler import GestureHandler, HandlerContext

class MyCustomHandler(GestureHandler):
    """
    Custom handler for specific gestures.
    
    Configuration:
        my_setting: Custom configuration value
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Set default gestures
        if 'gestures' not in config:
            config['gestures'] = ['THUMBS_UP', 'PEACE_SIGN']
        
        # Initialize base class
        super().__init__('my_custom_handler', config)
        
        # Extract custom settings
        self.my_setting = config.get('my_setting', 'default')
    
    def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
        """Process gesture events."""
        gesture = context.gesture
        
        if gesture == 'THUMBS_UP':
            return {
                'action': 'like',
                'timestamp': context.timestamp
            }
        
        return None
```

### Step 2: Create Factory Function

Add a factory function at the end of your handler file:

```python
def create_my_custom_handler(config: Dict[str, Any]) -> MyCustomHandler:
    """Factory function for creating handler."""
    return MyCustomHandler(config)
```

### Step 3: Register Handler

In your output module or orchestrator, register the handler factory:

```python
from handlers.my_custom_handler import create_my_custom_handler

registry.register_factory('my_custom_handler', create_my_custom_handler)
```

### Step 4: Configure Handler

Add configuration in `config/event_mappings.yaml` or `config/handler_config.yaml`:

```yaml
handlers:
  my_custom_handler:
    enabled: true
    priority: 50
    gestures:
      - THUMBS_UP
      - PEACE_SIGN
    my_setting: "custom_value"
    cooldown: 1.0
```

## Handler Interface

### Required Methods

#### `__init__(self, config: Dict[str, Any])`

Initialize your handler with configuration.

```python
def __init__(self, config: Dict[str, Any]):
    super().__init__('handler_name', config)
    # Extract custom settings
    self.custom_param = config.get('custom_param', default_value)
```

#### `handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]`

Process gesture events. Return a result dictionary or `None`.

```python
def handle(self, context: HandlerContext) -> Optional[Dict[str, Any]]:
    gesture = context.gesture
    data = context.data
    
    # Your logic here
    if gesture == 'MY_GESTURE':
        return {'action': 'my_action'}
    
    return None
```

### Optional Methods

#### `on_enable(self)`

Called when handler is enabled.

```python
def on_enable(self):
    # Initialize resources
    self.state = {}
```

#### `on_disable(self)`

Called when handler is disabled.

```python
def on_disable(self):
    # Cleanup resources
    self.state.clear()
```

#### `get_metadata(self) -> Dict[str, Any]`

Return handler metadata including custom state.

```python
def get_metadata(self) -> Dict[str, Any]:
    metadata = super().get_metadata()
    metadata['custom_state'] = self.my_state
    return metadata
```

## Handler Context

The `HandlerContext` object contains:

- **`event`**: Original `Event` object
- **`gesture`**: Gesture name (e.g., "THUMBS_UP")
- **`data`**: Gesture-specific data
  - `dx`, `dy`: Movement deltas (for drag gestures)
  - `confidence`: Detection confidence
  - `position`: Hand position
  - Custom data from gesture detector
- **`timestamp`**: Event timestamp
- **`metadata`**: Additional context

## Configuration Options

### Standard Options

All handlers support these configuration options:

```yaml
handler_name:
  enabled: true          # Enable/disable handler
  priority: 50           # Execution priority (0-100)
  gestures: []           # List of gestures to handle (empty = all)
  cooldown: 0.0          # Minimum time between executions (seconds)
```

### Custom Options

Add handler-specific options:

```yaml
handler_name:
  enabled: true
  # ... standard options ...
  
  # Custom options
  sensitivity: 1.5
  threshold: 0.8
  custom_setting: "value"
```

Access in handler:

```python
self.sensitivity = config.get('sensitivity', 1.0)
```

## Priority System

Handlers execute in priority order (highest first):

- **100 (HIGHEST)**: Critical handlers
- **75 (HIGH)**: Important handlers (e.g., viewport control)
- **50 (NORMAL)**: Standard handlers
- **25 (LOW)**: Background handlers
- **0 (LOWEST)**: Fallback handlers

Set priority in configuration:

```yaml
my_handler:
  priority: 75  # High priority
```

## Cooldown System

Prevent rapid repeated execution:

```yaml
my_handler:
  cooldown: 1.0  # 1 second minimum between executions
```

The handler system automatically enforces cooldown periods.

## Examples

### Example 1: Simple Action Handler

```python
class SimpleActionHandler(GestureHandler):
    def __init__(self, config):
        config['gestures'] = ['THUMBS_UP']
        super().__init__('simple_action', config)
    
    def handle(self, context):
        if context.gesture == 'THUMBS_UP':
            print("👍 Thumbs up detected!")
            return {'action': 'like'}
        return None
```

### Example 2: State Tracking Handler

```python
class CounterHandler(GestureHandler):
    def __init__(self, config):
        super().__init__('counter', config)
        self.count = 0
    
    def handle(self, context):
        self.count += 1
        return {
            'action': 'count',
            'count': self.count
        }
    
    def get_metadata(self):
        metadata = super().get_metadata()
        metadata['total_count'] = self.count
        return metadata
```

### Example 3: Conditional Handler

```python
class ConditionalHandler(GestureHandler):
    def __init__(self, config):
        super().__init__('conditional', config)
        self.threshold = config.get('threshold', 0.8)
    
    def handle(self, context):
        confidence = context.data.get('confidence', 1.0)
        
        if confidence < self.threshold:
            return None  # Don't handle low-confidence gestures
        
        return {'action': 'high_confidence_action'}
```

## Best Practices

### 1. Single Responsibility

Each handler should focus on one specific task:

✅ **Good**: `BlenderViewportHandler` handles viewport manipulation  
❌ **Bad**: `BlenderHandler` handles viewport, animation, and rendering

### 2. Configuration Over Code

Use configuration for customization:

✅ **Good**: `sensitivity = config.get('sensitivity', 1.0)`  
❌ **Bad**: Hardcoded sensitivity value

### 3. Graceful Degradation

Handle missing data gracefully:

```python
dx = context.data.get('dx', 0)  # Default to 0 if missing
```

### 4. Return None for Unhandled Gestures

```python
if gesture not in ['MY_GESTURE_1', 'MY_GESTURE_2']:
    return None  # Let other handlers try
```

### 5. Use Descriptive Names

```python
# Good
class BlenderViewportHandler(GestureHandler):
    pass

# Bad
class Handler1(GestureHandler):
    pass
```

### 6. Document Configuration

```python
class MyHandler(GestureHandler):
    """
    My custom handler.
    
    Configuration:
        sensitivity: Movement sensitivity (default: 1.0)
        threshold: Detection threshold (default: 0.8)
        enable_feature: Enable special feature (default: False)
    """
```

## Testing Handlers

### Unit Testing

```python
import unittest
from handlers.my_handler import MyCustomHandler
from core.gesture_handler import HandlerContext
from core.event_system import Event, EventType

class TestMyHandler(unittest.TestCase):
    def setUp(self):
        config = {'gestures': ['THUMBS_UP']}
        self.handler = MyCustomHandler(config)
    
    def test_handle_thumbs_up(self):
        event = Event(EventType.GESTURE, 'THUMBS_UP', {})
        context = HandlerContext(event, 'THUMBS_UP', {}, 0.0)
        
        result = self.handler.handle(context)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['action'], 'like')
```

### Integration Testing

Test with the full system:

```python
from core.gesture_handler import HandlerRegistry, HandlerManager

registry = HandlerRegistry()
registry.register_factory('my_handler', create_my_handler)
registry.create_from_config('my_handler', config)

manager = HandlerManager(registry)
results = manager.process_event(event)
```

## Troubleshooting

### Handler Not Executing

1. Check if handler is enabled in configuration
2. Verify gesture is in handler's gesture list
3. Check cooldown period
4. Verify handler is registered in registry

### Multiple Handlers Executing

This is normal! Multiple handlers can process the same gesture. Control with:

- Priority levels
- Gesture lists
- Cooldown periods

### Handler Errors

Errors are caught and logged. Check logs for details:

```
ERROR - Handler 'my_handler' error: ...
```

## Advanced Topics

### Dynamic Handler Loading

Load handlers at runtime:

```python
registry.create_from_config('new_handler', config)
```

### Handler Enable/Disable

Toggle handlers dynamically:

```python
manager.enable_handler('my_handler')
manager.disable_handler('my_handler')
```

### Execution Statistics

Track handler usage:

```python
stats = manager.get_stats()
print(f"Handler executed {stats['my_handler']} times")
```

## Complete Example

See [`handlers/example_custom_handler.py`](file:///Users/matte/MDS/Personal/lauzhack/handlers/example_custom_handler.py) for a fully documented example handler with all features demonstrated.

## Next Steps

1. Review existing handlers in `handlers/` directory
2. Copy `example_custom_handler.py` as a template
3. Implement your custom logic
4. Add configuration to YAML files
5. Test your handler
6. Deploy and enjoy!

## Support

For questions or issues:
- Check existing handlers for examples
- Review the implementation plan
- Examine the core handler system in `core/gesture_handler.py`
