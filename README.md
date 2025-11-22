# Production Gesture Control System

**Status**: ✅ Production-ready with macOS support

## 🚀 Quick Start

```bash
# Run the system
python main_orchestrator.py --config config/blender_mode.yaml

# With Blender demo
python demo_blender.py
```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Getting started guide
- **[SENSITIVITY_TUNING.md](SENSITIVITY_TUNING.md)** - Adjust gesture detection
- **[GESTURE_GUIDE.md](GESTURE_GUIDE.md)** - All available gestures
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Blender integration demo

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
│   └── event_mappings.yaml # Default event mappings
├── core/                    # Core event system
├── gestures/                # Production gesture library
│   ├── detector.py         # Gesture detection engine
│   ├── filters.py          # Smoothing filters
│   ├── validators.py       # Quality validators
│   └── library/            # Gesture definitions
│       ├── basic.py        # Basic gestures
│       └── advanced.py     # Advanced gestures
├── inputs/                  # Input modules
│   ├── gesture_input_production.py  # Production gesture input
│   └── mx_console_input.py # MX Console (stub)
├── outputs/                 # Output modules
│   ├── blender_output.py   # Blender integration
│   ├── loupedeck_output.py # Loupedeck (legacy)
│   └── system_output.py    # System commands
├── blender_addon/           # Blender addon
│   └── gesture_control_addon.py
├── main_orchestrator.py     # Main entry point
└── demo_blender.py          # Blender demo launcher
```

## 🧪 Testing

```bash
# Test gesture system
python test_production_gestures.py

# Quick camera test
python test_quick_camera.py

# Diagnostic with full logging
python test_diagnostic.py
```

## 🐛 Troubleshooting

**Camera doesn't open?**
- Check camera permissions
- Try different camera index: `--camera-index 1`

**Gestures not detected?**
- See [SENSITIVITY_TUNING.md](SENSITIVITY_TUNING.md)
- Run diagnostic: `python test_diagnostic.py`
- Improve lighting

**Blender not responding?**
- Install addon first (see [DEMO_GUIDE.md](DEMO_GUIDE.md))
- Check port 8888 is not in use
- Ensure addon is enabled in Blender

## 🎓 Architecture

This system uses an event-driven architecture with:
- **EventBus**: Central message routing
- **Input Modules**: Gesture recognition, device inputs
- **Output Modules**: Blender, Loupedeck, system control
- **Production Gestures**: Modular gesture library with filters/validators

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

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
