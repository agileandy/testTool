"""Test recorder for capturing browser interactions."""

import time
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..models.action import Action
from ..models.test_script import TestScript, TestStep


class TestRecorder:
    """
    Records browser interactions to create deterministic test scripts.
    
    Captures:
    - Actions performed
    - DOM state snapshots
    - Screenshots
    - Timing information
    - Metadata for reproducibility
    """
    
    def __init__(self, output_dir: str = "./test_scripts"):
        """
        Initialize the test recorder.
        
        Args:
            output_dir: Directory to save recorded test scripts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.recording = False
        self.current_script: Optional[TestScript] = None
        self.recorded_steps: List[TestStep] = []
        
    def start_recording(self, name: str, description: str, mode: str = "dumb"):
        """
        Start recording a new test script.
        
        Args:
            name: Test script name
            description: Test script description
            mode: Operating mode ('dumb' or 'smart')
        """
        self.recording = True
        self.current_script = TestScript(
            name=name,
            description=description,
            mode=mode,
            steps=[]
        )
        self.recorded_steps = []
        
    def record_step(
        self,
        description: str,
        action: Action,
        expected_outcome: Optional[str] = None,
        screenshot: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a single test step.
        
        Args:
            description: Human-readable step description
            action: The action performed
            expected_outcome: Expected outcome description
            screenshot: Whether screenshot was taken
            metadata: Additional step metadata
        """
        if not self.recording:
            raise RuntimeError("Recording not started. Call start_recording() first.")
        
        # Enhance action metadata with recording context
        if metadata:
            action.metadata.update(metadata)
        
        step = TestStep(
            description=description,
            action=action,
            expected_outcome=expected_outcome,
            screenshot=screenshot
        )
        
        self.recorded_steps.append(step)
        
    def stop_recording(self) -> TestScript:
        """
        Stop recording and return the completed test script.
        
        Returns:
            The recorded TestScript
        """
        if not self.recording:
            raise RuntimeError("No active recording.")
        
        self.current_script.steps = self.recorded_steps
        self.recording = False
        
        script = self.current_script
        self.current_script = None
        self.recorded_steps = []
        
        return script
    
    def add_metadata(self, key: str, value: Any):
        """
        Add metadata to the current recording.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if not self.recording or not self.current_script:
            raise RuntimeError("No active recording.")
        
        self.current_script.metadata[key] = value
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording
