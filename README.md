<div align="center">

![Gesture Control System](logo/logo.jpg)

# 3DX

**Real-time hand gesture recognition for controlling Blender's 3D viewport**

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Blender](https://img.shields.io/badge/blender-5.0+-orange) ![Python](https://img.shields.io/badge/python-3.11+-green) ![License](https://img.shields.io/badge/license-GPLv3-red)

</div>

## Features

| Gesture | Action |
|---------|--------|
| 🤏 Pinch & Drag | Rotate viewport (orbit-style) |
| ✌️ V-Gesture | Pan camera |
| 🖐️ Open Palm | Play animation |
| ✊ Closed Fist | Stop animation |

## Quick Start

### 1. Launch Blender via Command Line (Required)

**Crucial Step:** You must launch Blender from the terminal to ensure it has permission to access your camera on macOS.

```bash
# macOS
/Applications/Blender.app/Contents/MacOS/Blender
```

### 2. Install Addon

1. Download the `3dx.zip` release (or zip the repository yourself).
2. Blender → Edit → Preferences → Add-ons → Install...
3. Select `3dx.zip`.
4. Enable "3DX - Gesture Control".

**Note:** Dependencies (`opencv-python`, `mediapipe`, `numpy`, `pydantic`) are **automatically installed** when you enable the addon. You do not need to install them manually.

### 3. Use

1. Open 3D Viewport → Press `N` → Select **3DX** tab.
2. Click **Start Engine**.
3. Perform gestures in front of camera.

## Building from Source

To create the addon zip file without including development caches or git files, run:

```bash
zip -r 3dx.zip 3dx/ -x "3dx/__pycache__/*" "3dx/*/__pycache__/*" "3dx/.git/*" "3dx/tests/*" "3dx/.pytest_cache/*"
```

## Architecture

```
3dx/
├── __init__.py              # Addon registration & dependency management
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

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Camera Error** | **Launch Blender from Terminal** to grant permissions. |
| Dependencies error | Restart Blender after first installation. |
| Poor detection | Improve lighting, avoid cluttered backgrounds. |
| Gestures too sensitive | Lower sensitivity in preferences. |

## License

GNU General Public License v3.0

## Author

Matteo Caviglia ([@22cav](https://github.com/22cav))