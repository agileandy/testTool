"""Tests for test script models."""

import pytest
from datetime import datetime
from testTool.models.test_script import TestScript, TestStep
from testTool.models.action import Action, ActionType


def test_test_script_creation():
    """Test creating a test script."""
    script = TestScript(
        name="test_login",
        description="Test login functionality",
        mode="dumb"
    )
    
    assert script.name == "test_login"
    assert script.description == "Test login functionality"
    assert script.mode == "dumb"
    assert len(script.steps) == 0
    assert isinstance(script.created_at, datetime)


def test_test_script_with_steps():
    """Test creating a script with steps."""
    steps = [
        TestStep(
            description="Navigate to login",
            action=Action(type=ActionType.NAVIGATE, value="https://example.com/login")
        ),
        TestStep(
            description="Click login button",
            action=Action(type=ActionType.CLICK, selector="button#login")
        )
    ]
    
    script = TestScript(
        name="login_test",
        description="Login test",
        steps=steps
    )
    
    assert len(script.steps) == 2
    assert script.steps[0].description == "Navigate to login"
    assert script.steps[1].action.type == ActionType.CLICK


def test_test_script_serialization():
    """Test script serialization."""
    script = TestScript(
        name="test",
        description="Test script",
        steps=[
            TestStep(
                description="Step 1",
                action=Action(type=ActionType.CLICK, selector="button")
            )
        ],
        metadata={"browser": "chromium"}
    )
    
    data = script.model_dump()
    
    assert data["name"] == "test"
    assert data["metadata"]["browser"] == "chromium"
    assert len(data["steps"]) == 1
    
    # Can recreate
    new_script = TestScript(**data)
    assert new_script.name == script.name
    assert len(new_script.steps) == 1
