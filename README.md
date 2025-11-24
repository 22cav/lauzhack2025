# 3DX - Hand Gesture Control for Blender

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Blender](https://img.shields.io/badge/blender-3.0+-orange) ![Python](https://img.shields.io/badge/python-3.9+-green)

**Control Blender's 3D viewport with hand gestures using your webcam.** Production-ready addon with MediaPipe hand tracking, event-driven architecture, and Pydantic validation.

## Features

| Gesture | Action |
|---------|--------|
| 🤏 Pinch & Drag | Rotate viewport (orbit-style) |
| ✌️ V-Gesture | Pan camera |
| 🖐️ Open Palm | Play animation |
| ✊ Closed Fist | Stop animation |

## Quick Start

### 1. Install Dependencies

Install in **Blender's Python** (not system Python):

```bash
# macOS
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip install opencv-python mediapipe numpy pydantic

# Windows
"C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe" -m pip install opencv-python mediapipe numpy pydantic

# Linux
/usr/share/blender/4.2/python/bin/python3.11 -m pip install opencv-python mediapipe numpy pydantic
```

### 2. Install Addon

1. Download/clone this repository
2. Blender → Edit → Preferences → Add-ons → Install
3. Select the `3dx` folder (or ZIP it first)
4. Enable "3DX - Gesture Control"

### 3. Use

1. Open 3D Viewport → Press `N` → Select **3DX** tab
2. Click **Start** → Grant camera permission
3. Perform gestures in front of camera

## Architecture

```
3dx/
├── __init__.py              # Addon registration
├── config.py                # Constants, Pydantic models
├── gesture_engine.py        # Main processing loop
├── operators.py             # Start/stop/settings operators
├── properties.py            # Preferences & runtime state
├── panels.py                # UI panels
├── utils.py                 # Camera validation, math utils
├── core/
│   ├── event_system.py      # Pub/sub event bus
│   ├── listener.py          # Event → handler routing
│   └── modality_manager.py  # State management
├── gestures/
│   ├── detector.py          # Hand detection wrapper
│   ├── filters.py           # Temporal smoothing
│   ├── validators.py        # Data validation
│   ├── landmarks.py         # Hand landmark utilities
│   └── library/             # Gesture implementations
│       ├── basic.py         # Palm, Fist
│       ├── navigation.py    # Pinch, V-Gesture
│       └── advanced.py      # (Extensible)
├── handlers/
│   ├── handler_base.py      # Base handler interface
│   ├── viewport_handler.py  # Viewport manipulation
│   └── animation_handler.py # Animation control
└── camera/
    └── capture.py           # OpenCV camera wrapper
```

## Key Features

- **Event-Driven**: Pub/sub architecture with `EventBus` for loose coupling
- **Type-Safe**: Full type hints + Pydantic validation on all data structures
- **Modular**: Gesture library, handlers, and filters are independently extensible
- **Robust**: Comprehensive error handling, graceful camera fallback
- **Tested**: 80+ unit tests (event system, gestures, handlers, utils)
- **Performant**: ~30 FPS frame processing, configurable sensitivity

## Configuration

Access via Edit → Preferences → Add-ons → 3DX:

| Setting | Description | Default |
|---------|-------------|---------|
| Camera Index | Webcam device ID | 0 |
| Rotation Sensitivity | Viewport rotation speed | 0.1 |
| Pan Sensitivity | Camera pan speed | 0.1 |
| Min Confidence | Gesture detection threshold | 0.6 |
| Frame Rate | Processing FPS | 30 |
| Show Preview | Display camera feed | False |
| Enable [Gesture] | Toggle individual gestures | All enabled |

## Development

**Tech Stack**: Python 3.9+, MediaPipe Hands, OpenCV, Pydantic, Blender API

**Code Style**: Google-style docstrings, type hints, `[3DX Module]` logging format

**Testing**: Run tests in Blender's Python environment or install `fake-bpy-module`:
```bash
pip install pytest fake-bpy-module-latest
python -m pytest tests/ -v
```

**Extending**:
- Add gestures: Implement `Gesture` class in `gestures/library/`
- Add handlers: Subclass `BaseHandler` in `handlers/`
- Add modalities: Extend `ModalityManager` in `core/`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Camera not detected | Check system permissions, try different indices (0,1,2) |
| Dependencies error | Install in Blender's Python, not system Python |
| Poor detection | Improve lighting, avoid cluttered backgrounds |
| Gestures too sensitive | Lower sensitivity in preferences |
| Addon won't enable | Check Blender console for import errors |

## License

MIT License

## Author

Matteo Caviglia ([@22cav](https://github.com/22cav)) - LauzHack 2025