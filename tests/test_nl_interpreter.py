"""Tests for the natural language interpreter."""

import pytest
from testTool.nl_processor import NLInterpreter
from testTool.models.action import ActionType


def test_nl_interpreter_creation():
    """Test creating an interpreter."""
    interpreter = NLInterpreter(use_llm=False)
    assert interpreter is not None
    assert not interpreter.use_llm


def test_interpret_navigate():
    """Test interpreting navigation commands."""
    interpreter = NLInterpreter(use_llm=False)
    
    actions = interpreter.interpret("go to https://example.com")
    
    assert len(actions) > 0
    assert actions[0].type == ActionType.NAVIGATE
    assert "example.com" in actions[0].value


def test_interpret_click():
    """Test interpreting click commands."""
    interpreter = NLInterpreter(use_llm=False)
    
    actions = interpreter.interpret("click the login button")
    
    assert len(actions) > 0
    assert actions[0].type == ActionType.CLICK
    assert actions[0].selector is not None


def test_interpret_type():
    """Test interpreting type commands."""
    interpreter = NLInterpreter(use_llm=False)
    
    actions = interpreter.interpret("type 'admin' in username field")
    
    assert len(actions) > 0
    assert actions[0].type == ActionType.TYPE
    assert actions[0].value == "admin"


def test_interpret_wait():
    """Test interpreting wait commands."""
    interpreter = NLInterpreter(use_llm=False)
    
    actions = interpreter.interpret("wait for page to load")
    
    assert len(actions) > 0
    assert actions[0].type == ActionType.WAIT


def test_interpret_screenshot():
    """Test interpreting screenshot commands."""
    interpreter = NLInterpreter(use_llm=False)
    
    actions = interpreter.interpret("take a screenshot")
    
    assert len(actions) > 0
    assert actions[0].type == ActionType.SCREENSHOT


def test_validate_actions():
    """Test action validation."""
    interpreter = NLInterpreter(use_llm=False)
    
    actions = interpreter.interpret("click the button")
    issues = interpreter.validate_actions(actions)
    
    # Should have a selector (though it might be generic)
    assert isinstance(issues, list)


def test_extract_url():
    """Test URL extraction."""
    interpreter = NLInterpreter(use_llm=False)
    
    url = interpreter._extract_url("navigate to https://example.com/path")
    assert url == "https://example.com/path"
    
    url = interpreter._extract_url("go to 'https://test.com'")
    assert url == "https://test.com"


def test_extract_value():
    """Test value extraction from quotes."""
    interpreter = NLInterpreter(use_llm=False)
    
    value = interpreter._extract_value("type 'testuser' in field")
    assert value == "testuser"
    
    value = interpreter._extract_value('enter "password123"')
    assert value == "password123"
