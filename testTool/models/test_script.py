"""Test script models."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .action import Action


class TestStep(BaseModel):
    """A single step in a test script."""
    
    description: str = Field(..., description="Human-readable description of the step")
    action: Action = Field(..., description="The action to perform")
    expected_outcome: Optional[str] = Field(None, description="Expected outcome description")
    screenshot: bool = Field(default=False, description="Whether to take screenshot after step")


class TestScript(BaseModel):
    """A complete test script."""
    
    name: str = Field(..., description="Test script name")
    description: str = Field(..., description="Test script description")
    mode: str = Field(default="dumb", description="Mode: 'dumb' or 'smart'")
    steps: List[TestStep] = Field(default_factory=list, description="Test steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Script metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
