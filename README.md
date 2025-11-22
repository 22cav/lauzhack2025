# Multi-Input Gesture Control System

A modular, event-driven gesture control system that supports multiple input sources (webcam gestures, Bluetooth buttons) and multiple output targets (Blender, Logitech devices, system actions).

## 🎯 Features

- **Multi-Input Support**:
  - 📹 Webcam gesture recognition with MediaPipe
  - 🎮 Enhanced gestures: pinch-drag for viewport control
  - 🔘 MX Creative Console Bluetooth button support
  - 📷 MX Brio webcam optimization

- **Multi-Output Support**:
  - 🎨 Blender integration for 3D viewport control
  - 🎛️ Logitech/Loupedeck device integration (backward compatible)
  - 💻 System-level actions (volume, media controls)

- **Event-Driven Architecture**:
  - 🔄 Decoupled input producers and output consumers
  - ⚙️ Configurable event routing via YAML
  - 🔧 Extensible plugin system

## 🚀 Quick Start

### 🎨 **Live Demo with Blender** (Recommended)

See your gestures control Blender in real-time!

```bash
# Install dependencies
conda activate lauzhack
pip install -r requirements.txt

# Run the demo
python demo_blender.py
```

Follow the on-screen instructions to set up the Blender addon. See [DEMO_GUIDE.md](DEMO_GUIDE.md) for details.

### ⚡ **Quick Test** (No Blender needed)

```bash
# Test gesture recognition only
python main_orchestrator.py --config config/test_gesture_only.yaml
```

Perform gestures to control system volume and media playback.

## 📋 What You Get

### Camera Visualization
- ✅ Live camera feed with skeleton tracking
- ✅ Hand landmarks overlay
- ✅ Current gesture displayed
- ✅ Visual feedback for all gestures

### Blender Control
- ✅ Pinch-drag to rotate viewport
- ✅ Gestures control timeline and playback
- ✅ Real-time response
- ✅ Visual command feedback in Blender

## 📚 Documentation

- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Complete Blender demo guide  
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[docs/SETUP.md](docs/SETUP.md)** - Detailed setup and configuration
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design
- **[docs/README.md](docs/README.md)** - Documentation index

## 🎮 Supported Gestures

### Basic Gestures
- 🖐️ **Open Palm** - All fingers extended
- ✊ **Closed Fist** - All fingers closed
- 👆 **Pointing** - Index finger extended

### Advanced Gestures
- 🤏 **Pinch Start** - Thumb and index touch
- 🖱️ **Pinch Drag** - Move hand while pinching (for viewport control)
- 🔓 **Pinch Release** - Fingers separate

## 📁 Project Structure

```
lauzhack/
├── demo_blender.py         # 🎨 Blender demo launcher
├── main_orchestrator.py    # Main entry point
│
├── blender_addon/          # Blender addon
│   └── gesture_control_addon.py
│
├── core/                   # Core event system
│   └── event_system.py
│
├── inputs/                 # Input modules
│   ├── gesture_input.py    # Gesture recognition
│   └── mx_console_input.py # Bluetooth buttons
│
├── outputs/                # Output modules
│   ├── blender_output.py   # Blender integration
│   ├── loupedeck_output.py # Loupedeck plugin
│   └── system_output.py    # System actions
│
├── config/                 # YAML configurations
│   ├── event_mappings.yaml
│   ├── blender_mode.yaml
│   └── test_gesture_only.yaml
│
├── tests/                  # Unit tests
└── docs/                   # Documentation
```

## ⚙️ Configuration

Edit `config/event_mappings.yaml` to customize:

```yaml
inputs:
  gesture:
    enabled: true
    camera_index: 0           # Change if you have multiple cameras
    pinch_threshold: 0.05     # Adjust sensitivity
  
  mx_console:
    enabled: false            # Set to true if you have MX Console

outputs:
  blender:
    enabled: true             # Blender integration
    mappings:
      PINCH_DRAG: viewport_rotate
      OPEN_PALM: play_animation
  
  system:
    enabled: true             # Volume/media controls
    mappings:
      OPEN_PALM: volumeup
      CLOSED_FIST: volumedown
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Test with Blender demo
python demo_blender.py

# Test gesture recognition only
python main_orchestrator.py --config config/test_gesture_only.yaml
```

## 🔧 Development

### Adding New Gestures

Edit `inputs/gesture_input.py` → `_detect_basic_gesture()`:

```python
if extended_fingers == 2:
    # Peace sign detection
    return "PEACE_SIGN"
```

Then map in config:
```yaml
mappings:
  PEACE_SIGN: nexttrack
```

### Adding New Outputs

1. Create `outputs/my_output.py`
2. Implement `start()` and `stop()` methods
3. Subscribe to events: `event_bus.subscribe(EventType.GESTURE, callback)`
4. Add to `main_orchestrator.py`
5. Configure in YAML

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## 🎬 Demo Videos

The `demo_blender.py` script provides a complete visual demonstration:
- Camera window shows live gesture detection
- Blender window responds in real-time
- Visual feedback for all commands

## 🐛 Troubleshooting

### Camera Not Working
- Check `camera_index` in config (try 0, 1, 2...)
- Close other apps using camera
- Check permissions (System Preferences → Camera)

### Blender Not Responding
- Verify addon is installed and enabled
- Check port 8888 is not blocked
- See [DEMO_GUIDE.md](DEMO_GUIDE.md#troubleshooting)

### Gestures Not Detected
- Improve lighting
- Keep hand 30-60cm from camera
- Lower `min_detection_confidence` in config

## 🆘 Getting Help

1. **Live Demo**: See [DEMO_GUIDE.md](DEMO_GUIDE.md)
2. **Setup**: See [docs/SETUP.md](docs/SETUP.md)
3. **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Tests**: Run `python -m pytest tests/ -v`

## 📝 License

MIT

## 👥 Authors

Lauzhack Team

---

**🎉 Try the demo: `python demo_blender.py`**
