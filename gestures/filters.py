"""
Gesture Filters

Temporal filters for smoothing gesture data with Pydantic configuration.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any, Optional
import time
import math
from pydantic import BaseModel, Field


class FilterConfig(BaseModel):
    """Configuration for OneEuroFilter."""
    min_cutoff: float = Field(1.0, gt=0.0)
    beta: float = Field(0.0, ge=0.0)
    d_cutoff: float = Field(1.0, gt=0.0)


class OneEuroFilter:
    """
    OneEuroFilter for smoothing noisy signals.
    """
    
    def __init__(self, config: FilterConfig):
        self.config = config
        self.x_filter = LowPassFilter(alpha=1.0)
        self.dx_filter = LowPassFilter(alpha=1.0)
        self.last_time: Optional[float] = None
        
    def filter(self, value: float, timestamp: float = -1.0) -> float:
        """
        Apply one euro filter to value.
        
        Args:
            value: Value to filter
            timestamp: Optional timestamp (current time if not provided)
            
        Returns:
            Filtered value
        """
        if timestamp < 0:
            timestamp = time.time()
        
        # Safety check: handle NaN or infinite values
        if not isinstance(value, (int, float)) or value != value:  # NaN check
            return self.x_filter.last_value if self.x_filter.initialized else 0.0
            
        if self.last_time is None:
            self.last_time = timestamp
            return self.x_filter.filter(value)
            
        dt = timestamp - self.last_time
        
        # Safety check: prevent division by zero or negative dt
        if dt <= 0:
            return self.x_filter.last_value if self.x_filter.initialized else value
        
        # Prevent extremely large dt (likely clock jump)
        if dt > 1.0:  # More than 1 second gap
            # Reset filter
            self.last_time = timestamp
            return self.x_filter.filter(value)
            
        self.last_time = timestamp
        
        # Calculate derivative
        dx = (value - self.x_filter.last_value) / dt if self.x_filter.initialized else 0.0
        
        cutoff = self._alpha(self.dx_filter.filter(dx))
        
        return self.x_filter.filter(value, alpha=self._get_alpha(dt, cutoff))

    def _alpha(self, cutoff: float) -> float:
        """Calculate alpha from cutoff frequency."""
        # Safety check: ensure cutoff is positive
        if cutoff <= 0:
            cutoff = 0.001
        te = 1.0 / 30.0  # Assumed 30fps if dt not available
        tau = 1.0 / (2 * 3.14159265359 * cutoff)
        return 1.0 / (1.0 + tau / te)

    def _get_alpha(self, dt: float, cutoff: float) -> float:
        """Calculate alpha from dt and cutoff frequency."""
        # Safety checks
        if dt <= 0:
            dt = 1.0 / 30.0
        if cutoff <= 0:
            cutoff = 0.001
        tau = 1.0 / (2 * 3.14159265359 * cutoff)
        return 1.0 / (1.0 + tau / dt)


class LowPassFilter:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.last_value = 0.0
        self.initialized = False
        
    def filter(self, value: float, alpha: Optional[float] = None) -> float:
        if alpha is None:
            alpha = self.alpha
            
        if not self.initialized:
            self.last_value = value
            self.initialized = True
            return value
            
        self.last_value = alpha * value + (1.0 - alpha) * self.last_value
        return self.last_value
