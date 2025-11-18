"""Tests for pattern learner."""

import pytest
import tempfile
from testTool.learning_layer import PatternLearner
from testTool.models.test_script import TestScript, TestStep
from testTool.models.action import Action, ActionType


@pytest.fixture
def temp_learner():
    """Create a learner with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield PatternLearner(knowledge_base_path=tmpdir)


def test_learner_creation(temp_learner):
    """Test creating a pattern learner."""
    assert temp_learner is not None


def test_observe_script(temp_learner):
    """Test observing a script."""
    script = TestScript(
        name="test",
        description="Test script",
        steps=[
            TestStep(
                description="Navigate",
                action=Action(type=ActionType.NAVIGATE, value="https://example.com")
            ),
            TestStep(
                description="Click",
                action=Action(type=ActionType.CLICK, selector="button")
            )
        ]
    )
    
    temp_learner.observe_script(script)
    
    patterns = temp_learner.get_common_patterns(min_count=1)
    assert len(patterns) > 0


def test_common_patterns(temp_learner):
    """Test finding common patterns."""
    # Create multiple similar scripts
    for i in range(3):
        script = TestScript(
            name=f"test_{i}",
            description="Login test",
            steps=[
                TestStep(
                    description="Navigate to login",
                    action=Action(type=ActionType.NAVIGATE, value="https://example.com/login")
                ),
                TestStep(
                    description="Click login",
                    action=Action(type=ActionType.CLICK, selector="button#login")
                )
            ]
        )
        temp_learner.observe_script(script)
    
    patterns = temp_learner.get_common_patterns(min_count=2)
    assert len(patterns) > 0
    assert patterns[0]["count"] >= 2


def test_suggest_selector(temp_learner):
    """Test selector suggestion."""
    script = TestScript(
        name="test",
        description="Test",
        steps=[
            TestStep(
                description="Click button",
                action=Action(type=ActionType.CLICK, selector="button#submit")
            )
        ]
    )
    
    temp_learner.observe_script(script)
    
    suggestion = temp_learner.suggest_selector("click", "Click button")
    assert suggestion == "button#submit"


def test_find_similar_workflows(temp_learner):
    """Test finding similar workflows."""
    script = TestScript(
        name="login_workflow",
        description="User login workflow",
        steps=[
            TestStep(
                description="Navigate",
                action=Action(type=ActionType.NAVIGATE, value="https://example.com")
            ),
            TestStep(
                description="Login",
                action=Action(type=ActionType.CLICK, selector="button")
            ),
            TestStep(
                description="Verify",
                action=Action(type=ActionType.ASSERT_TEXT, selector="h1", text="Welcome")
            )
        ]
    )
    
    temp_learner.observe_script(script)
    
    similar = temp_learner.find_similar_workflows("user login")
    assert len(similar) > 0
    assert similar[0]["name"] == "login_workflow"
