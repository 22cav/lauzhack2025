#!/usr/bin/env python3
"""
Production Gesture Recognition Demo

Tests the new production gesture system with all implemented gestures.
Runs in main thread for macOS compatibility.
"""

import cv2
import mediapipe as mp
import sys
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).parent))

from gestures import GestureDetector, GestureRegistry
from gestures.filters import LandmarkFilter
from gestures.validators import ConfidenceValidator, QualityValidator
from gestures.library import basic, advanced

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def main():
    print("="*70)
    print("🚀 PRODUCTION GESTURE RECOGNITION DEMO")
    print("="*70)
    print("\n📋 Available Gestures:")
    print("\n✋ Basic Gestures:")
    print("   • Open Palm • Closed Fist • Pointing")
    print("   • Peace Sign • Thumbs Up • Rock On")
    print("\n🤏 Advanced Gestures:")
    print("   • Pinch • Pinch & Drag")
    print("   • Swipe (Left/Right/Up/Down)")
    print("   • Rotate Clockwise • Wave")
    print("\n🎯 Features:")
    print("   • Confidence scoring (0.0-1.0)")
    print("   • Landmark smoothing")
    print("   • Quality validation")
    print("\n⌨️  Press ESC to exit")
    print("="*70)
    
    # Initialize detector
    detector = GestureDetector(min_confidence=0.6)
    
    # Get registry and load all gestures
    registry = GestureRegistry()
    
    # Register from basic module
    for attr_name in dir(basic):
        attr = getattr(basic, attr_name)
        if isinstance(attr, type) and hasattr(attr, 'detect'):
            try:
                gesture = attr()
                detector.register(gesture)
                print(f"   ✓ Registered: {gesture.name}")
            except:
                pass
    
    # Register from advanced module
    for attr_name in dir(advanced):
        attr = getattr(advanced, attr_name)
        if isinstance(attr, type) and hasattr(attr, 'detect'):
            try:
                gesture = attr()
                detector.register(gesture)
                print(f"   ✓ Registered: {gesture.name}")
            except:
                pass
    
    print(f"\n✅ Loaded {len(detector.gestures)} gestures")
    print("\n🎬 Starting camera...\n")
    
    # Initialize filters and validators
    landmark_filter = LandmarkFilter(window_size=3)
    quality_validator = QualityValidator()
    confidence_validator = ConfidenceValidator(min_confidence=0.6, stability_frames=2)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera!")
        return 1
    
    print("✅ Camera opened - window should appear now!\n")
    
    # Track statistics
    frame_count = 0
    detected_gestures = set()
    
    # Run detection
    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:
        
        while True:
            success, image = cap.read()
            if not success:
                continue
            
            frame_count += 1
            
            # Process frame
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)
            
            # Convert back for display
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Draw landmarks
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            mp_drawing.draw_landmarks(
                image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(
                image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            
            # Detect gestures
            hand_landmarks = results.right_hand_landmarks or results.left_hand_landmarks
            
            current_gesture = "UNKNOWN"
            confidence = 0.0
            
            if hand_landmarks:
                # Validate quality
                if quality_validator.validate(hand_landmarks):
                    # Smooth landmarks
                    smoothed_landmarks = landmark_filter.update(hand_landmarks)
                    
                    # Detect best gesture
                    gesture_result = detector.detect_best(smoothed_landmarks)
                    
                    if gesture_result:
                        # Validate confidence
                        if confidence_validator.validate(gesture_result):
                            current_gesture = gesture_result.name
                            confidence = gesture_result.confidence
                            detected_gestures.add(current_gesture)
            
            # Display information
            y_offset = 30
            
            # Current gesture
            color = (0, 255, 0) if current_gesture != "UNKNOWN" else (128, 128, 128)
            cv2.putText(image, f"Gesture: {current_gesture}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
            y_offset += 40
            
            # Confidence
            if confidence > 0:
                conf_color = (0, int(255 * confidence), int(255 * (1 - confidence)))
                cv2.putText(image, f"Confidence: {confidence:.2f}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, conf_color, 2)
                y_offset += 35
            
            # Stats
            cv2.putText(image, f"Gestures found: {len(detected_gestures)}/{len(detector.gestures)}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            y_offset += 30
            
            cv2.putText(image, f"Frame: {frame_count}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Instructions
            cv2.putText(image, "Press ESC to exit", 
                       (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show image
            cv2.imshow('Production Gesture Recognition', image)
            
            # Check for exit
            if cv2.waitKey(5) & 0xFF == 27:  # ESC key
                break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Print statistics
    print("\n" + "="*70)
    print("📊 STATISTICS")
    print("="*70)
    print(f"Total frames: {frame_count}")
    print(f"Gestures detected: {len(detected_gestures)}/{len(detector.gestures)}")
    print(f"\n✓ Detected gestures:")
    for gesture in sorted(detected_gestures):
        print(f"   • {gesture}")
    
    stats = detector.get_stats()
    print(f"\n📈 Detection stats:")
    print(f"   Total detections: {stats['total_detections']}")
    if stats['gesture_counts']:
        print(f"   Most common:")
        for gesture, count in sorted(stats['gesture_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {gesture}: {count} times")
    
    print("\n✅ Demo complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
