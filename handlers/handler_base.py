"""
Handler Base Classes

Base classes and protocols for gesture handlers with Pydantic configuration.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any, Protocol
from abc import ABC, abstractmethod
from bpy.types import Context
from pydantic import BaseModel, Field


class HandlerConfig(BaseModel):
    """Base configuration for all handlers."""
    enabled: bool = True
    cooldown: float = Field(0.1, ge=0.0)
    sensitivity: float = Field(1.0, gt=0.0)


class GestureHandlerProtocol(Protocol):
    """Protocol defining the interface for gesture handlers."""
    
    def can_handle(self, gesture: str) -> bool:
        """Check if handler supports this gesture."""
        ...
    
    def handle(self, context: Context, gesture: str, data: Dict[str, Any]) -> None:
        """Handle the gesture."""
        ...


class BaseHandler(ABC):
    """
    Base class for all gesture handlers.
    """
    
    def __init__(self, config: HandlerConfig):
        """
        Initialize handler with configuration.
        
        Args:
            config: Handler-specific configuration object
        """
        self.config = config
        self.last_trigger_time: float = 0.0
    
    @abstractmethod
    def can_handle(self, gesture: str) -> bool:
        pass
    
    @abstractmethod
    def handle(self, context: Context, gesture: str, data: Dict[str, Any]) -> None:
        pass
    
    def is_enabled(self) -> bool:
        return self.config.enabled
    
    def enable(self) -> None:
        self.config.enabled = True
    
    def disable(self) -> None:
        self.config.enabled = False
