"""Knowledge base for storing learned information."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class KnowledgeBase:
    """
    Central knowledge base for the testing tool.
    
    Stores:
    - Element mappings (source components -> selectors)
    - Successful interaction patterns
    - Application structure (routes, components, APIs)
    - Test execution history
    """
    
    def __init__(self, base_path: str = "./knowledge_base"):
        """
        Initialize the knowledge base.
        
        Args:
            base_path: Base directory for knowledge storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.element_mappings: Dict[str, Dict[str, Any]] = {}
        self.routes: List[str] = []
        self.components: Dict[str, Any] = {}
        self.api_endpoints: List[str] = []
        
        self._load()
    
    def add_element_mapping(
        self,
        component_name: str,
        selector: str,
        selector_type: str = "css",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a mapping from source component to DOM selector.
        
        Args:
            component_name: Name of the source component
            selector: DOM selector
            selector_type: Type of selector (css, xpath, testid)
            metadata: Additional metadata
        """
        if component_name not in self.element_mappings:
            self.element_mappings[component_name] = {
                "selectors": [],
                "selector_type": selector_type,
                "metadata": metadata or {}
            }
        
        if selector not in [s["value"] for s in self.element_mappings[component_name]["selectors"]]:
            self.element_mappings[component_name]["selectors"].append({
                "value": selector,
                "type": selector_type
            })
        
        self._save()
    
    def get_selector(self, component_name: str) -> Optional[str]:
        """
        Get the best selector for a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Selector string or None
        """
        mapping = self.element_mappings.get(component_name)
        if mapping and mapping["selectors"]:
            # Return the first (most stable) selector
            return mapping["selectors"][0]["value"]
        return None
    
    def add_route(self, route: str):
        """
        Add an application route.
        
        Args:
            route: Route path
        """
        if route not in self.routes:
            self.routes.append(route)
            self._save()
    
    def add_component(self, name: str, component_info: Dict[str, Any]):
        """
        Add component information.
        
        Args:
            name: Component name
            component_info: Component details
        """
        self.components[name] = component_info
        self._save()
    
    def add_api_endpoint(self, endpoint: str):
        """
        Add an API endpoint.
        
        Args:
            endpoint: API endpoint URL or path
        """
        if endpoint not in self.api_endpoints:
            self.api_endpoints.append(endpoint)
            self._save()
    
    def get_all_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Get all element mappings."""
        return self.element_mappings
    
    def get_all_routes(self) -> List[str]:
        """Get all known routes."""
        return self.routes
    
    def get_all_components(self) -> Dict[str, Any]:
        """Get all component information."""
        return self.components
    
    def get_all_endpoints(self) -> List[str]:
        """Get all API endpoints."""
        return self.api_endpoints
    
    def _load(self):
        """Load knowledge base from disk."""
        kb_file = self.base_path / "knowledge_base.json"
        
        if kb_file.exists():
            with open(kb_file, 'r') as f:
                data = json.load(f)
                self.element_mappings = data.get("element_mappings", {})
                self.routes = data.get("routes", [])
                self.components = data.get("components", {})
                self.api_endpoints = data.get("api_endpoints", [])
    
    def _save(self):
        """Save knowledge base to disk."""
        kb_file = self.base_path / "knowledge_base.json"
        
        data = {
            "element_mappings": self.element_mappings,
            "routes": self.routes,
            "components": self.components,
            "api_endpoints": self.api_endpoints
        }
        
        with open(kb_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_catalog(self) -> Dict[str, Any]:
        """
        Export a complete test case catalog.
        
        Returns:
            Dictionary with all knowledge base information
        """
        return {
            "element_mappings": self.element_mappings,
            "routes": self.routes,
            "components": self.components,
            "api_endpoints": self.api_endpoints,
            "stats": {
                "total_mappings": len(self.element_mappings),
                "total_routes": len(self.routes),
                "total_components": len(self.components),
                "total_endpoints": len(self.api_endpoints)
            }
        }
