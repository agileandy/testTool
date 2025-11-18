"""Pattern learner for identifying common workflows."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
from ..models.test_script import TestScript
from ..models.action import Action


class PatternLearner:
    """
    Learns from repeated interactions to identify common patterns.
    
    Capabilities:
    - Identify frequently used action sequences
    - Detect common workflows
    - Build reusable test components
    - Improve selector stability
    """
    
    def __init__(self, knowledge_base_path: str = "./knowledge_base"):
        """
        Initialize the pattern learner.
        
        Args:
            knowledge_base_path: Path to knowledge base storage
        """
        self.kb_path = Path(knowledge_base_path)
        self.kb_path.mkdir(parents=True, exist_ok=True)
        
        self.patterns: Dict[str, Any] = defaultdict(lambda: {"count": 0, "examples": []})
        self.workflows: List[Dict[str, Any]] = []
        self.selector_mappings: Dict[str, List[str]] = defaultdict(list)
        
        self._load_knowledge()
    
    def observe_script(self, script: TestScript):
        """
        Observe a test script and learn from it.
        
        Args:
            script: The test script to learn from
        """
        # Extract action sequences
        action_sequence = [step.action.type for step in script.steps]
        sequence_key = " -> ".join(action_sequence)
        
        self.patterns[sequence_key]["count"] += 1
        self.patterns[sequence_key]["examples"].append(script.name)
        
        # Learn selector patterns
        for step in script.steps:
            if step.action.selector:
                action_type = step.action.type
                selector = step.action.selector
                
                key = f"{action_type}:{step.description}"
                if selector not in self.selector_mappings[key]:
                    self.selector_mappings[key].append(selector)
        
        # Identify workflows (sequences of 3+ actions)
        if len(script.steps) >= 3:
            workflow = {
                "name": script.name,
                "description": script.description,
                "steps": [
                    {
                        "type": step.action.type,
                        "description": step.description
                    }
                    for step in script.steps
                ]
            }
            self.workflows.append(workflow)
        
        self._save_knowledge()
    
    def get_common_patterns(self, min_count: int = 2) -> List[Dict[str, Any]]:
        """
        Get commonly observed patterns.
        
        Args:
            min_count: Minimum occurrence count
            
        Returns:
            List of common patterns with their details
        """
        common = []
        for pattern, data in self.patterns.items():
            if data["count"] >= min_count:
                common.append({
                    "pattern": pattern,
                    "count": data["count"],
                    "examples": data["examples"][:5]  # Limit examples
                })
        
        return sorted(common, key=lambda x: x["count"], reverse=True)
    
    def suggest_selector(self, action_type: str, description: str) -> Optional[str]:
        """
        Suggest a selector based on learned patterns.
        
        Args:
            action_type: Type of action
            description: Step description
            
        Returns:
            Suggested selector or None
        """
        key = f"{action_type}:{description}"
        selectors = self.selector_mappings.get(key, [])
        
        if selectors:
            # Return most common selector (first one for now)
            return selectors[0]
        
        return None
    
    def find_similar_workflows(self, description: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find workflows similar to the given description.
        
        Args:
            description: Workflow description
            limit: Maximum number of results
            
        Returns:
            List of similar workflows
        """
        # Simple keyword matching for now
        keywords = set(description.lower().split())
        
        scored_workflows = []
        for workflow in self.workflows:
            workflow_text = f"{workflow['name']} {workflow['description']}".lower()
            workflow_keywords = set(workflow_text.split())
            
            # Calculate similarity (Jaccard index)
            intersection = keywords & workflow_keywords
            union = keywords | workflow_keywords
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > 0.1:  # Threshold
                    scored_workflows.append((similarity, workflow))
        
        # Sort by similarity and return top results
        scored_workflows.sort(reverse=True, key=lambda x: x[0])
        return [w for _, w in scored_workflows[:limit]]
    
    def auto_generate_test(self, description: str) -> Optional[TestScript]:
        """
        Auto-generate a test script based on learned patterns.
        
        Args:
            description: Test description
            
        Returns:
            Generated TestScript or None
        """
        similar = self.find_similar_workflows(description, limit=1)
        
        if similar:
            workflow = similar[0]
            # Create a new script based on the workflow
            # This is a simplified version
            return TestScript(
                name=f"auto_{description[:30]}",
                description=description,
                mode="smart",
                steps=[],  # Would need to reconstruct steps from workflow
                metadata={"auto_generated": True, "based_on": workflow["name"]}
            )
        
        return None
    
    def _load_knowledge(self):
        """Load knowledge base from disk."""
        patterns_file = self.kb_path / "patterns.json"
        workflows_file = self.kb_path / "workflows.json"
        selectors_file = self.kb_path / "selectors.json"
        
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                self.patterns = defaultdict(lambda: {"count": 0, "examples": []}, json.load(f))
        
        if workflows_file.exists():
            with open(workflows_file, 'r') as f:
                self.workflows = json.load(f)
        
        if selectors_file.exists():
            with open(selectors_file, 'r') as f:
                self.selector_mappings = defaultdict(list, json.load(f))
    
    def _save_knowledge(self):
        """Save knowledge base to disk."""
        with open(self.kb_path / "patterns.json", 'w') as f:
            json.dump(dict(self.patterns), f, indent=2)
        
        with open(self.kb_path / "workflows.json", 'w') as f:
            json.dump(self.workflows, f, indent=2)
        
        with open(self.kb_path / "selectors.json", 'w') as f:
            json.dump(dict(self.selector_mappings), f, indent=2)
