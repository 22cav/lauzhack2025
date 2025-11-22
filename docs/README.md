# Documentation Index

Complete reference for the Multi-Input Gesture Control System.

## Quick Start

- **[QUICKSTART.md](../QUICKSTART.md)** - 5-minute setup guide
- **[README.md](../README.md)** - Project overview and features

## Setup & Installation

- **[SETUP.md](SETUP.md)** - Detailed installation and configuration guide
- **[requirements.txt](../requirements.txt)** - Python dependencies

## Architecture & Design

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design patterns
- **[API.md](API.md)** - Event system API reference

## Component Documentation

- **[PYTHON_ENGINE.md](PYTHON_ENGINE.md)** - Gesture detection implementation
- **[CSHARP_PLUGIN.md](CSHARP_PLUGIN.md)** - C# Loupedeck plugin details

## Configuration

- **[config/event_mappings.yaml](../config/event_mappings.yaml)** - Default configuration
- **[config/blender_mode.yaml](../config/blender_mode.yaml)** - Blender-specific config
- **[config/test_gesture_only.yaml](../config/test_gesture_only.yaml)** - Testing config

## Legacy Documentation

These documents describe the old monolithic system and are kept for historical reference:

- **[GUIDE_LEGACY.md](GUIDE_LEGACY.md)** - Old comprehensive guide
- **[C#_PLUGIN_WALKTHROUGH.md](C#_PLUGIN_WALKTHROUGH.md)** - Original C# plugin walkthrough

## File Structure

```
lauzhack/
│
├── docs/                    # Documentation (you are here)
│   ├── README.md            # Documentation index
│   ├── SETUP.md             # Setup guide
│   ├── ARCHITECTURE.md      # Architecture documentation
│   ├── API.md               # API reference
│   ├── PYTHON_ENGINE.md     # Python implementation details
│   ├── CSHARP_PLUGIN.md     # C# plugin details
│   ├── GUIDE_LEGACY.md      # Legacy guide
│   └── C#_PLUGIN_WALKTHROUGH.md  # Legacy walkthrough
│
├── core/                    # Core event system
│   ├── event_system.py      # EventBus implementation
│   └── __init__.py
│
├── inputs/                  # Input modules
│   ├── gesture_input.py     # Gesture recognition
│   ├── mx_console_input.py  # MX Console buttons
│   └── __init__.py
│
├── outputs/                 # Output modules
│   ├── blender_output.py    # Blender integration
│   ├── loupedeck_output.py  # C# plugin client
│   ├── system_output.py     # System actions
│   └── __init__.py
│
├── config/                  # YAML configurations
│   ├── event_mappings.yaml  # Default config
│   ├── blender_mode.yaml    # Blender config
│   └── test_gesture_only.yaml  # Test config
│
├── tests/                   # Unit tests
│   ├── test_event_system.py # Event system tests
│   └── __init__.py
│
├── GestureControlPlugin/    # C# Loupedeck plugin
│   ├── src/                 # C# source code
│   ├── gesture_engine_legacy/  # Old Python code (archived)
│   └── GestureControlPlugin.sln
│
├── main_orchestrator.py     # Main entry point
├── requirements.txt         # Python dependencies
├── QUICKSTART.md            # Quick start guide
└── README.md                # Project overview
```

## Common Tasks

### First Time Setup

1. Read [QUICKSTART.md](../QUICKSTART.md)
2. Follow [SETUP.md](SETUP.md) for detailed installation
3. Test with `python test_quick.py`

### Understanding the Architecture

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Review [API.md](API.md) for event system API
3. Check component docs ([PYTHON_ENGINE.md](PYTHON_ENGINE.md), [CSHARP_PLUGIN.md](CSHARP_PLUGIN.md))

### Customizing the System

1. Edit `config/event_mappings.yaml` for basic customization
2. Modify `inputs/gesture_input.py` to add new gestures
3. Create new output modules in `outputs/` for new targets

### Troubleshooting

1. Check [SETUP.md](SETUP.md#troubleshooting) for common issues
2. Review logs in terminal output
3. Verify configuration in YAML files

## Key Concepts

### Event-Driven Architecture

The system uses a publish-subscribe pattern:
- **Inputs** publish events when actions are detected
- **EventBus** routes events to subscribed handlers
- **Outputs** subscribe to events and execute actions

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

### Gestures

Supported gestures:
- OPEN_PALM, CLOSED_FIST, POINTING (basic)
- PINCH_START, PINCH_DRAG, PINCH_RELEASE (advanced)

See [PYTHON_ENGINE.md](PYTHON_ENGINE.md) for implementation.

### Configuration

YAML files define:
- Which inputs are enabled
- Which outputs are enabled
- How events map to actions

See [SETUP.md](SETUP.md#advanced-configuration) for examples.

## Getting Help

1. **Documentation**: Start with this index and follow relevant links
2. **Examples**: Check `config/` for configuration examples
3. **Tests**: Run `python -m pytest tests/ -v` to verify system
4. **Code**: All modules are well-documented with docstrings

## Contributing

When adding features:
1. Update relevant documentation
2. Add unit tests
3. Update configuration examples
4. Test with existing system

---

**Last Updated**: 2025-11-22

**Version**: 2.0 (Event-Driven Architecture)
