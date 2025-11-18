"""Natural language interpreter for converting human instructions to actions."""

import json
import os
from typing import List, Optional, Dict, Any
from ..models.action import Action, ActionType


class NLInterpreter:
    """
    Interprets natural language instructions and converts them to structured actions.
    
    Supports both LLM-based and rule-based interpretation.
    """
    
    def __init__(self, use_llm: bool = False, llm_provider: str = "openai"):
        """
        Initialize the NL interpreter.
        
        Args:
            use_llm: Whether to use LLM for interpretation
            llm_provider: LLM provider ('openai' or 'anthropic')
        """
        self.use_llm = use_llm
        self.llm_provider = llm_provider
        self._client = None
        
        if use_llm:
            self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client if API keys are available."""
        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    from openai import OpenAI
                    self._client = OpenAI(api_key=api_key)
                except ImportError:
                    print("Warning: openai package not installed")
        elif self.llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                try:
                    from anthropic import Anthropic
                    self._client = Anthropic(api_key=api_key)
                except ImportError:
                    print("Warning: anthropic package not installed")
    
    def interpret(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> List[Action]:
        """
        Interpret a natural language instruction into structured actions.
        
        Args:
            instruction: Natural language instruction
            context: Optional context (DOM state, previous actions, etc.)
            
        Returns:
            List of Action objects
        """
        if self.use_llm and self._client:
            return self._interpret_with_llm(instruction, context)
        else:
            return self._interpret_with_rules(instruction, context)
    
    def _interpret_with_llm(self, instruction: str, context: Optional[Dict[str, Any]]) -> List[Action]:
        """Use LLM to interpret instruction."""
        system_prompt = """You are a browser automation expert. Convert natural language instructions 
        into structured browser actions. Return a JSON array of actions with this schema:
        {
            "type": "navigate|click|type|select|wait|scroll|screenshot|assert_text|assert_element|extract",
            "selector": "CSS selector or XPath (if applicable)",
            "value": "value for navigation URL, typing, or selecting",
            "text": "expected text for assertions",
            "timeout": 30000
        }
        
        Examples:
        - "go to https://example.com" -> [{"type": "navigate", "value": "https://example.com"}]
        - "click the login button" -> [{"type": "click", "selector": "button[data-testid='login']"}]
        - "type 'admin' in username field" -> [{"type": "type", "selector": "input[name='username']", "value": "admin"}]
        
        Be deterministic and prefer data-testid selectors when possible.
        """
        
        user_prompt = f"Instruction: {instruction}"
        if context:
            user_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
        
        try:
            if self.llm_provider == "openai":
                response = self._client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,  # Low temperature for determinism
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                actions_data = result.get("actions", [])
                
            elif self.llm_provider == "anthropic":
                response = self._client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                )
                result = json.loads(response.content[0].text)
                actions_data = result.get("actions", [])
            
            return [Action(**action_data) for action_data in actions_data]
            
        except Exception as e:
            print(f"LLM interpretation failed: {e}. Falling back to rule-based.")
            return self._interpret_with_rules(instruction, context)
    
    def _interpret_with_rules(self, instruction: str, context: Optional[Dict[str, Any]]) -> List[Action]:
        """Use rule-based interpretation as fallback."""
        instruction_lower = instruction.lower().strip()
        actions = []
        
        # Navigation patterns
        if any(keyword in instruction_lower for keyword in ["go to", "navigate to", "open", "visit"]):
            url = self._extract_url(instruction)
            if url:
                actions.append(Action(type=ActionType.NAVIGATE, value=url))
        
        # Click patterns
        elif any(keyword in instruction_lower for keyword in ["click", "press", "tap"]):
            selector = self._extract_selector(instruction, "button")
            actions.append(Action(type=ActionType.CLICK, selector=selector))
        
        # Type/input patterns
        elif any(keyword in instruction_lower for keyword in ["type", "enter", "input", "fill"]):
            value = self._extract_value(instruction)
            selector = self._extract_selector(instruction, "input")
            actions.append(Action(type=ActionType.TYPE, selector=selector, value=value))
        
        # Select patterns
        elif "select" in instruction_lower:
            value = self._extract_value(instruction)
            selector = self._extract_selector(instruction, "select")
            actions.append(Action(type=ActionType.SELECT, selector=selector, value=value))
        
        # Wait patterns
        elif "wait" in instruction_lower:
            wait_type = "load"
            if "network" in instruction_lower:
                wait_type = "networkidle"
            actions.append(Action(type=ActionType.WAIT, value=wait_type))
        
        # Screenshot patterns
        elif "screenshot" in instruction_lower or "capture" in instruction_lower:
            actions.append(Action(type=ActionType.SCREENSHOT))
        
        # Assertion patterns
        elif any(keyword in instruction_lower for keyword in ["verify", "assert", "check"]):
            text = self._extract_value(instruction)
            selector = self._extract_selector(instruction, "*")
            if "text" in instruction_lower:
                actions.append(Action(type=ActionType.ASSERT_TEXT, selector=selector, text=text))
            else:
                actions.append(Action(type=ActionType.ASSERT_ELEMENT, selector=selector))
        
        # Default: try to extract as click action
        if not actions:
            actions.append(Action(
                type=ActionType.CLICK,
                selector="*",
                metadata={"raw_instruction": instruction}
            ))
        
        return actions
    
    def _extract_url(self, instruction: str) -> Optional[str]:
        """Extract URL from instruction."""
        import re
        url_pattern = r'https?://[^\s\'"]+(?=[\'"\s]|$)'
        match = re.search(url_pattern, instruction)
        if match:
            return match.group(0)
        
        # Try to extract from quotes
        quote_pattern = r'["\']([^"\']+)["\']'
        match = re.search(quote_pattern, instruction)
        if match:
            potential_url = match.group(1)
            if potential_url.startswith('http'):
                return potential_url
        
        return None
    
    def _extract_value(self, instruction: str) -> str:
        """Extract value from instruction (text in quotes)."""
        import re
        quote_pattern = r'["\']([^"\']+)["\']'
        match = re.search(quote_pattern, instruction)
        if match:
            return match.group(1)
        return ""
    
    def _extract_selector(self, instruction: str, default_element: str) -> str:
        """Extract or generate selector from instruction."""
        instruction_lower = instruction.lower()
        
        # Common element identifiers
        element_map = {
            "login": "button[data-testid='login'], #login, .login-btn",
            "submit": "button[type='submit'], input[type='submit']",
            "username": "input[name='username'], #username",
            "password": "input[name='password'], #password",
            "email": "input[type='email'], input[name='email']",
        }
        
        for keyword, selector in element_map.items():
            if keyword in instruction_lower:
                return selector.split(',')[0].strip()
        
        # Try to extract from quotes
        import re
        quote_pattern = r'["\']([^"\']+)["\']'
        match = re.search(quote_pattern, instruction)
        if match:
            text = match.group(1)
            return f"{default_element}:has-text('{text}')"
        
        return default_element
    
    def validate_actions(self, actions: List[Action]) -> List[str]:
        """
        Validate actions before execution.
        
        Returns:
            List of validation warnings/errors
        """
        issues = []
        
        for i, action in enumerate(actions):
            if action.type in [ActionType.CLICK, ActionType.TYPE, ActionType.SELECT, ActionType.SCROLL]:
                if not action.selector:
                    issues.append(f"Action {i}: {action.type} requires a selector")
            
            if action.type == ActionType.NAVIGATE:
                if not action.value:
                    issues.append(f"Action {i}: NAVIGATE requires a URL value")
            
            if action.type == ActionType.TYPE:
                if not action.value:
                    issues.append(f"Action {i}: TYPE requires a value")
            
            if action.type == ActionType.ASSERT_TEXT:
                if not action.text:
                    issues.append(f"Action {i}: ASSERT_TEXT requires expected text")
        
        return issues
