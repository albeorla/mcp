"""
Pytest configuration file for Aerith Admin MCP server tests.
This file contains shared fixtures and configuration for all tests.
"""
import os
import sys
import pytest
import logging

# Register custom markers
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "browser: marks tests that require browser automation (deselect with '-m \"not browser\"')")

# Configure logging for tests
@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("MCP_DEBUG") == "true" else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(stream=sys.stderr)
        ]
    )
    
    # Suppress excessive logging during tests
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    logger = logging.getLogger("aerith-test")
    logger.info("Test logging configured")

# Add the project root to sys.path if needed
@pytest.fixture(scope="session", autouse=True)
def add_mcp_to_path():
    """Ensure MCP module is in the Python path."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Also add the mcp directory itself
    mcp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if mcp_dir not in sys.path:
        sys.path.insert(0, mcp_dir)

# Mock dependencies for browser automation
@pytest.fixture
def mock_browser_context():
    """Mock browser context for testing browser automation."""
    class MockBrowserContext:
        def __init__(self, headless=True):
            self.headless = headless
            
        def navigate(self, url):
            return {"success": True, "url": url}
            
        def click(self, selector):
            return {"success": True, "selector": selector}
            
        def type(self, selector, text):
            return {"success": True, "selector": selector, "text": text}
            
        def get_content(self):
            return "<html><body>Mock content</body></html>"
    
    return MockBrowserContext

# Create a mock Agent for browser automation
@pytest.fixture
def mock_browser_agent(mock_browser_context):
    """Mock Agent for testing browser automation."""
    class MockAgent:
        def __init__(self, context, initial_goal):
            self.context = context
            self.goal = initial_goal
            
        def run(self):
            return {
                "success": True,
                "goal": self.goal,
                "result": "Mock result for browser automation"
            }
    
    return MockAgent 