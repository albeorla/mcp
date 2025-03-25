#!/usr/bin/env python3
"""
Test script for the tree_directory command in the MCP server.
This script directly calls the tree_directory function to verify it works.
"""
import os
import sys
import json

# Add parent directory to path to import server.py
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

# Import the tree_directory function from server.py
try:
    from server import tree_directory
    print("Successfully imported tree_directory function")
except Exception as e:
    print(f"Error importing tree_directory: {e}")
    sys.exit(1)

def test_tree(directory="", max_depth=3, show_files=True, show_hidden=False, pattern=None, 
              exclude_common=True, custom_excludes=None):
    """Test the tree_directory function with various parameters"""
    print(f"\n--- Testing tree_directory({directory}, {max_depth}, {show_files}, {show_hidden}, {pattern}, {exclude_common}, {custom_excludes}) ---")
    try:
        result = tree_directory(
            directory_path=directory, 
            max_depth=max_depth, 
            show_files=show_files, 
            show_hidden=show_hidden, 
            pattern=pattern,
            exclude_common=exclude_common,
            custom_excludes=custom_excludes
        )
        if result["success"]:
            print(f"Success! {result['message']}")
            print("\nTree Output:")
            print(result["tree"])
            print("\nStats:")
            print(f"- Directories: {result['stats']['directories']}")
            print(f"- Files: {result['stats']['files']}")
            print(f"- Total size: {result['stats']['total_size']} bytes")
            print(f"- Excluded items: {result['stats']['excluded_items']}")
        else:
            print(f"Error: {result['message']}")
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Test the tree_directory command")
    parser.add_argument("--dir", default="", help="Directory path to display")
    parser.add_argument("--depth", type=int, default=3, help="Maximum depth to display")
    parser.add_argument("--no-files", action="store_true", help="Don't show files")
    parser.add_argument("--hidden", action="store_true", help="Show hidden files/directories")
    parser.add_argument("--pattern", help="Glob pattern to filter files/directories")
    parser.add_argument("--include-all", action="store_true", help="Include commonly excluded directories like __pycache__, .git, etc.")
    parser.add_argument("--exclude", action="append", help="Additional patterns to exclude (can be used multiple times)")
    
    args = parser.parse_args()
    
    # Run the test
    test_tree(
        directory=args.dir,
        max_depth=args.depth,
        show_files=not args.no_files,
        show_hidden=args.hidden,
        pattern=args.pattern,
        exclude_common=not args.include_all,
        custom_excludes=args.exclude
    ) 