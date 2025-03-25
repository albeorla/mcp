#!/usr/bin/env python3
"""Script to check the Python environment and installed packages."""
import sys
import os
import importlib.util

def check_module(module_name):
    """Check if a module is available and print its location."""
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        if spec.origin:
            return f"✅ {module_name}: Found at {spec.origin}"
        else:
            return f"✅ {module_name}: Found (namespace package)"
    else:
        return f"❌ {module_name}: Not found"

if __name__ == "__main__":
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Check key modules
    modules = ["pytest", "coverage", "pytest_cov", "mcp", "server"]
    for module in modules:
        print(check_module(module))
    
    # List installed packages
    try:
        import pkg_resources
        print("\nInstalled packages:")
        for package in pkg_resources.working_set:
            print(f"  {package.project_name}=={package.version}")
    except ImportError:
        print("\nCouldn't import pkg_resources to list installed packages") 