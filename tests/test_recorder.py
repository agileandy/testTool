"""Tests for test recorder."""

import pytest
from testTool.recorder import TestRecorder
from testTool.models.action import Action, ActionType


def test_recorder_creation():
    """Test creating a recorder."""
    recorder = TestRecorder()
    assert recorder is not None
    assert not recorder.is_recording()


def test_start_stop_recording():
    """Test starting and stopping recording."""
    recorder = TestRecorder()
    
    recorder.start_recording("test", "Test description", mode="dumb")
    assert recorder.is_recording()
    
    script = recorder.stop_recording()
    assert not recorder.is_recording()
    assert script.name == "test"
    assert script.description == "Test description"


def test_record_steps():
    """Test recording steps."""
    recorder = TestRecorder()
    recorder.start_recording("test", "Test")
    
    recorder.record_step(
        description="Click button",
        action=Action(type=ActionType.CLICK, selector="button")
    )
    
    recorder.record_step(
        description="Type text",
        action=Action(type=ActionType.TYPE, selector="input", value="test")
    )
    
    script = recorder.stop_recording()
    
    assert len(script.steps) == 2
    assert script.steps[0].description == "Click button"
    assert script.steps[1].action.value == "test"


def test_record_with_metadata():
    """Test recording with metadata."""
    recorder = TestRecorder()
    recorder.start_recording("test", "Test")
    
    recorder.add_metadata("browser", "chromium")
    recorder.add_metadata("viewport", "1280x720")
    
    script = recorder.stop_recording()
    
    assert script.metadata["browser"] == "chromium"
    assert script.metadata["viewport"] == "1280x720"


def test_recording_not_started_error():
    """Test error when recording not started."""
    recorder = TestRecorder()
    
    with pytest.raises(RuntimeError):
        recorder.record_step(
            description="Test",
            action=Action(type=ActionType.CLICK, selector="button")
        )


def test_stop_without_start_error():
    """Test error when stopping without starting."""
    recorder = TestRecorder()
    
    with pytest.raises(RuntimeError):
        recorder.stop_recording()
