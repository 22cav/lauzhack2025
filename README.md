# Production Gesture Control System

**Status**: ✅ Production-ready with macOS support

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Blender integration
python main_orchestrator.py --config config/blender_mode.yaml

# Run with debug logging
python main_orchestrator.py --config config/blender_mode.yaml --debug
```

## ✨ Features

### Production Gesture System
- **15+ Gestures**: Basic (6) + Advanced (9)
- **Robust Detection**: Smoothing filters and confidence validation
- **Platform-Aware**: Automatic macOS/Linux/Windows support
- **Modular Design**: Easy to extend with new gestures

### Platform Support
- ✅ **macOS**: Main-thread camera mode (camera window works!)
- ✅ **Linux**: Threaded camera mode
- ✅ **Windows**: Threaded camera mode

### Available Gestures

**Basic** (6):
- 🖐️ Open Palm
- ✊ Closed Fist  
- 👆 Pointing
- ✌️ Peace Sign
- 👍 Thumbs Up
- 🤘 Rock On

**Advanced** (9):
- 🤏 Pinch
- 🖱️ Pinch & Drag (viewport control)
- ⬅️➡️⬆️⬇️ Swipes (4 directions)
- 🔄 Rotate Clockwise
- 👋 Wave

## 🎯 Blender Integration

Control Blender with hand gestures:
- **Pinch + Drag** → Rotate 3D viewport
- **Open Palm** → Play animation
- **Closed Fist** → Pause animation
- **Pointing** → Next frame
- **Peace Sign** → Previous frame
- **Thumbs Up** → Toggle edit mode

## 🔧 Configuration

Edit `config/blender_mode.yaml` to adjust:
- Gesture sensitivity
- Enabled gesture sets
- Camera settings
- Blender mappings

## 📦 Project Structure

```
├── config/                  # Configuration files
│   ├── blender_mode.yaml   # Blender integration config
│   ├── event_mappings.yaml # Default event mappings
│   └── test_gesture_only.yaml
├── core/                    # Core event system
│   ├── event_system.py     # EventBus implementation
│   ├── gesture_handler.py  # Gesture processing
│   └── launcher.py         # Application launcher
├── gestures/                # Production gesture library
│   ├── detector.py         # Gesture detection engine
│   ├── filters.py          # Smoothing filters
│   ├── validators.py       # Quality validators
│   ├── registry.py         # Gesture registration
│   └── library/            # Gesture definitions
│       ├── basic.py        # Basic gestures (6)
│       ├── advanced.py     # Advanced gestures (9)
│       └── navigation.py   # Navigation gestures
├── handlers/                # Specialized gesture handlers
│   ├── blender_animation_handler.py
│   └── blender_viewport_handler.py
├── inputs/                  # Input modules
│   ├── gesture_input.py    # Base gesture input
│   ├── gesture_input_production.py
│   └── mx_console_input.py
├── outputs/                 # Output modules
│   ├── blender_output.py   # Blender integration
│   ├── loupedeck_output.py # Loupedeck (legacy)
│   └── system_output.py    # System commands
├── blender_addon/           # Blender addon
│   └── gesture_control_addon.py
├── tests/                   # Test suite
│   ├── test_core.py
│   ├── test_gestures.py
│   ├── test_integration.py
│   ├── test_launcher.py
│   └── test_navigation_gestures.py
└── main_orchestrator.py     # Main entry point
```

## 🧪 Testing

```bash
# Core system tests
python -m pytest tests/test_core.py

# Gesture detection tests
python -m pytest tests/test_gestures.py

# Navigation gesture tests
python -m pytest tests/test_navigation_gestures.py

# Integration tests
python -m pytest tests/test_integration.py

# Run all tests
python -m pytest tests/
```

## 🐛 Troubleshooting

**Camera doesn't open?**
- Check camera permissions
- Try different camera index: `--camera-index 1`

**Gestures not detected?**
- Adjust sensitivity in `config/blender_mode.yaml`
- Run with debug logging: `--debug`
- Improve lighting conditions

**Blender not responding?**
- Install addon from `blender_addon/gesture_control_addon.py`
- Check port 8888 is not in use
- Ensure addon is enabled in Blender preferences

## 🎓 Architecture

Event-driven system with modular components:
- **EventBus** (`core/event_system.py`) - Central message routing
- **Input Modules** (`inputs/`) - Gesture recognition, device inputs
- **Output Modules** (`outputs/`) - Blender, Loupedeck, system control
- **Gesture Library** (`gestures/`) - Detection, filtering, validation
- **Handlers** (`handlers/`) - Specialized gesture processing

## 📝 Requirements

```
mediapipe>=0.10.0
opencv-python>=4.8.0
PyYAML>=6.0
numpy>=1.24.0
```

Install: `pip install -r requirements.txt`

## 🆕 What's New

- ✅ macOS camera support (main-thread mode)
- ✅ 15+ production gestures
- ✅ Smoothing filters for stability
- ✅ Confidence validation
- ✅ Platform auto-detection
- ✅ Modular gesture library

## 📄 License

See LICENSE file for details.

---

**Made with ❤️ for LauzHack 2025**
