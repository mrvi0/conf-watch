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
  confwatch snapshot ~/.bashrc -c "After installing nvm"
  confwatch snapshot -c "Daily backup" --force
  confwatch diff ~/.bashrc
  confwatch history ~/.bashrc
  confwatch tag ~/.bashrc "after-nvm-install"
  confwatch rollback ~/.bashrc abc1234
  confwatch web
  confwatch web --port 9000
  confwatch uninstall
  confwatch uninstall --force
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Snapshot command
    snapshot_parser = subparsers.add_parser('snapshot', help='Create snapshot of file(s)')
    snapshot_parser.add_argument('files', nargs='*', help='Files to snapshot (if empty, snapshot all monitored files)')
    snapshot_parser.add_argument('--comment', '-c', help='Add comment to snapshot')
    snapshot_parser.add_argument('--force', '-f', action='store_true', help='Force snapshot even if no changes detected')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Show differences for file')
    diff_parser.add_argument('file', help='File to show diff for')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show file history')
    history_parser.add_argument('file', help='File to show history for')
    
    # Tag command
    tag_parser = subparsers.add_parser('tag', help='Tag current version of file')
    tag_parser.add_argument('file', help='File to tag')
    tag_parser.add_argument('tag', help='Tag name')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback file to previous version')
    rollback_parser.add_argument('file', help='File to rollback')
    rollback_parser.add_argument('version', nargs='+', help='Version to rollback to (commit hash, tag, or version number)')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    web_parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List monitored files')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall ConfWatch')
    uninstall_parser.add_argument('--force', '-f', action='store_true', help='Force uninstall without confirmation')
    
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
        elif args.command == 'tag':
            handle_tag(args, config_file, repo_dir)
        elif args.command == 'rollback':
            handle_rollback(args, config_file, repo_dir)
        elif args.command == 'web':
            handle_web(args)
        elif args.command == 'list':
            handle_list(config_file)
        elif args.command == 'uninstall':
            handle_uninstall(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def handle_snapshot(args, config_file, repo_dir):
    scanner = FileScanner(config_file)
    storage = GitStorage(repo_dir)
    
    # Check if config is empty
    files = scanner.get_watched_files()
    if not files:
        print("No files configured for monitoring.")
        print("Please add files to ~/.confwatch/config/config.yml")
        print("Example:")
        print("  - ~/.bashrc")
        print("  - ~/.zshrc")
        print("  - ~/.env")
        return
    
    if args.files:
        for file_path in args.files:
            expanded_path = scanner.expand_path(file_path)
            if not os.path.exists(expanded_path):
                print(f"Warning: File not found: {file_path}")
                continue
            with open(expanded_path, 'r') as f:
                content = f.read()
            if storage.save_file(file_path, content, comment=args.comment or '', force=args.force):
                print(f"Snapshot created for {file_path}")
            else:
                print(f"No changes detected in {file_path}")
    else:
        for file_info in files:
            if file_info and file_info.get('exists'):
                with open(file_info['path'], 'r') as f:
                    content = f.read()
                if storage.save_file(file_info['original_path'], content, comment=args.comment or '', force=args.force):
                    print(f"Snapshot created for {file_info['original_path']}")
                else:
                    print(f"No changes detected in {file_info['original_path']}")
            elif file_info:
                print(f"Warning: File not found: {file_info['original_path']}")

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

def handle_tag(args, config_file, repo_dir):
    """Handle tag command."""
    storage = GitStorage(repo_dir)
    history = storage.get_file_history(args.file)
    if not history:
        print(f"No history found for {args.file}")
        return
    
    # Get the latest commit
    latest_commit = history[0]['hash']
    
    try:
        # Create tag
        storage.repo.create_tag(args.tag, latest_commit)
        print(f"Tagged version {latest_commit[:8]} as '{args.tag}' for {args.file}")
    except Exception as e:
        print(f"Error creating tag: {e}")

def handle_rollback(args, config_file, repo_dir):
    """Handle rollback command."""
    import subprocess
    storage = GitStorage(repo_dir)
    history = storage.get_file_history(args.file)
    if not history:
        print(f"No history found for {args.file}")
        return
    
    # Join version arguments to handle spaces
    target_version = ' '.join(args.version)
    
    # Check if it's a commit hash (40 characters)
    if len(target_version) == 40 and all(c in '0123456789abcdef' for c in target_version.lower()):
        commit_hash = target_version
    # Check if it's a short hash (7-8 characters)
    elif len(target_version) in [7, 8] and all(c in '0123456789abcdef' for c in target_version.lower()):
        # Find the full hash
        for entry in history:
            if entry['hash'].startswith(target_version):
                commit_hash = entry['hash']
                break
        else:
            print(f"Error: Commit hash '{target_version}' not found in history.")
            return
    # Check if it's a tag
    elif target_version.startswith('v'):
        try:
            commit_hash = storage.repo.git.rev_parse(target_version)
        except:
            print(f"Error: Tag '{target_version}' not found.")
            return
    else:
        # Try to find by comment
        found_commit = None
        for entry in history:
            if target_version in entry['message']:
                found_commit = entry['hash']
                break
        
        if found_commit:
            commit_hash = found_commit
        else:
            print(f"Error: Version '{target_version}' not found in history.")
            print("Available versions:")
            for entry in history:
                print(f"  {entry['hash'][:8]} - {entry['message'].split('Snapshot:')[0].strip()}")
            return
    
    try:
        # Получаем safe_name для файла
        safe_name = storage._safe_name(args.file)
        # Получаем содержимое файла из git по нужному коммиту
        file_content = storage.repo.git.show(f"{commit_hash}:{safe_name}")
        # Перезаписываем отслеживаемый файл этим содержимым
        scanner = FileScanner(config_file)
        expanded_path = scanner.expand_path(args.file)
        with open(expanded_path, 'w') as f:
            f.write(file_content)
        print(f"Restored {args.file} to state from commit {commit_hash[:8]}")
        # Создаём снапшот с комментарием
        rollback_comment = f"Rollback from commit {commit_hash[:8]}"
        if storage.save_file(args.file, file_content, comment=rollback_comment, force=True):
            print(f"Snapshot created for rollback: {rollback_comment}")
    except Exception as e:
        print(f"Error rolling back: {e}")

def handle_web(args):
    """Handle web command."""
    run_web_server(host=args.host, port=args.port, debug=args.debug)

def handle_list(config_file):
    """Handle list command."""
    try:
        scanner = FileScanner(config_file)
        files = scanner.get_watched_files()
        
        if not files:
            print("No files configured for monitoring.")
            print("Please add files to ~/.confwatch/config/config.yml")
            print("Example:")
            print("  - ~/.bashrc")
            print("  - ~/.zshrc")
            print("  - ~/.env")
            return
        
        print("Monitored Files:")
        print("=" * 50)
        
        for file_info in files:
            if file_info is None:
                print("Warning: file_info is None, skipping...")
                continue
            status = "✓" if file_info.get('exists') else "✗"
            print(f"{status} {file_info.get('original_path', 'Unknown')}")
            if not file_info.get('exists'):
                print(f"    (not found: {file_info.get('path', 'Unknown')})")
    except Exception as e:
        print(f"Error in handle_list: {e}")
        import traceback
        traceback.print_exc()

def handle_uninstall(args):
    """Handle uninstall command."""
    confwatch_home = os.path.expanduser("~/.confwatch")
    
    if not os.path.exists(confwatch_home):
        print("ConfWatch is not installed.")
        return
    
    if not args.force:
        print("This will completely remove ConfWatch and all its data.")
        print(f"Location: {confwatch_home}")
        response = input("Are you sure? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Uninstall cancelled.")
            return
    
    try:
        import shutil
        
        # Remove ConfWatch directory
        shutil.rmtree(confwatch_home)
        print(f"✓ Removed {confwatch_home}")
        
        # Remove from PATH in shell config files
        shell_configs = [
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.zshrc"),
            os.path.expanduser("~/.profile")
        ]
        
        for config_file in shell_configs:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                    
                    # Remove ConfWatch PATH lines
                    lines = content.split('\n')
                    filtered_lines = []
                    for line in lines:
                        if not line.strip().startswith('# ConfWatch') and confwatch_home not in line:
                            filtered_lines.append(line)
                    
                    if len(filtered_lines) != len(lines):
                        with open(config_file, 'w') as f:
                            f.write('\n'.join(filtered_lines))
                        print(f"✓ Removed from {config_file}")
                except Exception as e:
                    print(f"Warning: Could not update {config_file}: {e}")
        
        print("\nConfWatch has been uninstalled successfully!")
        print("Please restart your terminal or run 'source ~/.bashrc' to update your PATH.")
        
    except Exception as e:
        print(f"Error during uninstall: {e}")
        print("You may need to manually remove ~/.confwatch")

if __name__ == '__main__':
    main() 