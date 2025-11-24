"""
Handler Base Classes
"""

from typing import Dict, Any
from abc import ABC, abstractmethod
from bpy.types import Context


class BaseHandler(ABC):
    """Base class for all gesture handlers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config: Dict[str, Any] = config
        self.enabled: bool = True
    
    @abstractmethod
    def can_handle(self, gesture: str) -> bool:
        pass
    
    @abstractmethod
    def handle(self, context: Context, gesture: str, data: Dict[str, Any]) -> None:
        pass
