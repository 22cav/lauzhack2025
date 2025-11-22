# Gesture Sensitivity Tuning Guide

## Quick Adjustments

Edit `config/blender_mode.yaml` to tune gesture detection:

### For MORE Sensitive (Easier Detection)

```yaml
inputs:
  gesture:
    min_detection_confidence: 0.3  # Lower = easier hand detection
    min_tracking_confidence: 0.3   # Lower = better tracking
    min_confidence: 0.4            # Lower = more gestures detected
    stability_frames: 1            # Lower = faster response
```

### For LESS Sensitive (Fewer False Positives)

```yaml
inputs:
  gesture:
    min_detection_confidence: 0.7  # Higher = only clear hands
    min_tracking_confidence: 0.7   # Higher = stable tracking only
    min_confidence: 0.8            # Higher = only confident gestures
    stability_frames: 3            # Higher = must hold gesture longer
```

## Current Settings (Balanced - Easy Detection)

```yaml
min_detection_confidence: 0.3  # Easy to detect hands
min_tracking_confidence: 0.3   # Maintains tracking well
min_confidence: 0.4            # Gestures detected easily
stability_frames: 1            # Quick response
filter_window: 3               # Light smoothing
```

## Parameter Explanations

### `min_detection_confidence` (0.0-1.0)
**What it does**: How confident MediaPipe must be to detect a hand  
**Lower (0.3)**: Detects hands in poor lighting, far from camera  
**Higher (0.7)**: Only detects clear, close hands  
**Recommended**: 0.3-0.5

### `min_tracking_confidence` (0.0-1.0)
**What it does**: How confident MediaPipe must be to continue tracking  
**Lower (0.3)**: Maintains tracking even when hand partially obscured  
**Higher (0.7)**: Loses tracking if hand moves fast or gets blurry  
**Recommended**: 0.3-0.5

### `min_confidence` (0.0-1.0)
**What it does**: Minimum gesture confidence to publish event  
**Lower (0.4)**: More gestures detected, some false positives  
**Higher (0.8)**: Only very clear gestures, may miss some  
**Recommended**: 0.4-0.6

### `stability_frames` (1-5)
**What it does**: How many consecutive frames gesture must be detected  
**Lower (1)**: Instant response, may flicker between gestures  
**Higher (3)**: Must hold gesture steady, very stable  
**Recommended**: 1-2

### `filter_window` (3-7)
**What it does**: Smoothing window size for landmark positions  
**Lower (3)**: Faster response, less smooth  
**Higher (7)**: Smoother motion, slight lag  
**Recommended**: 3-5

## Troubleshooting

### "Gestures not detected at all"
- Lower `min_confidence` to 0.3
- Lower `min_detection_confidence` to 0.3
- Set `stability_frames` to 1
- Improve lighting
- Move hand closer to camera (30-60cm)

### "Wrong gestures detected"
- Raise `min_confidence` to 0.7
- Raise `stability_frames` to 3
- Increase `filter_window` to 5
- Make gestures more distinct and deliberate

### "Gestures flicker/unstable"
- Increase `stability_frames` to 2-3
- Increase `filter_window` to 5-7
- Ensure good lighting
- Keep hand steady

### "Slow response"
- Decrease `stability_frames` to 1
- Decrease `filter_window` to 3
- Ensure good CPU performance

## Testing Your Settings

After editing config, run:
```bash
python main_orchestrator.py --config config/blender_mode.yaml
```

Watch the terminal for gesture events:
```
INFO:outputs.blender_output:Blender command: {"command": "play_animation", ...}
```

If you see these appearing when you do gestures, it's working!

## Recommended Presets

### Preset 1: Easy Detection (Current)
```yaml
min_detection_confidence: 0.3
min_tracking_confidence: 0.3
min_confidence: 0.4
stability_frames: 1
filter_window: 3
```
**Best for**: Testing, demos, varied lighting

### Preset 2: Balanced
```yaml
min_detection_confidence: 0.5
min_tracking_confidence: 0.5
min_confidence: 0.6
stability_frames: 2
filter_window: 5
```
**Best for**: Production use, good lighting

### Preset 3: High Precision
```yaml
min_detection_confidence: 0.7
min_tracking_confidence: 0.7
min_confidence: 0.8
stability_frames: 3
filter_window: 5
```
**Best for**: No false positives, willing to miss some gestures
