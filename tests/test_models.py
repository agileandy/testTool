"""Tests for action models."""

import pytest
from testTool.models.action import Action, ActionType


def test_action_creation():
    """Test creating a basic action."""
    action = Action(
        type=ActionType.CLICK,
        selector="button#submit"
    )
    
    assert action.type == ActionType.CLICK
    assert action.selector == "button#submit"
    assert action.timeout == 30000  # default


def test_navigate_action():
    """Test navigate action."""
    action = Action(
        type=ActionType.NAVIGATE,
        value="https://example.com"
    )
    
    assert action.type == ActionType.NAVIGATE
    assert action.value == "https://example.com"


def test_type_action():
    """Test type action."""
    action = Action(
        type=ActionType.TYPE,
        selector="input[name='username']",
        value="admin"
    )
    
    assert action.type == ActionType.TYPE
    assert action.selector == "input[name='username']"
    assert action.value == "admin"


def test_action_metadata():
    """Test action with metadata."""
    action = Action(
        type=ActionType.CLICK,
        selector="button",
        metadata={"context": "login"}
    )
    
    assert action.metadata["context"] == "login"


def test_action_serialization():
    """Test action can be serialized."""
    action = Action(
        type=ActionType.ASSERT_TEXT,
        selector="h1",
        text="Welcome"
    )
    
    data = action.model_dump()
    
    assert data["type"] == "assert_text"
    assert data["selector"] == "h1"
    assert data["text"] == "Welcome"
    
    # Can recreate from dict
    new_action = Action(**data)
    assert new_action.type == action.type
