"""Script storage for saving and loading test scripts."""

import json
import yaml
from pathlib import Path
from typing import List, Optional
from ..models.test_script import TestScript


class ScriptStorage:
    """
    Manages storage and retrieval of test scripts.
    
    Supports multiple formats:
    - JSON (default)
    - YAML
    - Custom DSL (future)
    """
    
    def __init__(self, storage_dir: str = "./test_scripts"):
        """
        Initialize script storage.
        
        Args:
            storage_dir: Directory for storing test scripts
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, script: TestScript, format: str = "json") -> Path:
        """
        Save a test script to storage.
        
        Args:
            script: The test script to save
            format: Storage format ('json' or 'yaml')
            
        Returns:
            Path to saved script file
        """
        # Sanitize filename
        safe_name = "".join(c for c in script.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        if format == "json":
            filename = f"{safe_name}.json"
            filepath = self.storage_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(script.model_dump(), f, indent=2, default=str)
                
        elif format == "yaml":
            filename = f"{safe_name}.yaml"
            filepath = self.storage_dir / filename
            
            with open(filepath, 'w') as f:
                yaml.dump(script.model_dump(), f, default_flow_style=False, sort_keys=False)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return filepath
    
    def load(self, name: str, format: str = "json") -> TestScript:
        """
        Load a test script from storage.
        
        Args:
            name: Script name or filename
            format: Storage format ('json' or 'yaml')
            
        Returns:
            The loaded TestScript
        """
        # Try to find the file
        if format == "json":
            filepath = self.storage_dir / f"{name}.json"
            if not filepath.exists():
                filepath = self.storage_dir / name
        elif format == "yaml":
            filepath = self.storage_dir / f"{name}.yaml"
            if not filepath.exists():
                filepath = self.storage_dir / name
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if not filepath.exists():
            raise FileNotFoundError(f"Script not found: {name}")
        
        with open(filepath, 'r') as f:
            if format == "json":
                data = json.load(f)
            elif format == "yaml":
                data = yaml.safe_load(f)
        
        return TestScript(**data)
    
    def list_scripts(self) -> List[str]:
        """
        List all available test scripts.
        
        Returns:
            List of script names
        """
        scripts = []
        
        for filepath in self.storage_dir.glob("*.json"):
            scripts.append(filepath.stem)
        
        for filepath in self.storage_dir.glob("*.yaml"):
            if filepath.stem not in scripts:  # Avoid duplicates
                scripts.append(filepath.stem)
        
        return sorted(scripts)
    
    def delete(self, name: str) -> bool:
        """
        Delete a test script.
        
        Args:
            name: Script name
            
        Returns:
            True if deleted, False if not found
        """
        deleted = False
        
        for ext in ['.json', '.yaml']:
            filepath = self.storage_dir / f"{name}{ext}"
            if filepath.exists():
                filepath.unlink()
                deleted = True
        
        return deleted
    
    def exists(self, name: str) -> bool:
        """
        Check if a script exists.
        
        Args:
            name: Script name
            
        Returns:
            True if script exists
        """
        return (
            (self.storage_dir / f"{name}.json").exists() or
            (self.storage_dir / f"{name}.yaml").exists()
        )
