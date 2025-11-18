"""Tests for script storage."""

import pytest
import tempfile
from pathlib import Path
from testTool.recorder import ScriptStorage
from testTool.models.test_script import TestScript, TestStep
from testTool.models.action import Action, ActionType


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield ScriptStorage(storage_dir=tmpdir)


def test_storage_creation(temp_storage):
    """Test creating storage."""
    assert temp_storage is not None
    assert temp_storage.storage_dir.exists()


def test_save_and_load_json(temp_storage):
    """Test saving and loading JSON scripts."""
    script = TestScript(
        name="test_script",
        description="Test",
        steps=[
            TestStep(
                description="Click",
                action=Action(type=ActionType.CLICK, selector="button")
            )
        ]
    )
    
    # Save
    filepath = temp_storage.save(script, format='json')
    assert filepath.exists()
    
    # Load
    loaded = temp_storage.load("test_script", format='json')
    assert loaded.name == script.name
    assert len(loaded.steps) == 1
    assert loaded.steps[0].action.type == ActionType.CLICK


def test_save_and_load_yaml(temp_storage):
    """Test saving and loading YAML scripts."""
    script = TestScript(
        name="yaml_test",
        description="YAML Test",
        steps=[
            TestStep(
                description="Navigate",
                action=Action(type=ActionType.NAVIGATE, value="https://example.com")
            )
        ]
    )
    
    # Save
    filepath = temp_storage.save(script, format='yaml')
    assert filepath.exists()
    
    # Load
    loaded = temp_storage.load("yaml_test", format='yaml')
    assert loaded.name == script.name
    assert loaded.steps[0].action.value == "https://example.com"


def test_list_scripts(temp_storage):
    """Test listing scripts."""
    # Create multiple scripts
    for i in range(3):
        script = TestScript(name=f"test_{i}", description="Test")
        temp_storage.save(script)
    
    scripts = temp_storage.list_scripts()
    assert len(scripts) >= 3
    assert "test_0" in scripts


def test_delete_script(temp_storage):
    """Test deleting a script."""
    script = TestScript(name="delete_me", description="Test")
    temp_storage.save(script)
    
    assert temp_storage.exists("delete_me")
    
    deleted = temp_storage.delete("delete_me")
    assert deleted
    assert not temp_storage.exists("delete_me")


def test_script_not_found(temp_storage):
    """Test loading non-existent script."""
    with pytest.raises(FileNotFoundError):
        temp_storage.load("nonexistent")


def test_exists(temp_storage):
    """Test checking if script exists."""
    assert not temp_storage.exists("test")
    
    script = TestScript(name="test", description="Test")
    temp_storage.save(script)
    
    assert temp_storage.exists("test")
