"""Source code analyzer for Smart Mode."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


class SourceAnalyzer:
    """
    Analyzes application source code to extract useful testing information.
    
    In Smart Mode, this helps:
    - Find data-testid attributes
    - Extract routes and navigation structure
    - Identify components and their selectors
    - Discover API endpoints
    """
    
    def __init__(self, source_dir: str):
        """
        Initialize the source analyzer.
        
        Args:
            source_dir: Root directory of the application source
        """
        self.source_dir = Path(source_dir)
        
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive source analysis.
        
        Returns:
            Dictionary with analysis results
        """
        return {
            "test_ids": self.find_test_ids(),
            "routes": self.find_routes(),
            "components": self.find_components(),
            "api_endpoints": self.find_api_endpoints(),
        }
    
    def find_test_ids(self) -> List[Dict[str, str]]:
        """
        Find all data-testid attributes in source files.
        
        Returns:
            List of test IDs with their locations
        """
        test_ids = []
        
        # Search in common file types
        patterns = [
            '**/*.html',
            '**/*.jsx',
            '**/*.tsx',
            '**/*.vue',
            '**/*.svelte'
        ]
        
        for pattern in patterns:
            for filepath in self.source_dir.glob(pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Find data-testid attributes
                        matches = re.finditer(r'data-testid=["\']([^"\']+)["\']', content)
                        for match in matches:
                            test_ids.append({
                                "id": match.group(1),
                                "file": str(filepath.relative_to(self.source_dir)),
                                "selector": f'[data-testid="{match.group(1)}"]'
                            })
                except Exception:
                    continue
        
        return test_ids
    
    def find_routes(self) -> List[str]:
        """
        Find application routes.
        
        Returns:
            List of route paths
        """
        routes = []
        
        # Common routing patterns
        route_patterns = [
            r'path:\s*["\']([^"\']+)["\']',  # Vue, Angular
            r'<Route\s+path=["\']([^"\']+)["\']',  # React Router
            r'@app\.route\(["\']([^"\']+)["\']',  # Flask
            r'@route\(["\']([^"\']+)["\']',  # FastAPI
        ]
        
        for filepath in self.source_dir.rglob('*.py'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in route_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            route = match.group(1)
                            if route not in routes:
                                routes.append(route)
            except Exception:
                continue
        
        for filepath in self.source_dir.rglob('*.js'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in route_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            route = match.group(1)
                            if route not in routes:
                                routes.append(route)
            except Exception:
                continue
        
        return sorted(routes)
    
    def find_components(self) -> Dict[str, Any]:
        """
        Find UI components and their information.
        
        Returns:
            Dictionary of components
        """
        components = {}
        
        # Search for component files
        component_patterns = [
            '**/*Component.jsx',
            '**/*Component.tsx',
            '**/components/**/*.jsx',
            '**/components/**/*.tsx',
            '**/components/**/*.vue'
        ]
        
        for pattern in component_patterns:
            for filepath in self.source_dir.glob(pattern):
                component_name = filepath.stem
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extract component info
                        components[component_name] = {
                            "file": str(filepath.relative_to(self.source_dir)),
                            "test_ids": self._extract_test_ids_from_content(content),
                            "props": self._extract_props(content)
                        }
                except Exception:
                    continue
        
        return components
    
    def find_api_endpoints(self) -> List[str]:
        """
        Find API endpoints in the source.
        
        Returns:
            List of API endpoint paths
        """
        endpoints = []
        
        # API endpoint patterns
        api_patterns = [
            r'["\']\/api\/([^"\']+)["\']',
            r'fetch\(["\']([^"\']+)["\']',
            r'axios\.[a-z]+\(["\']([^"\']+)["\']',
        ]
        
        for filepath in self.source_dir.rglob('*.js'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in api_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            endpoint = match.group(1)
                            if endpoint.startswith('/') and endpoint not in endpoints:
                                endpoints.append(endpoint)
            except Exception:
                continue
        
        return sorted(endpoints)
    
    def _extract_test_ids_from_content(self, content: str) -> List[str]:
        """Extract test IDs from file content."""
        test_ids = []
        matches = re.finditer(r'data-testid=["\']([^"\']+)["\']', content)
        for match in matches:
            test_ids.append(match.group(1))
        return test_ids
    
    def _extract_props(self, content: str) -> List[str]:
        """Extract component props (simplified)."""
        props = []
        # Simple pattern for props in TypeScript/JavaScript
        matches = re.finditer(r'(\w+)\s*:\s*\w+[,;]', content)
        for match in matches:
            prop = match.group(1)
            if prop not in ['const', 'let', 'var', 'function', 'class']:
                props.append(prop)
        return props[:10]  # Limit to avoid noise
