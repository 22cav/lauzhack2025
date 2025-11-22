# Quick Start Guide - Separated Concerns Architecture

## What Changed?

The gesture control system has been refactored into a modular, event-driven architecture:

- ✅ **Multiple Inputs**: Webcam gestures + MX Creative Console buttons
- ✅ **Multiple Outputs**: Blender + Loupedeck + System actions
- ✅ **Configurable**: YAML-based event routing
- ✅ **Advanced Gestures**: Pinch-drag for viewport control
- ✅ **Backward Compatible**: Existing C# plugin still works

## Installation

```bash
conda activate lauzhack
cd /Users/matte/MDS/Personal/lauzhack
pip install -r requirements.txt
```

## Usage

### Basic Test (No Camera)

```bash
python test_quick.py
```

### System Control Mode

Control volume and media playback with gestures:

```bash
python main_orchestrator.py --config config/test_gesture_only.yaml
```

- 🖐️ Open Palm → Volume Up
- ✊ Closed Fist → Volume Down  
- 👆 Pointing → Play/Pause

### Blender Mode

Control Blender viewport with gestures:

```bash
# Start orchestrator
python main_orchestrator.py --config config/blender_mode.yaml

# In Blender, install the listener addon from outputs/blender_output.py
```

- 🤏 Pinch + Drag → Rotate viewport
- 🖐️ Open Palm → Play animation
- ✊ Closed Fist → Pause animation
- 👆 Pointing → Next frame

### Default Mode (Everything)

```bash
python main_orchestrator.py
```

## Configuration

Edit `config/event_mappings.yaml` to customize:

```yaml
inputs:
  gesture:
    enabled: true
    camera_index: 0      # Change if you have multiple cameras
    pinch_threshold: 0.05 # Adjust sensitivity
  
  mx_console:
    enabled: false       # Set to true if you have MX Console

outputs:
  blender:
    enabled: true        # Blender integration
  loupedeck:
    enabled: false       # C# Loupedeck plugin
  system:
    enabled: true        # Volume/media controls
```

## Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Quick integration test
python test_quick.py
```

## File Structure

```
lauzhack/
├── core/               # Event system (EventBus)
├── inputs/             # Gesture, MX Console
├── outputs/            # Blender, Loupedeck, System
├── config/             # YAML configurations
├── tests/              # Unit tests
└── main_orchestrator.py # Main entry point
```

## New Gestures

In addition to the original gestures (open palm, closed fist, pointing), you now have:

- **PINCH_START**: Thumb and index finger touch
- **PINCH_DRAG**: Move hand while pinching (continuous position updates)
- **PINCH_RELEASE**: Fingers separate

Perfect for controlling 3D viewports!

## Next Steps

1. Try the test mode: `python test_quick.py`
2. Test gesture recognition: `python main_orchestrator.py --config config/test_gesture_only.yaml`
3. Customize mappings in `config/event_mappings.yaml`
4. Read the full [README.md](README.md) for more details

## Troubleshooting

**Camera not working?**
- Check `camera_index` in config (try 0, 1, 2...)
- Close other apps using camera
- Check permissions in System Preferences

**MX Console not connecting?**
- Install bleak: `pip install bleak`
- Note: Protocol needs reverse-engineering (currently stub)

**Blender not receiving events?**
- Verify Blender listener addon installed
- Check port 8888 not blocked

---

**Questions?** See the [walkthrough](/.gemini/antigravity/brain/676d8f7a-6124-4875-ad54-23c965025672/walkthrough.md) for complete documentation.
