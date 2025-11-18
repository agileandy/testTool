"""Test executor for deterministic playback of test scripts."""

import time
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from ..models.test_script import TestScript
from ..models.execution_result import ExecutionResult, StepResult
from ..browser_control.playwright_controller import PlaywrightController


class TestExecutor:
    """
    Executes test scripts deterministically.
    
    Ensures:
    - Same script produces same execution sequence
    - Proper error handling and reporting
    - Detailed execution logs
    """
    
    def __init__(
        self,
        headless: bool = True,
        screenshots_dir: str = "./screenshots",
        results_dir: str = "./test_results"
    ):
        """
        Initialize the test executor.
        
        Args:
            headless: Whether to run browser in headless mode
            screenshots_dir: Directory for screenshots
            results_dir: Directory for execution results
        """
        self.headless = headless
        self.screenshots_dir = Path(screenshots_dir)
        self.results_dir = Path(results_dir)
        
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.controller: Optional[PlaywrightController] = None
    
    async def execute(self, script: TestScript) -> ExecutionResult:
        """
        Execute a test script and return results.
        
        Args:
            script: The test script to execute
            
        Returns:
            ExecutionResult with detailed execution information
        """
        start_time = time.time()
        step_results = []
        all_success = True
        
        # Initialize browser controller
        self.controller = PlaywrightController(
            headless=self.headless,
            screenshots_dir=str(self.screenshots_dir)
        )
        
        try:
            await self.controller.start()
            
            # Execute each step
            for i, step in enumerate(script.steps):
                step_result = await self._execute_step(i, step)
                step_results.append(step_result)
                
                if not step_result.success:
                    all_success = False
                    # Optionally stop on first failure
                    # break
            
        finally:
            # Always cleanup
            if self.controller:
                await self.controller.stop()
        
        total_duration = (time.time() - start_time) * 1000
        
        result = ExecutionResult(
            script_name=script.name,
            success=all_success,
            step_results=step_results,
            total_duration_ms=total_duration
        )
        
        # Save result
        self._save_result(result)
        
        return result
    
    async def _execute_step(self, index: int, step) -> StepResult:
        """Execute a single test step."""
        step_start = time.time()
        
        try:
            # Execute the action
            action_result = await self.controller.execute_action(step.action)
            
            # Capture screenshot if requested
            screenshot_path = None
            if step.screenshot:
                screenshot_path = str(
                    await self.controller._screenshot(f"step_{index}")
                )
            
            # Get DOM snapshot hash for verification
            dom_snapshot = await self.controller.get_dom_snapshot()
            
            duration = (time.time() - step_start) * 1000
            
            return StepResult(
                step_index=index,
                success=action_result["success"],
                error=action_result.get("error"),
                screenshot_path=screenshot_path,
                dom_snapshot=dom_snapshot,
                duration_ms=duration,
                metadata=action_result.get("metadata", {})
            )
            
        except Exception as e:
            duration = (time.time() - step_start) * 1000
            return StepResult(
                step_index=index,
                success=False,
                error=str(e),
                screenshot_path=None,
                dom_snapshot=None,
                duration_ms=duration,
                metadata={}
            )
    
    def _save_result(self, result: ExecutionResult):
        """Save execution result to file."""
        import json
        
        filename = f"{result.script_name}_{int(time.time())}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(result.model_dump(), f, indent=2, default=str)
    
    def execute_sync(self, script: TestScript) -> ExecutionResult:
        """
        Synchronous wrapper for execute().
        
        Args:
            script: The test script to execute
            
        Returns:
            ExecutionResult
        """
        return asyncio.run(self.execute(script))
