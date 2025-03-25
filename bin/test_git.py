#!/usr/bin/env python3
"""
Test script for the Git-related tools in the MCP server.
This script directly calls the Git tool functions to verify they work.
"""
import os
import sys
import json

# Add parent directory to path to import server.py
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

# Import the git tool functions from server.py
try:
    from server import git_status, git_log, git_branch, git_diff
    print("Successfully imported Git tool functions")
except Exception as e:
    print(f"Error importing Git tool functions: {e}")
    sys.exit(1)

def print_json(data):
    """Print data in formatted JSON"""
    print(json.dumps(data, indent=2))

def test_git_status():
    """Test the git_status function"""
    print("\n--- Testing git_status() ---")
    try:
        result = git_status(detailed=True)
        if result["success"]:
            print(f"Success! Branch: {result['status']['branch']}")
            print(f"Clean working directory: {result['status']['is_clean']}")
            
            print("\nStaged changes:")
            for item in result["status"]["changes"]["staged"]:
                print(f"  {item['status']}: {item['file']}")
                
            print("\nNot staged changes:")
            for item in result["status"]["changes"]["not_staged"]:
                print(f"  {item['status']}: {item['file']}")
                
            print("\nUntracked files:")
            for item in result["status"]["changes"]["untracked"]:
                print(f"  {item['file']}")
        else:
            print(f"Error: {result['message']}")
    except Exception as e:
        print(f"Exception occurred: {e}")

def test_git_log(count=5):
    """Test the git_log function"""
    print(f"\n--- Testing git_log(count={count}) ---")
    try:
        result = git_log(count=count, show_stats=True)
        if result["success"]:
            print(f"Success! Retrieved {len(result['commits'])} commits")
            
            for commit in result['commits']:
                print(f"\nCommit: {commit['hash']}")
                print(f"Author: {commit['author_name']} <{commit['author_email']}>")
                print(f"Date: {commit['date']}")
                print(f"Message: {commit['message']}")
                if commit['stats']:
                    print("Stats:")
                    for stat in commit['stats']:
                        print(f"  {stat}")
        else:
            print(f"Error: {result['message']}")
    except Exception as e:
        print(f"Exception occurred: {e}")

def test_git_branch():
    """Test the git_branch function"""
    print("\n--- Testing git_branch() ---")
    try:
        result = git_branch(remote=True)
        if result["success"]:
            print(f"Success! Current branch: {result['current_branch']}")
            
            print("\nLocal branches:")
            for branch in result['branches']:
                if branch['type'] == 'local':
                    current = "*" if branch['is_current'] else " "
                    print(f"  {current} {branch['name']}")
                    
            print("\nRemote branches:")
            for branch in result['branches']:
                if branch['type'] == 'remote':
                    print(f"  {branch['name']}")
        else:
            print(f"Error: {result['message']}")
    except Exception as e:
        print(f"Exception occurred: {e}")

def test_git_diff(file_path=""):
    """Test the git_diff function"""
    print(f"\n--- Testing git_diff(file_path='{file_path}') ---")
    try:
        result = git_diff(file_path=file_path)
        if result["success"]:
            print(f"Success! Files changed: {len(result['files_changed'])}")
            
            for file_info in result['files_changed']:
                print(f"\nFile: {file_info['new_file']}")
                print(f"Changes: +{file_info['changes']['insertions']}, -{file_info['changes']['deletions']}")
                print(f"Hunks: {len(file_info['hunks'])}")
        else:
            print(f"Error: {result['message']}")
            print(result['raw_output'])
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Test the Git tool functions")
    parser.add_argument("--status", action="store_true", help="Test git_status")
    parser.add_argument("--log", action="store_true", help="Test git_log")
    parser.add_argument("--branch", action="store_true", help="Test git_branch")
    parser.add_argument("--diff", action="store_true", help="Test git_diff")
    parser.add_argument("--all", action="store_true", help="Test all Git functions")
    parser.add_argument("--count", type=int, default=5, help="Number of commits to show in log")
    parser.add_argument("--file", default="", help="File path for diff")
    
    args = parser.parse_args()
    
    # Run the requested tests
    if args.all or args.status:
        test_git_status()
    
    if args.all or args.log:
        test_git_log(count=args.count)
    
    if args.all or args.branch:
        test_git_branch()
    
    if args.all or args.diff:
        test_git_diff(file_path=args.file)
        
    # If no test was specified, run all tests
    if not (args.status or args.log or args.branch or args.diff or args.all):
        test_git_status()
        test_git_log()
        test_git_branch()
        test_git_diff() 