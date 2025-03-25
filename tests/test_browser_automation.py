#!/usr/bin/env python3
"""
Tests for browser automation functionality in the MCP server.
"""
import os
import sys
import pytest
from unittest import mock

# Import the test fixture
from conftest import add_mcp_to_path, mock_browser_context, mock_browser_agent

# Import the functions we need for testing
from server import run_browser_agent


class TestBrowserAutomation:
    """Test class for browser automation functionality."""
    
    def test_run_browser_agent_with_mocks(self, tmpdir, mock_browser_context, mock_browser_agent):
        """Test running a browser agent with mocked browser context and agent."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Create mock modules and classes
        mock_browser_use = mock.MagicMock()
        mock_browser_use.BrowserContext = mock.MagicMock(return_value=mock_browser_context())
        mock_browser_use.Agent = mock.MagicMock(return_value=mock_browser_agent(mock_browser_context(), "Test goal"))
        
        # Mock the browser-use library import
        with mock.patch.dict('sys.modules', {'browser_use': mock_browser_use}):
            # Call the run_browser_agent function
            result = run_browser_agent("Search for something online")
            
            # Verify the response
            assert result["success"] is True
            assert "result" in result
            assert "message" in result
            assert "Search for something online" in result["message"]
    
    def test_run_browser_agent_error_handling(self, tmpdir):
        """Test error handling in the run_browser_agent function."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Create a mock that raises an ImportError
        with mock.patch.dict('sys.modules', {'browser_use': None}):
            # This should handle the ImportError gracefully
            result = run_browser_agent("Search for something online")
            
            # Verify the error response
            assert result["success"] is False
            assert "error" in result
            assert "browser-use library not installed" in result["error"]
    
    def test_run_browser_agent_execution_error(self, tmpdir, mock_browser_context):
        """Test handling of runtime errors in the browser agent."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Create a mock Agent that raises an exception when run
        class ErrorAgent:
            def __init__(self, context, initial_goal):
                self.context = context
                self.goal = initial_goal
            
            def run(self):
                raise RuntimeError("Test error in browser automation")
        
        # Create mock modules with our error agent
        mock_browser_use = mock.MagicMock()
        mock_browser_use.BrowserContext = mock.MagicMock(return_value=mock_browser_context())
        mock_browser_use.Agent = mock.MagicMock(return_value=ErrorAgent(mock_browser_context(), "Test goal"))
        
        # Mock the browser-use library import
        with mock.patch.dict('sys.modules', {'browser_use': mock_browser_use}):
            # Call the run_browser_agent function
            result = run_browser_agent("Search for something online")
            
            # Verify the error response
            assert result["success"] is False
            assert "error" in result
            assert "Test error in browser automation" in result["error"]


@pytest.mark.browser
class TestActualBrowserAutomation:
    """Test class for actual browser automation.
    
    These tests are marked with 'browser' to allow skipping them
    when browser automation libraries are not installed.
    Skip with pytest -m "not browser" to avoid running these tests.
    """
    
    def test_actual_browser_agent(self, tmpdir):
        """Test running a real browser agent if the library is installed."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Try to import the browser-use library
        try:
            import browser_use
            # If we get here, the library is installed
            
            # Call the run_browser_agent function with a simple goal
            result = run_browser_agent("Navigate to example.com and get the title")
            
            # Verify the response - we only check if it ran without errors
            # since the actual result depends on browser environment
            assert result["success"] is True
            assert "result" in result
            
        except ImportError:
            # Skip the test if browser-use is not installed
            pytest.skip("browser-use library not installed")
    
    def test_multi_step_browser_task(self, tmpdir):
        """Test a more complex browser task with multiple steps."""
        # Set up test environment
        os.chdir(tmpdir)
        
        # Try to import the browser-use library
        try:
            import browser_use
            # If we get here, the library is installed
            
            # Call the run_browser_agent function with a complex goal
            result = run_browser_agent(
                "Go to example.com, then find a link, click it, and return the new page title"
            )
            
            # Verify the response - we only check if it ran without errors
            assert result["success"] is True
            assert "result" in result
            
        except ImportError:
            # Skip the test if browser-use is not installed
            pytest.skip("browser-use library not installed") 