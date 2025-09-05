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
from confwatch.core.colors import print_header, print_success, print_error, print_warning, colored

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
  confwatch daemon start
  confwatch daemon stop
  confwatch daemon status
  confwatch web-daemon start --port 9000
  confwatch web-daemon stop
  confwatch web-daemon status
  confwatch completion bash --install
  confwatch completion zsh --install
  confwatch update
  confwatch update --force
  confwatch reset-password
  confwatch reset-password --force
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
    web_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    web_parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List monitored files')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall ConfWatch')
    uninstall_parser.add_argument('--force', '-f', action='store_true', help='Force uninstall without confirmation')
    
    # Reset password command
    reset_password_parser = subparsers.add_parser('reset-password', help='Reset web interface password')
    reset_password_parser.add_argument('--force', '-f', action='store_true', help='Force reset without confirmation')
    
    # Daemon commands
    daemon_parser = subparsers.add_parser('daemon', help='Manage file monitoring daemon')
    daemon_subparsers = daemon_parser.add_subparsers(dest='daemon_action', help='Daemon actions')
    
    # Daemon start
    daemon_start_parser = daemon_subparsers.add_parser('start', help='Start file monitoring daemon')
    daemon_start_parser.add_argument('--foreground', '-f', action='store_true', help='Run in foreground')
    daemon_start_parser.add_argument('--polling', '-p', action='store_true', help='Use polling instead of watchdog')
    
    # Daemon stop
    daemon_stop_parser = daemon_subparsers.add_parser('stop', help='Stop file monitoring daemon')
    
    # Daemon restart
    daemon_restart_parser = daemon_subparsers.add_parser('restart', help='Restart file monitoring daemon')
    daemon_restart_parser.add_argument('--polling', '-p', action='store_true', help='Use polling instead of watchdog')
    
    # Daemon status
    daemon_status_parser = daemon_subparsers.add_parser('status', help='Show daemon status')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update ConfWatch to latest version')
    update_parser.add_argument('--force', '-f', action='store_true', help='Force update without confirmation')
    update_parser.add_argument('--branch', default='main', help='Branch to update from (default: main)')
    
    # Web daemon commands
    web_daemon_parser = subparsers.add_parser('web-daemon', help='Manage persistent web server daemon')
    web_daemon_subparsers = web_daemon_parser.add_subparsers(dest='web_daemon_action', help='Web daemon actions')
    
    # Web daemon start
    web_daemon_start_parser = web_daemon_subparsers.add_parser('start', help='Start persistent web server daemon')
    web_daemon_start_parser.add_argument('--host', default=None, help='Host to bind to')
    web_daemon_start_parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    web_daemon_start_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    web_daemon_start_parser.add_argument('--foreground', '-f', action='store_true', help='Run in foreground')
    
    # Web daemon stop
    web_daemon_stop_parser = web_daemon_subparsers.add_parser('stop', help='Stop persistent web server daemon')
    
    # Web daemon restart
    web_daemon_restart_parser = web_daemon_subparsers.add_parser('restart', help='Restart persistent web server daemon')
    web_daemon_restart_parser.add_argument('--host', default=None, help='Host to bind to')
    web_daemon_restart_parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    web_daemon_restart_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Web daemon status
    web_daemon_status_parser = web_daemon_subparsers.add_parser('status', help='Show web daemon status')
    
    # Web daemon config
    web_daemon_config_parser = web_daemon_subparsers.add_parser('config', help='Configure web daemon settings')
    web_daemon_config_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    web_daemon_config_parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    web_daemon_config_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Completion command
    completion_parser = subparsers.add_parser('completion', help='Install shell completion')
    completion_parser.add_argument('shell', nargs='?', choices=['bash', 'zsh'], help='Shell type (bash or zsh)')
    completion_parser.add_argument('--install', action='store_true', help='Install completion automatically')
    completion_parser.add_argument('--output', help='Output directory for completion files')
    
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
        elif args.command == 'reset-password':
            handle_reset_password(args, config_file)
        elif args.command == 'daemon':
            handle_daemon(args, config_file, repo_dir)
        elif args.command == 'update':
            handle_update(args, config_file)
        elif args.command == 'web-daemon':
            handle_web_daemon(args, config_file)
        elif args.command == 'completion':
            handle_completion(args)
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
        # Find the full hash - check for multiple matches
        matching_commits = [entry for entry in history if entry['hash'].startswith(target_version)]
        if len(matching_commits) == 1:
            commit_hash = matching_commits[0]['hash']
        elif len(matching_commits) > 1:
            print(f"Error: Multiple commits found for prefix '{target_version}'. Please use full commit hash.")
            print("Matching commits:")
            for entry in matching_commits:
                print(f"  {entry['hash'][:8]} - {entry['message'].split('Snapshot:')[0].strip()}")
            return
        else:
            print(f"Error: Commit hash '{target_version}' not found in history.")
            return
    # Check if it's a tag
    elif target_version.startswith('v'):
        try:
            commit_hash = storage.repo.git.rev_parse(target_version)
        except Exception as e:
            print(f"Error: Tag '{target_version}' not found: {e}")
            return
    else:
        # Try to find by comment
        found_commits = []
        for entry in history:
            if target_version.lower() in entry['message'].lower():
                found_commits.append(entry)
        
        if len(found_commits) == 1:
            commit_hash = found_commits[0]['hash']
        elif len(found_commits) > 1:
            print(f"Error: Multiple commits found matching '{target_version}'. Please be more specific.")
            print("Matching commits:")
            for entry in found_commits:
                print(f"  {entry['hash'][:8]} - {entry['message'].split('Snapshot:')[0].strip()}")
            return
        else:
            print(f"Error: Version '{target_version}' not found in history.")
            print("Available versions:")
            for entry in history:
                print(f"  {entry['hash'][:8]} - {entry['message'].split('Snapshot:')[0].strip()}")
            return
    
    try:
        # Получаем safe_name для файла
        safe_name = storage._safe_name(args.file)
        
        # Проверяем, что файл существует в коммите
        try:
            file_content = storage.repo.git.show(f"{commit_hash}:{safe_name}")
        except Exception as e:
            print(f"Error: File not found in commit {commit_hash[:8]}: {e}")
            return
        
        # Перезаписываем отслеживаемый файл этим содержимым с правильной кодировкой
        scanner = FileScanner(config_file)
        expanded_path = scanner.expand_path(args.file)
        
        try:
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        except Exception as e:
            print(f"Error writing file {args.file}: {e}")
            return
        
        print(f"Restored {args.file} to state from commit {commit_hash[:8]}")
        
        # Создаём снапшот с комментарием
        rollback_comment = f"Rollback from commit {commit_hash[:8]}"
        if storage.save_file(args.file, file_content, comment=rollback_comment, force=True):
            print(f"Snapshot created for rollback: {rollback_comment}")
        else:
            print("Warning: Failed to create rollback snapshot")
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

