"""Playwright-based browser controller for deterministic browser automation."""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from ..models.action import Action, ActionType


class PlaywrightController:
    """
    Deterministic browser controller using Playwright.
    
    Ensures consistent execution by:
    - Using stable selectors (data-testid preferred)
    - Enforcing explicit waits
    - Capturing deterministic state snapshots
    """
    
    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        screenshots_dir: str = "./screenshots"
    ):
        """
        Initialize the browser controller.
        
        Args:
            headless: Whether to run in headless mode
            browser_type: Browser type (chromium, firefox, webkit)
            screenshots_dir: Directory to store screenshots
        """
        self.headless = headless
        self.browser_type = browser_type
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def start(self):
        """Start the browser instance."""
        self.playwright = await async_playwright().start()
        
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = await browser_launcher.launch(headless=self.headless)
        
        # Create context with deterministic viewport
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="TestTool/1.0 (Deterministic Testing)"
        )
        
        self.page = await self.context.new_page()
        
        # Set deterministic timeouts
        self.page.set_default_timeout(30000)
        
    async def stop(self):
        """Stop the browser instance."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def execute_action(self, action: Action) -> Dict[str, Any]:
        """
        Execute a single browser action deterministically.
        
        Args:
            action: The action to execute
            
        Returns:
            Dictionary with execution results and metadata
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        start_time = time.time()
        result = {"success": True, "metadata": {}}
        
        try:
            if action.type == ActionType.NAVIGATE:
                await self._navigate(action.value)
                result["metadata"]["url"] = action.value
                
            elif action.type == ActionType.CLICK:
                await self._click(action.selector, action.timeout)
                result["metadata"]["selector"] = action.selector
                
            elif action.type == ActionType.TYPE:
                await self._type(action.selector, action.value, action.timeout)
                result["metadata"]["selector"] = action.selector
                
            elif action.type == ActionType.SELECT:
                await self._select(action.selector, action.value, action.timeout)
                result["metadata"]["selector"] = action.selector
                
            elif action.type == ActionType.WAIT:
                await self._wait(action.value or "load", action.timeout)
                result["metadata"]["wait_type"] = action.value
                
            elif action.type == ActionType.SCROLL:
                await self._scroll(action.selector, action.timeout)
                result["metadata"]["selector"] = action.selector
                
            elif action.type == ActionType.SCREENSHOT:
                path = await self._screenshot(action.value)
                result["metadata"]["screenshot_path"] = str(path)
                
            elif action.type == ActionType.ASSERT_TEXT:
                await self._assert_text(action.selector, action.text, action.timeout)
                result["metadata"]["text"] = action.text
                
            elif action.type == ActionType.ASSERT_ELEMENT:
                await self._assert_element(action.selector, action.timeout)
                result["metadata"]["selector"] = action.selector
                
            elif action.type == ActionType.EXTRACT:
                extracted = await self._extract_text(action.selector, action.timeout)
                result["metadata"]["extracted_text"] = extracted
                
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
        result["duration_ms"] = (time.time() - start_time) * 1000
        
        return result
    
    async def _navigate(self, url: str):
        """Navigate to URL and wait for load."""
        await self.page.goto(url, wait_until="domcontentloaded")
        
    async def _click(self, selector: str, timeout: int):
        """Click element with deterministic waiting."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        await element.click()
        # Wait for potential navigation or state changes
        await self.page.wait_for_load_state("domcontentloaded")
        
    async def _type(self, selector: str, value: str, timeout: int):
        """Type into element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        await element.fill(value)
        
    async def _select(self, selector: str, value: str, timeout: int):
        """Select option from dropdown."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        await element.select_option(value)
        
    async def _wait(self, wait_type: str, timeout: int):
        """Wait for specific condition."""
        if wait_type == "load":
            await self.page.wait_for_load_state("load", timeout=timeout)
        elif wait_type == "networkidle":
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
        else:
            # Wait for specific time
            await asyncio.sleep(int(wait_type) / 1000)
            
    async def _scroll(self, selector: Optional[str], timeout: int):
        """Scroll to element or position."""
        if selector:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            await element.scroll_into_view_if_needed()
        else:
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
    async def _screenshot(self, name: Optional[str] = None) -> Path:
        """Take screenshot and return path."""
        if not name:
            name = f"screenshot_{int(time.time() * 1000)}.png"
        if not name.endswith('.png'):
            name += '.png'
            
        path = self.screenshots_dir / name
        await self.page.screenshot(path=str(path), full_page=True)
        return path
    
    async def _assert_text(self, selector: str, expected_text: str, timeout: int):
        """Assert element contains expected text."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        actual_text = await element.inner_text()
        if expected_text not in actual_text:
            raise AssertionError(
                f"Expected text '{expected_text}' not found. Actual: '{actual_text}'"
            )
            
    async def _assert_element(self, selector: str, timeout: int):
        """Assert element exists."""
        await self.page.wait_for_selector(selector, timeout=timeout)
        
    async def _extract_text(self, selector: str, timeout: int) -> str:
        """Extract text from element."""
        element = await self.page.wait_for_selector(selector, timeout=timeout)
        return await element.inner_text()
    
    async def get_dom_snapshot(self) -> str:
        """Get deterministic DOM snapshot hash."""
        content = await self.page.content()
        # Remove non-deterministic elements (timestamps, IDs, etc.)
        # This is a simplified version - real implementation would need more filtering
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get_network_events(self) -> List[Dict[str, Any]]:
        """Get captured network events."""
        # This is a placeholder - real implementation would capture events
        return []
