"""Tests for knowledge base."""

import pytest
import tempfile
from testTool.learning_layer import KnowledgeBase


@pytest.fixture
def temp_kb():
    """Create a knowledge base with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield KnowledgeBase(base_path=tmpdir)


def test_kb_creation(temp_kb):
    """Test creating a knowledge base."""
    assert temp_kb is not None


def test_add_element_mapping(temp_kb):
    """Test adding element mappings."""
    temp_kb.add_element_mapping(
        "LoginButton",
        "button#login",
        selector_type="css"
    )
    
    selector = temp_kb.get_selector("LoginButton")
    assert selector == "button#login"


def test_add_route(temp_kb):
    """Test adding routes."""
    temp_kb.add_route("/login")
    temp_kb.add_route("/dashboard")
    
    routes = temp_kb.get_all_routes()
    assert "/login" in routes
    assert "/dashboard" in routes


def test_add_component(temp_kb):
    """Test adding components."""
    temp_kb.add_component("Header", {
        "file": "components/Header.jsx",
        "props": ["title", "user"]
    })
    
    components = temp_kb.get_all_components()
    assert "Header" in components
    assert components["Header"]["file"] == "components/Header.jsx"


def test_add_api_endpoint(temp_kb):
    """Test adding API endpoints."""
    temp_kb.add_api_endpoint("/api/users")
    temp_kb.add_api_endpoint("/api/auth")
    
    endpoints = temp_kb.get_all_endpoints()
    assert "/api/users" in endpoints
    assert "/api/auth" in endpoints


def test_export_catalog(temp_kb):
    """Test exporting catalog."""
    temp_kb.add_element_mapping("Button", "button")
    temp_kb.add_route("/home")
    temp_kb.add_api_endpoint("/api/data")
    
    catalog = temp_kb.export_catalog()
    
    assert catalog["stats"]["total_mappings"] >= 1
    assert catalog["stats"]["total_routes"] >= 1
    assert catalog["stats"]["total_endpoints"] >= 1


def test_persistence(temp_kb):
    """Test that knowledge base persists."""
    # Add data
    temp_kb.add_element_mapping("TestElement", "div#test")
    
    # Create new KB with same path
    base_path = temp_kb.base_path
    new_kb = KnowledgeBase(base_path=str(base_path))
    
    # Should have the same data
    selector = new_kb.get_selector("TestElement")
    assert selector == "div#test"
