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

### Prerequisites

- Python 3.8+
- Conda (recommended) or virtualenv
- Webcam
- (Optional) MX Creative Console
- (Optional) Blender 3.0+

### Installation

```bash
# Create conda environment
conda create -n lauzhack python=3.9 -y
conda activate lauzhack

# Install dependencies
cd /Users/matte/MDS/Personal/lauzhack
pip install -r requirements.txt
```

### Running

```bash
# Default mode (gesture → system actions)
python main_orchestrator.py

# Blender mode
python main_orchestrator.py --config config/blender_mode.yaml

# Test mode (gestures only)
python main_orchestrator.py --config config/test_gesture_only.yaml
```

## 📁 Project Structure

```
lauzhack/
├── core/                       # Core event system
│   ├── event_system.py         # EventBus and Event classes
│   └── __init__.py
│
├── inputs/                     # Input modules (event producers)
│   ├── gesture_input.py        # Gesture recognition with pinch-drag
│   ├── mx_console_input.py     # MX Creative Console (Bluetooth)
│   └── __init__.py
│
├── outputs/                    # Output modules (event consumers)
│   ├── blender_output.py       # Blender integration
│   ├── loupedeck_output.py     # Loupedeck/Logitech plugin
│   ├── system_output.py        # System actions (volume, media)
│   └── __init__.py
│
├── config/                     # Configuration files
│   ├── event_mappings.yaml     # Default configuration
│   ├── blender_mode.yaml       # Blender-specific config
│   └── test_gesture_only.yaml  # Test configuration
│
├── tests/                      # Unit tests
│   ├── test_event_system.py    # Event system tests
│   └── __init__.py
│
├── GestureControlPlugin/       # Legacy C# Loupedeck plugin
│   ├── src/                    # C# source
│   └── gesture_engine/         # Original Python gesture code (deprecated)
│
├── main_orchestrator.py        # Main entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎮 Supported Gestures

### Basic Gestures
- 🖐️ **Open Palm** - All fingers extended
- ✊ **Closed Fist** - All fingers closed
- 👆 **Pointing** - Index finger extended

### Advanced Gestures
- 🤏 **Pinch Start** - Thumb and index touch
- 🖱️ **Pinch Drag** - Move hand while pinching (for viewport control)
- 🔓 **Pinch Release** - Fingers separate

## ⚙️ Configuration

Edit `config/event_mappings.yaml` to customize input sources and output targets:

```yaml
inputs:
  gesture:
    enabled: true
    camera_index: 0
    pinch_threshold: 0.05
  
  mx_console:
    enabled: false  # Enable if you have MX Creative Console

outputs:
  blender:
    enabled: true
    mappings:
      PINCH_DRAG: viewport_rotate
      OPEN_PALM: play_animation
  
  system:
    enabled: true
    mappings:
      OPEN_PALM: volumeup
      CLOSED_FIST: volumedown
```

## 🎨 Blender Integration

### Option 1: External Control (Current)

1. Start the orchestrator with Blender config:
   ```bash
   python main_orchestrator.py --config config/blender_mode.yaml
   ```

2. In Blender, install the listener addon:
   - Copy the code from `outputs/blender_output.py` (BLENDER_ADDON_TEMPLATE)
   - Save as `gesture_listener.py` in Blender addons folder
   - Enable in Blender preferences

3. Perform gestures to control Blender viewport

### Option 2: Blender Addon (Future)

Package the entire system as a Blender addon with embedded gesture engine.

## 🔧 Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_event_system.py

# Run with verbose output
python -m pytest tests/ -v
```

### Adding New Gestures

1. Edit `inputs/gesture_input.py`
2. Add detection logic in `_detect_basic_gesture()` or create new method
3. Publish new event type
4. Map in configuration file

### Adding New Outputs

1. Create new file in `outputs/` (e.g., `outputs/my_output.py`)
2. Implement class with `start()` and `stop()` methods
3. Subscribe to events in `start()`
4. Add to `main_orchestrator.py`
5. Add configuration section in YAML

## 📚 Documentation

- [GUIDE.md](GUIDE.md) - Detailed setup and usage guide
- [Implementation Plan](/.gemini/antigravity/brain/676d8f7a-6124-4875-ad54-23c965025672/implementation_plan.md) - Architecture design doc
- [Legacy Docs](docs/) - Original documentation

## 🔄 Backward Compatibility

The system maintains full backward compatibility with the existing C# Loupedeck plugin:

```bash
# Enable Loupedeck output in config
# config/event_mappings.yaml
outputs:
  loupedeck:
    enabled: true
    
# Run orchestrator
python main_orchestrator.py

# Start C# plugin (in Logitech G Hub)
# Gestures will be sent to C# plugin as before
```

## 🐛 Troubleshooting

### Camera Issues
- Ensure no other app is using the camera
- Try different `camera_index` values (0, 1, 2...)
- Check camera permissions in System Preferences (macOS)

### Blender Not Receiving Events
- Verify Blender listener addon is installed and running
- Check that port 8888 is not blocked by firewall
- Look for connection errors in orchestrator logs

### MX Console Not Detected
- Ensure `bleak` library is installed: `pip install bleak`
- Check Bluetooth is enabled
- Note: MX Console support requires reverse-engineering the Bluetooth protocol

## 📝 License

MIT

## 👥 Authors

Lauzhack Team

---

**🎉 Enjoy your multi-input gesture control system!**
