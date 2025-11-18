"""Tests for source analyzer."""

import pytest
import tempfile
from pathlib import Path
from testTool.utils import SourceAnalyzer


@pytest.fixture
def temp_source_dir():
    """Create a temporary source directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir)
        
        # Create sample HTML file
        html_file = source_dir / "index.html"
        html_file.write_text('''
            <html>
                <button data-testid="login-btn">Login</button>
                <input data-testid="username" />
            </html>
        ''')
        
        # Create sample JSX file
        jsx_file = source_dir / "App.jsx"
        jsx_file.write_text('''
            function App() {
                return (
                    <div data-testid="app-container">
                        <button data-testid="submit-btn">Submit</button>
                    </div>
                );
            }
        ''')
        
        # Create sample Python file with routes
        py_file = source_dir / "routes.py"
        py_file.write_text('''
            from flask import Flask
            app = Flask(__name__)
            
            @app.route('/login')
            def login():
                pass
            
            @app.route('/dashboard')
            def dashboard():
                pass
        ''')
        
        # Create sample JS file with API calls
        js_file = source_dir / "api.js"
        js_file.write_text('''
            const fetchUsers = () => {
                return fetch('/api/users');
            };
            
            const fetchData = () => {
                return fetch('/api/data');
            };
        ''')
        
        yield source_dir


def test_analyzer_creation(temp_source_dir):
    """Test creating a source analyzer."""
    analyzer = SourceAnalyzer(str(temp_source_dir))
    assert analyzer is not None


def test_find_test_ids(temp_source_dir):
    """Test finding data-testid attributes."""
    analyzer = SourceAnalyzer(str(temp_source_dir))
    test_ids = analyzer.find_test_ids()
    
    assert len(test_ids) > 0
    
    # Check that we found the test IDs
    ids = [item['id'] for item in test_ids]
    assert 'login-btn' in ids
    assert 'username' in ids
    assert 'submit-btn' in ids


def test_find_routes(temp_source_dir):
    """Test finding application routes."""
    analyzer = SourceAnalyzer(str(temp_source_dir))
    routes = analyzer.find_routes()
    
    assert len(routes) > 0
    assert '/login' in routes
    assert '/dashboard' in routes


def test_find_api_endpoints(temp_source_dir):
    """Test finding API endpoints."""
    analyzer = SourceAnalyzer(str(temp_source_dir))
    endpoints = analyzer.find_api_endpoints()
    
    assert len(endpoints) > 0
    assert '/api/users' in endpoints
    assert '/api/data' in endpoints


def test_analyze_comprehensive(temp_source_dir):
    """Test comprehensive analysis."""
    analyzer = SourceAnalyzer(str(temp_source_dir))
    results = analyzer.analyze()
    
    assert 'test_ids' in results
    assert 'routes' in results
    assert 'components' in results
    assert 'api_endpoints' in results
    
    assert len(results['test_ids']) > 0
    assert len(results['routes']) > 0
    assert len(results['api_endpoints']) > 0


def test_invalid_source_dir():
    """Test error with invalid source directory."""
    with pytest.raises(ValueError):
        SourceAnalyzer("/nonexistent/path")
