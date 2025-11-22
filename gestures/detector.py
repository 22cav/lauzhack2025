"""
Gesture Detection Result and Detector Classes

Provides infrastructure for detecting and scoring gestures with confidence metrics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class GestureResult:
    """Result of a gesture detection."""
    
    name: str                           # Gesture name (e.g., "OPEN_PALM")
    confidence: float                    # Confidence score 0.0-1.0
    data: Dict[str, Any] = field(default_factory=dict)  # Additional data
    timestamp: float = field(default_factory=time.time)  # Detection time
    
    def __post_init__(self):
        """Validate confidence value."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    def __str__(self):
        return f"{self.name} ({self.confidence:.2f})"
    
    def __repr__(self):
        return f"GestureResult(name='{self.name}', confidence={self.confidence:.2f})"


class Gesture(ABC):
    """Abstract base class for gesture implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique gesture name."""
        pass
    
    @property
    def priority(self) -> int:
        """Detection priority (higher = checked first). Default: 0"""
        return 0
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return f"{self.name} gesture"
    
    @abstractmethod
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect gesture from landmarks.
        
        Args:
            landmarks: MediaPipe hand landmarks
            context: Additional context (previous gestures, hand side, etc.)
        
        Returns:
            GestureResult if detected with confidence > 0, None otherwise
        """
        pass


class GestureDetector:
    """
    Main gesture detection engine.
    
    Manages registered gestures, performs detection, and filters results
    based on confidence thresholds.
    """
    
    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize gesture detector.
        
        Args:
            min_confidence: Minimum confidence threshold for valid detection
        """
        self.gestures: List[Gesture] = []
        self.min_confidence = min_confidence
        self.detection_count = 0
        self.history: List[GestureResult] = []
        self.max_history = 30  # Keep last 30 detections
        
        logger.info(f"GestureDetector initialized with min_confidence={min_confidence}")
    
    def register(self, gesture: Gesture):
        """
        Register a gesture for detection.
        
        Args:
            gesture: Gesture instance to register
        """
        if not isinstance(gesture, Gesture):
            raise TypeError(f"Expected Gesture, got {type(gesture)}")
        
        # Check for duplicate names
        if any(g.name == gesture.name for g in self.gestures):
            logger.warning(f"Overwriting existing gesture: {gesture.name}")
            self.gestures = [g for g in self.gestures if g.name != gesture.name]
        
        self.gestures.append(gesture)
        # Sort by priority (highest first)
        self.gestures.sort(key=lambda g: g.priority, reverse=True)
        
        logger.debug(f"Registered gesture: {gesture.name} (priority={gesture.priority})")
    
    def unregister(self, gesture_name: str):
        """Remove a gesture from detection."""
        self.gestures = [g for g in self.gestures if g.name != gesture_name]
        logger.debug(f"Unregistered gesture: {gesture_name}")
    
    def detect(self, landmarks, context: Optional[Dict[str, Any]] = None) -> List[GestureResult]:
        """
        Detect all gestures from landmarks.
        
        Args:
            landmarks: MediaPipe hand landmarks
            context: Optional context dictionary
        
        Returns:
            List of GestureResult, sorted by confidence (highest first)
        """
        if landmarks is None:
            return []
        
        if context is None:
            context = {}
        
        # Add history to context
        context['history'] = self.history
        
        results = []
        
        # Detect all gestures
        for gesture in self.gestures:
            try:
                result = gesture.detect(landmarks, context)
                if result and result.confidence >= self.min_confidence:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error detecting {gesture.name}: {e}", exc_info=True)
        
        # Sort by confidence
        results.sort(key=lambda r: r.confidence, reverse=True)
        
        # Update statistics
        self.detection_count += 1
        
        # Update history with top result
        if results:
            self.history.append(results[0])
            if len(self.history) > self.max_history:
                self.history.pop(0)
        
        return results
    
    def detect_best(self, landmarks, context: Optional[Dict[str, Any]] = None) -> Optional[GestureResult]:
        """
        Detect the most confident gesture.
        
        Args:
            landmarks: MediaPipe hand landmarks
            context: Optional context dictionary
        
        Returns:
            Best GestureResult or None
        """
        results = self.detect(landmarks, context)
        return results[0] if results else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detection statistics."""
        gesture_counts = {}
        for result in self.history:
            gesture_counts[result.name] = gesture_counts.get(result.name, 0) + 1
        
        return {
            'total_detections': self.detection_count,
            'registered_gestures': len(self.gestures),
            'history_size': len(self.history),
            'gesture_counts': gesture_counts,
        }
    
    def reset(self):
        """Reset detection history and stats."""
        self.history.clear()
        self.detection_count = 0
        logger.info("Detector reset")
