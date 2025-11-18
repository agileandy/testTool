"""Action models representing browser interactions."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Types of browser actions."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    WAIT = "wait"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    ASSERT_TEXT = "assert_text"
    ASSERT_ELEMENT = "assert_element"
    EXTRACT = "extract"


class Action(BaseModel):
    """Represents a single browser action."""
    
    type: ActionType = Field(..., description="Type of action to perform")
    selector: Optional[str] = Field(None, description="CSS selector or XPath for element")
    value: Optional[str] = Field(None, description="Value for typing, selecting, or URL")
    text: Optional[str] = Field(None, description="Text to verify or extract")
    timeout: int = Field(default=30000, description="Timeout in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional action metadata")
    
    class Config:
        use_enum_values = True
