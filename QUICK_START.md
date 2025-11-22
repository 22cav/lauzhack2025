# Production Gesture Control - Quick Start

## ✅ macOS Fix Applied!

The system now **works correctly on macOS** with the camera window!

## 🚀 Run the Demo

```bash
python main_orchestrator.py --config config/blender_mode.yaml
```

On **macOS**, you'll see:
- ✓ "macOS main-thread mode" detected
- ✓ Camera window appears and works
- ✓ All 15+ gestures available
- ✓ Smooth landmark tracking

On **other platforms**:
- ✓ "threaded mode" used
- ✓ Background processing
- ✓ Same gesture functionality

## 🎯 Available Gestures

### Basic (6)
- 🖐️ Open Palm → Play animation
- ✊ Closed Fist → Pause animation
- 👆 Pointing → Next frame
- ✌️ Peace Sign → Previous frame
- 👍 Thumbs Up → Toggle edit mode
- 🤘 Rock On → (available)

### Advanced (9)
- 🤏 Pinch + Drag → **Rotate Blender viewport**
- ⬅️ Swipe Left → Previous frame
- ➡️ Swipe Right → Next frame
- ⬆️ Swipe Up → Play animation
- ⬇️ Swipe Down → Pause animation
- 🔄 Rotate CW → (available)
- 👋 Wave → (available)

## 🧪 Test Before Blender

Test imports and platform detection:
```bash
python test_production_system.py
```

Expected output:
```
✓ macOS detected - main-thread camera mode will be used
✓ GestureDetector
✓ Gesture libraries
✓ Production gesture input
✓ EventBus
✅ All imports successful!
```

## 📝 Configuration

Edit `config/blender_mode.yaml`:

```yaml
inputs:
  gesture:
    use_production: true  # Production gestures
    gesture_sets:
      - basic     # 6 gestures
      - advanced  # 9 gestures
```

## 🎨 With Blender

1. Install Blender addon (one-time):
   - Open Blender
   - Edit → Preferences → Add-ons → Install
   - Select: `blender_addon/gesture_control_addon.py`
   - Enable it

2. Run demo:
   ```bash
   python demo_blender.py
   ```

3. Or run orchestrator directly:
   ```bash
   python main_orchestrator.py --config config/blender_mode.yaml
   ```

## ⌨️ Controls

- **ESC** in camera window: Exit
- **Ctrl+C** in terminal: Stop orchestrator

## 🐛 Troubleshooting

**Camera doesn't open?**
- Check camera permissions (System Preferences → Security)
- Try different camera: `--camera-index 1`

**Gestures not detected?**
- Lower confidence: Edit `min_confidence: 0.5` in config
- Better lighting helps
- Hand should be 30-60cm from camera

**Blender not responding?**
- Check addon is enabled
- Verify port 8888 not in use
- Look for "Listening on localhost:8888" in Blender console

## 📊 What Changed

- ✅ **macOS compatibility**: Camera runs in main thread
- ✅ **Production gestures**: 15+ robust gestures
- ✅ **Smooth tracking**: Landmark filtering
- ✅ **Auto-detection**: Platform-aware mode selection
- ✅ **Modular config**: Easy gesture set selection

## 🎓 Documentation

- [GESTURE_GUIDE.md](file:///Users/matte/MDS/Personal/lauzhack/GESTURE_GUIDE.md) - Full gesture reference
- [INTEGRATION_ANALYSIS.md](file:///Users/matte/MDS/Personal/lauzhack/INTEGRATION_ANALYSIS.md) - Technical details
- [DEMO_GUIDE.md](file:///Users/matte/MDS/Personal/lauzhack/DEMO_GUIDE.md) - Blender demo guide

---

**Status**: ✅ Production ready for macOS and other platforms!