def handle_reset_password(args, config_file):
    """Handle reset password command."""
    from confwatch.core.auth import AuthManager
    
    print_header("PASSWORD RESET", "yellow")
    
    auth = AuthManager(config_file)
    
    if not args.force:
        print("This will reset the web interface password.")
        print("You will need to use the new password to access the web interface.")
        print()
        response = input("Are you sure? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print_warning("Password reset cancelled.")
            return
    
    try:
        # Generate new password
        new_password = auth.generate_password()
        auth.save_password(new_password)
        
        print()
        print_success("Web interface password has been reset successfully!")
        print()
        print("=" * 50)
        print(colored("NEW PASSWORD:", "white", "bold"))
        print(colored(f"{new_password}", "green", "bold"))
        print("=" * 50)
        print()
        print_warning("IMPORTANT: Save this password! It won't be shown again.")
        print_success("You can now use this password to access the web interface.")
        
    except Exception as e:
        print_error(f"Error resetting password: {e}")

def handle_daemon(args, config_file, repo_dir):
    """Handle daemon commands."""
    from confwatch.daemon.daemon import DaemonManager
    
    daemon = DaemonManager(config_file, repo_dir)
    
    if not args.daemon_action:
        print("Error: No daemon action specified. Use 'start', 'stop', 'restart', or 'status'")
        return
    
    if args.daemon_action == 'start':
        use_watchdog = not args.polling
        background = not args.foreground
        
        if daemon.start(background=background, use_watchdog=use_watchdog):
            if background:
                print("✓ Daemon started successfully in background")
            else:
                print("✓ Daemon started in foreground")
        else:
            print("✗ Failed to start daemon")
            sys.exit(1)
    
    elif args.daemon_action == 'stop':
        if daemon.stop():
            print("✓ Daemon stopped successfully")
        else:
            print("✗ Failed to stop daemon")
            sys.exit(1)
    
    elif args.daemon_action == 'restart':
        use_watchdog = not args.polling
        if daemon.restart(use_watchdog=use_watchdog):
            print("✓ Daemon restarted successfully")
        else:
            print("✗ Failed to restart daemon")
            sys.exit(1)
    
    elif args.daemon_action == 'status':
        status = daemon.status()
        
        print("Daemon Status:")
        print("=" * 30)
        print(f"Running: {'Yes' if status['running'] else 'No'}")
        
        if status['running']:
            print(f"PID: {status['pid']}")
            print(f"Mode: {status.get('mode', 'unknown')}")
            print(f"Monitored files: {status.get('monitored_files', 0)}")
            print(f"Pending snapshots: {status.get('pending_snapshots', 0)}")
            print(f"Watchdog available: {'Yes' if status.get('watchdog_available', False) else 'No'}")
        
        print(f"PID file: {status['pid_file']}")
        print(f"Log file: {status['log_file']}")
        
        if 'watcher_error' in status:
            print(f"Watcher error: {status['watcher_error']}")

def handle_update(args, config_file):
    """Handle update command."""
    from confwatch.core.updater import ConfWatchUpdater
    
    updater = ConfWatchUpdater(config_file)
    success = updater.update(branch=args.branch, force=args.force)
    
    if not success:
        sys.exit(1)

def handle_web_daemon(args, config_file):
    """Handle web daemon commands."""
    from confwatch.core.web_daemon import WebDaemonManager
    
    web_daemon = WebDaemonManager(config_file)
    
    if not args.web_daemon_action:
        print("Error: No web daemon action specified. Use 'start', 'stop', 'restart', 'status', or 'config'")
        return
    
    if args.web_daemon_action == 'start':
        background = not args.foreground
        
        if web_daemon.start(
            background=background,
            host=args.host,
            port=args.port,
            debug=args.debug
        ):
            if background:
                print("✅ Web daemon started successfully in background")
            else:
                print("✅ Web daemon started in foreground")
        else:
            print("❌ Failed to start web daemon")
            sys.exit(1)
    
    elif args.web_daemon_action == 'stop':
        if web_daemon.stop():
            print("✅ Web daemon stopped successfully")
        else:
            print("❌ Failed to stop web daemon")
            sys.exit(1)
    
    elif args.web_daemon_action == 'restart':
        if web_daemon.restart(host=args.host, port=args.port, debug=args.debug):
            print("✅ Web daemon restarted successfully")
        else:
            print("❌ Failed to restart web daemon")
            sys.exit(1)
    
    elif args.web_daemon_action == 'status':
        status = web_daemon.status()
        
        print("Web Daemon Status:")
        print("=" * 30)
        print(f"Running: {'Yes' if status['running'] else 'No'}")
        
        if status['running']:
            print(f"PID: {status['pid']}")
            print(f"URL: http://{status['host']}:{status['port']}")
            print(f"Debug mode: {'Yes' if status['debug'] else 'No'}")
        
        print(f"Configuration file: {status['config_file']}")
        print(f"PID file: {status['pid_file']}")
        print(f"Log file: {status['log_file']}")
    
    elif args.web_daemon_action == 'config':
        web_daemon.save_config(host=args.host, port=args.port, debug=args.debug)
        print("✅ Web daemon configuration updated")
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print(f"Debug: {args.debug}")

def handle_completion(args):
    """Handle completion command."""
    import tempfile
    import shutil
    from confwatch.core.completion import CompletionGenerator
    
    generator = CompletionGenerator()
    
    # Determine shell
    if args.shell:
        shell = args.shell
    else:
        # Auto-detect shell
        import os
        shell_env = os.environ.get('SHELL', '/bin/bash')
        if 'zsh' in shell_env:
            shell = 'zsh'
        else:
            shell = 'bash'
        print(f"Auto-detected shell: {shell}")
    
    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = tempfile.mkdtemp()
    
    # Generate completion scripts
    bash_file, zsh_file = generator.save_completion_scripts(output_dir)
    
    if args.install:
        # Install completion automatically
        install_success = False
        
        if shell == 'bash':
            # Try to install bash completion
            bash_completion_dirs = [
                '/usr/share/bash-completion/completions',
                '/usr/local/share/bash-completion/completions',
                os.path.expanduser('~/.local/share/bash-completion/completions'),
                os.path.expanduser('~/.bash_completion.d')
            ]
            
            for completion_dir in bash_completion_dirs:
                try:
                    if os.path.exists(os.path.dirname(completion_dir)):
                        os.makedirs(completion_dir, exist_ok=True)
                        target_file = os.path.join(completion_dir, 'confwatch')
                        shutil.copy2(bash_file, target_file)
                        print(f"✅ Bash completion installed to: {target_file}")
                        print("Restart your shell or run: source ~/.bashrc")
                        install_success = True
                        break
                except (OSError, PermissionError):
                    continue
            
            if not install_success:
                print("❌ Could not install bash completion automatically.")
                print("Manual installation:")
                print(f"  sudo cp {bash_file} /usr/share/bash-completion/completions/confwatch")
                print("  # or")
                print(f"  mkdir -p ~/.bash_completion.d && cp {bash_file} ~/.bash_completion.d/confwatch")
        
        elif shell == 'zsh':
            # Try to install zsh completion
            zsh_completion_dirs = [
                '/usr/share/zsh/site-functions',
                '/usr/local/share/zsh/site-functions',
                os.path.expanduser('~/.local/share/zsh/site-functions')
            ]
            
            # Also check FPATH
            fpath = os.environ.get('FPATH', '').split(':')
            for path in fpath:
                if path and os.path.exists(path):
                    zsh_completion_dirs.append(path)
            
            for completion_dir in zsh_completion_dirs:
                try:
                    if os.path.exists(os.path.dirname(completion_dir)):
                        os.makedirs(completion_dir, exist_ok=True)
                        target_file = os.path.join(completion_dir, '_confwatch')
                        shutil.copy2(zsh_file, target_file)
                        print(f"✅ Zsh completion installed to: {target_file}")
                        print("Restart your shell or run: compinit")
                        install_success = True
                        break
                except (OSError, PermissionError):
                    continue
            
            if not install_success:
                print("❌ Could not install zsh completion automatically.")
                print("Manual installation:")
                print(f"  sudo cp {zsh_file} /usr/share/zsh/site-functions/_confwatch")
                print("  # or add to your ~/.zshrc:")
                print(f"  fpath=(~/.local/share/zsh/site-functions $fpath)")
                print(f"  mkdir -p ~/.local/share/zsh/site-functions && cp {zsh_file} ~/.local/share/zsh/site-functions/_confwatch")
    
    else:
        # Just show the files
        print("Completion files generated:")
        print(f"  Bash: {bash_file}")
        print(f"  Zsh:  {zsh_file}")
        print("")
        print("To install manually:")
        print("  Bash:")
        print(f"    sudo cp {bash_file} /usr/share/bash-completion/completions/confwatch")
        print("  Zsh:")
        print(f"    sudo cp {zsh_file} /usr/share/zsh/site-functions/_confwatch")
        print("")
        print("Or run with --install flag to install automatically")

if __name__ == '__main__':
    main() 