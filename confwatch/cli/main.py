#!/usr/bin/env python3
"""
ConfWatch CLI - Command Line Interface
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from confwatch.core.scanner import FileScanner
from confwatch.core.storage import GitStorage
from confwatch.core.diff import DiffViewer
from confwatch.web.app import run_web_server

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ConfWatch - Configuration File Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  confwatch snapshot ~/.bashrc
  confwatch diff ~/.bashrc
  confwatch history ~/.bashrc
  confwatch web
  confwatch web --port 9000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Snapshot command
    snapshot_parser = subparsers.add_parser('snapshot', help='Create snapshot of file(s)')
    snapshot_parser.add_argument('files', nargs='*', help='Files to snapshot (if empty, snapshot all monitored files)')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Show differences for file')
    diff_parser.add_argument('file', help='File to show diff for')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show file history')
    history_parser.add_argument('file', help='File to show history for')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    web_parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List monitored files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Configuration
    confwatch_home = os.path.expanduser("~/.confwatch")
    config_file = os.path.join(confwatch_home, "config", "config.yml")
    repo_dir = os.path.join(confwatch_home, "repo")
    
    # Check if ConfWatch is installed
    if not os.path.exists(confwatch_home):
        print("Error: ConfWatch is not installed. Run ./install.sh first.")
        sys.exit(1)
    
    try:
        if args.command == 'snapshot':
            handle_snapshot(args, config_file, repo_dir)
        elif args.command == 'diff':
            handle_diff(args, config_file, repo_dir)
        elif args.command == 'history':
            handle_history(args, config_file, repo_dir)
        elif args.command == 'web':
            handle_web(args)
        elif args.command == 'list':
            handle_list(config_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def handle_snapshot(args, config_file, repo_dir):
    scanner = FileScanner(config_file)
    storage = GitStorage(repo_dir)
    if args.files:
        for file_path in args.files:
            expanded_path = scanner.expand_path(file_path)
            if not os.path.exists(expanded_path):
                print(f"Warning: File not found: {file_path}")
                continue
            with open(expanded_path, 'r') as f:
                content = f.read()
            if storage.save_file(file_path, content):
                print(f"Snapshot created for {file_path}")
            else:
                print(f"No changes detected in {file_path}")
    else:
        files = scanner.get_watched_files()
        for file_info in files:
            if file_info['exists']:
                with open(file_info['path'], 'r') as f:
                    content = f.read()
                if storage.save_file(file_info['original_path'], content):
                    print(f"Snapshot created for {file_info['original_path']}")
                else:
                    print(f"No changes detected in {file_info['original_path']}")

def handle_diff(args, config_file, repo_dir):
    scanner = FileScanner(config_file)
    storage = GitStorage(repo_dir)
    expanded_path = scanner.expand_path(args.file)
    if not os.path.exists(expanded_path):
        print(f"Error: File not found: {args.file}")
        return
    history = storage.get_file_history(args.file)
    if not history:
        print(f"No history found for {args.file}")
        return
    if len(history) < 2:
        print(f"No previous version found for {args.file}")
        return
    prev_commit = history[1]['hash']
    curr_commit = history[0]['hash']
    diff_output = storage.get_file_diff(args.file, prev_commit, curr_commit)
    print(diff_output)

def handle_history(args, config_file, repo_dir):
    storage = GitStorage(repo_dir)
    history = storage.get_file_history(args.file)
    if not history:
        print(f"No history found for {args.file}")
        return
    print(f"History for {args.file}:")
    print("=" * 50)
    for entry in history:
        print(f"[{entry['date']}] {entry['hash'][:8]} - {entry['message']}")

def handle_web(args):
    """Handle web command."""
    run_web_server(host=args.host, port=args.port, debug=args.debug)

def handle_list(config_file):
    """Handle list command."""
    scanner = FileScanner(config_file)
    files = scanner.get_watched_files()
    
    print("Monitored Files:")
    print("=" * 50)
    
    for file_info in files:
        status = "✓" if file_info['exists'] else "✗"
        print(f"{status} {file_info['original_path']}")
        if not file_info['exists']:
            print(f"    (not found: {file_info['path']})")

if __name__ == '__main__':
    main() 