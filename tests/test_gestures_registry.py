import pytest
from gestures.registry import GestureRegistry, get_registry, register
from gestures.detector import Gesture

class DummyGesture(Gesture):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, landmarks, context):
        return None

def test_registry_register_and_retrieve():
    registry = GestureRegistry()
    registry.register_gesture(DummyGesture, set_name="test_set")
    # Retrieve class
    cls = registry.get_gesture("dummy")
    assert cls is DummyGesture
    # Create instance
    instance = registry.create_gesture("dummy")
    assert isinstance(instance, DummyGesture)
    # List gestures and sets
    assert "dummy" in registry.list_gestures()
    assert "test_set" in registry.list_sets()
    # Get set returns instances
    gestures = registry.get_set("test_set")
    assert len(gestures) == 1
    assert isinstance(gestures[0], DummyGesture)
    # Metadata
    meta = registry.get_metadata("dummy")
    assert meta["name"] == "dummy"
    # Clear
    registry.clear()
    assert registry.list_gestures() == []
    assert registry.list_sets() == []

def test_global_registry_decorator():
    @register(set_name="global")
    class GlobalDummy(Gesture):
        @property
        def name(self) -> str:
            return "global_dummy"
        def detect(self, landmarks, context):
            return None
    global_reg = get_registry()
    assert "global_dummy" in global_reg.list_gestures()
    assert "global" in global_reg.list_sets()
    instance = global_reg.create_gesture("global_dummy")
    assert isinstance(instance, GlobalDummy)
