"""Execution result models."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class StepResult(BaseModel):
    """Result of executing a single test step."""
    
    step_index: int = Field(..., description="Index of the step")
    success: bool = Field(..., description="Whether step succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")
    screenshot_path: Optional[str] = Field(None, description="Path to screenshot")
    dom_snapshot: Optional[str] = Field(None, description="DOM snapshot hash")
    duration_ms: float = Field(..., description="Execution duration in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional result data")


class ExecutionResult(BaseModel):
    """Result of executing a complete test script."""
    
    script_name: str = Field(..., description="Name of executed script")
    success: bool = Field(..., description="Whether all steps succeeded")
    step_results: List[StepResult] = Field(default_factory=list, description="Results for each step")
    total_duration_ms: float = Field(..., description="Total execution duration")
    executed_at: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
