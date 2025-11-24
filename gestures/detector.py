"""
Gesture Detector

Core gesture detection logic with Pydantic validation.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
from pydantic import BaseModel, Field, field_validator


class GestureResult(BaseModel):
    """
    Result of a gesture detection with validation.
    """
    name: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    
    class Config:
        frozen = True


class Gesture(ABC):
    """
    Abstract base class for gestures.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the gesture."""
        pass
    
    @abstractmethod
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect gesture from landmarks.
        
        Args:
            landmarks: MediaPipe landmarks
            context: Context dictionary
            
        Returns:
            GestureResult if detected, None otherwise
        """
        pass


class GestureDetector:
    """
    Manager for gesture detection.
    """
    
    def __init__(self, min_confidence: float = 0.5):
        self.gestures: List[Gesture] = []
        self.min_confidence = min_confidence
        self.history: List[GestureResult] = []
        self.max_history = 30
    
    def register(self, gesture: Gesture) -> None:
        """Register a new gesture."""
        self.gestures.append(gesture)
    
    def detect_best(self, landmarks: Any, context: Optional[Dict[str, Any]] = None) -> Optional[GestureResult]:
        """
        Detect the best matching gesture.
        
        Args:
            landmarks: MediaPipe landmarks
            context: Optional context
            
        Returns:
            Best matching GestureResult or None
        """
        # Safety check: ensure landmarks exist
        if landmarks is None:
            return None
        
        # Safety check: ensure we have registered gestures
        if not self.gestures:
            return None
        
        if context is None:
            context = {}
        
        best_result: Optional[GestureResult] = None
        max_confidence = 0.0
        
        for gesture in self.gestures:
            try:
                result = gesture.detect(landmarks, context)
                
                # Validate result
                if result and result.confidence >= self.min_confidence:
                    if result.confidence > max_confidence:
                        max_confidence = result.confidence
                        best_result = result
            except Exception as e:
                # Log error but continue with other gestures
                # Don't let one gesture crash the entire detection
                import logging
                logging.error(f"Error detecting gesture {gesture.name}: {e}")
                continue
        
        if best_result:
            self._update_history(best_result)
            
        return best_result
    
    def _update_history(self, result: GestureResult) -> None:
        """Update detection history."""
        self.history.append(result)
        if len(self.history) > self.max_history:
            self.history.pop(0)
