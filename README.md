# ConfWatch - Configuration File Monitor

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

```
 ██████╗ ██████╗ ███╗   ██╗███████╗██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗
██╔════╝██╔═══██╗████╗  ██║██╔════╝██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
██║     ██║   ██║██╔██╗ ██║█████╗  ██║ █╗ ██║███████║   ██║   ██║     ███████║
██║     ██║   ██║██║╚██╗██║██╔══╝  ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║
╚██████╗╚██████╔╝██║ ╚████║██║     ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝      ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
```

ConfWatch is a Python-based tool for monitoring and versioning configuration files. It provides a powerful CLI and a terminal-style web interface for managing configuration file changes, history, and diffs. **Now with secure authentication - each installation gets a unique password!**

---

## Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [One-line install (recommended)](#one-line-install-recommended)
  - [Development install](#development-install)
- [Configuration](#configuration)
- [CLI Usage](#cli-usage)
- [Web Interface](#web-interface)
- [Snapshots, Safe Name, and File Storage](#snapshots-safe-name-and-file-storage)
- [Directory Structure](#directory-structure)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Development](#development)
- [License](#license)

---

## Features
- **Monitor any config files** (dotfiles, .env, /etc/*, etc.)
- **Automatic versioning** (Git-based, per-file, with unique safe names)
- **History for every file** (see all changes, with date and comment)
- **Diff between any two snapshots** (choose any two versions to compare)
- **Terminal-style web interface** (for easy browsing and diff viewing)
- **Custom checkboxes and controls** (all styled for terminal look)
- **Animated CLI demo in web** (see usage examples live)
- **Secure authentication** (unique password per installation)
- **Automatic file monitoring** (watchdog + polling modes with daemon)
- **Remote web access** (accessible from any IP, not just localhost)
- **Easy install/uninstall** (user and dev modes)
- **Isolated virtualenv** (no system Python pollution)

---

## Installation

### One-line install (recommended for users)

```bash
curl -fsSL https://raw.githubusercontent.com/mrvi0/conf-watch/main/install.sh | bash
```

- Installs to `~/.confwatch/`
- Adds `confwatch` to your PATH (via .bashrc/.zshrc)
- Creates virtualenv, config, repo, web, launcher
- All dependencies are installed automatically

### Development install (for contributors)

```bash
git clone https://github.com/mrvi0/conf-watch.git
cd conf-watch
./install-dev.sh
```
- Installs to `~/.confwatch/` (but uses local sources)
- For development, testing, and PRs

---

## Configuration

Edit `~/.confwatch/config/config.yml` to specify which files to monitor:

```yaml
# List of files to monitor (one per line, starting with -)
- ~/.bashrc
- ~/.zshrc
- ~/.ssh/config
- ~/.env
- /etc/nginx/nginx.conf
```

- You can use `~` and environment variables in paths.
- After editing config, run `confwatch snapshot` to create initial versions.

---

## CLI Usage

```bash
confwatch list                    # List monitored files
confwatch snapshot [files...]     # Create snapshots (all or specific files)
confwatch snapshot --comment "msg" # Create snapshot with comment
confwatch diff <file>             # Show diff (latest vs previous)
confwatch history <file>          # Show file history (with commit hashes)
confwatch tag <file> <tag>        # Tag current version
confwatch rollback <file> <ver>   # Rollback to specific version
confwatch web [options]           # Start web interface (one-time)
confwatch web-daemon start        # Start persistent web server daemon
confwatch web-daemon stop         # Stop persistent web server daemon
confwatch web-daemon status       # Show web daemon status
confwatch daemon start            # Start automatic file monitoring
confwatch daemon stop             # Stop automatic file monitoring
confwatch daemon status           # Show daemon status
confwatch completion --install    # Install shell autocompletion
confwatch reset-password          # Reset web interface password
confwatch update                  # Update ConfWatch to latest version
confwatch --help                  # Show all commands
```

#### Examples
```bash
confwatch snapshot ~/.bashrc --comment "After installing nvm"
confwatch snapshot --comment "Daily backup" --force
confwatch diff ~/.env
confwatch history /etc/nginx/nginx.conf
confwatch tag ~/.bashrc "after-nvm-install"
confwatch rollback ~/.bashrc abc1234
confwatch web --port 9000                # One-time web server
confwatch web-daemon start --port 8080  # Persistent web daemon
confwatch web-daemon config --port 9000 # Configure web daemon
confwatch daemon start --foreground     # Start monitoring in foreground
confwatch daemon start --polling        # Use polling instead of watchdog
confwatch daemon restart
confwatch completion bash --install     # Install bash completion
confwatch completion zsh --install      # Install zsh completion
confwatch update --force                # Force update without confirmation
confwatch reset-password --force
```

---

## Web Interface

- Start with `confwatch web` (default: http://0.0.0.0:8080)
- **Remote access** - accessible from any IP address, not just localhost
- **Secure authentication** - each installation gets a unique password
- Browse all monitored files, see status and history
- Click [HISTORY] to see all snapshots for a file
- Select any two snapshots and click [SHOW DIFF] to compare them
- All controls (checkboxes, buttons) styled as in a terminal
- Animated CLI demo at the top (shows usage examples)
- Logout button in the terminal header

**[SCREENSHOT PLACEHOLDER: Main web interface with file list, status, and animated CLI demo]**
**[SCREENSHOT PLACEHOLDER: File history view with custom checkboxes and [SHOW DIFF] button]**
**[SCREENSHOT PLACEHOLDER: Diff view between two arbitrary snapshots]**

---

## Persistent Web Daemon

For production use, you can run a persistent web server daemon that starts automatically and remembers its configuration:

### Setup and Start
```bash
confwatch web-daemon config --host 0.0.0.0 --port 8080  # Configure settings
confwatch web-daemon start                              # Start in background
```

### Management
```bash
confwatch web-daemon status      # Check if running
confwatch web-daemon stop        # Stop daemon  
confwatch web-daemon restart     # Restart with saved config
```

### Features
- **Configuration persistence** - settings saved in `~/.confwatch/web_daemon.conf`
- **Background operation** - runs as daemon with PID file management
- **Automatic restart** - remembers host, port, debug settings
- **Logging** - output goes to `~/.confwatch/web_daemon.log`
- **Process management** - proper start/stop/restart with PID tracking

### Difference from regular web command
- **`confwatch web`** - one-time server with command-line parameters
- **`confwatch web-daemon`** - persistent daemon with saved configuration

---

## Shell Autocompletion

ConfWatch supports intelligent autocompletion for bash and zsh shells:

### Automatic Installation
Autocompletion is installed automatically during ConfWatch setup. If you need to reinstall or install manually:

```bash
confwatch completion --install          # Auto-detect shell and install
confwatch completion bash --install     # Install for bash
confwatch completion zsh --install      # Install for zsh
```

### Features
- **Command completion** - `confwatch <TAB>` shows all available commands
- **Subcommand completion** - `confwatch web-daemon <TAB>` shows start, stop, restart, etc.
- **Option completion** - `confwatch daemon start --<TAB>` shows available flags
- **File path completion** - `confwatch snapshot <TAB>` completes file paths
- **Context-aware** - different options for different commands and subcommands

### Manual Setup
If automatic installation fails, you can install manually:

```bash
# Generate completion files
confwatch completion --output /tmp/completion

# Install manually
sudo cp /tmp/completion/confwatch-completion.bash /usr/share/bash-completion/completions/confwatch
sudo cp /tmp/completion/_confwatch /usr/share/zsh/site-functions/_confwatch
```

After installation, restart your shell or run:
- **Bash**: `source ~/.bashrc`
- **Zsh**: `compinit`

---

## Automatic File Monitoring

ConfWatch can automatically monitor your configuration files and create snapshots when they change:

### Start Monitoring
```bash
confwatch daemon start              # Start in background (recommended)
confwatch daemon start --foreground # Start in foreground for debugging
confwatch daemon start --polling    # Use polling instead of watchdog
```

### Monitor Status
```bash
confwatch daemon status             # Check if daemon is running
```

### Stop Monitoring
```bash
confwatch daemon stop               # Stop background monitoring
confwatch daemon restart            # Restart daemon
```

### How it Works
- **Watchdog mode** (default): Uses system file events (inotify on Linux) for instant detection
- **Polling mode** (fallback): Checks files every 30 seconds using hash comparison
- **Debouncing**: Waits 5 seconds after last change before creating snapshot
- **Auto comments**: Snapshots get `[AUTO]` prefix with timestamp
- **Smart filtering**: Ignores temporary files (.swp, .tmp, .bak, etc.)

### Logs
- **PID file**: `~/.confwatch/daemon.pid`
- **Log file**: `~/.confwatch/daemon.log`
- **Background mode**: All output goes to log file
- **Foreground mode**: Output to terminal

---

## Snapshots, Safe Name, and File Storage

- **Every file** is tracked by its absolute path, but stored in the repo as a unique "safe name":
  - `safe_name = sha256(abs_path) + '_' + filename`
  - This prevents conflicts for files with the same name in different folders.
- **In the UI and CLI** you always see the original file path and short git commit hashes.
- **In the repo** you may see long filenames — this is normal and ensures uniqueness.
- **Snapshots** are git commits, each with a hash, date, and optional comment.
- **Diff** can be shown between any two snapshots (not just latest vs previous).

---

## Directory Structure

After install, you will have:

```
~/.confwatch/
├── venv/                # Python virtual environment
├── config/config.yml    # List of monitored files
├── repo/                # Git repo with all file versions (safe names)
├── web/                 # Web UI static files
├── confwatch            # Launcher script (added to PATH)
└── confwatch-module/    # All Python code (core, cli, web)
```

---

## Troubleshooting

- **confwatch: command not found**
  - Run `source ~/.bashrc` or restart your terminal
  - Make sure `~/.confwatch/` is in your PATH
- **Python/pip/git not found**
  - Install Python 3.7+, pip, and git
- **Web interface not opening**
  - Make sure nothing else is using port 8080 (or use `confwatch web --port 9000`)
  - Check if firewall is blocking the port for remote access
- **Permission errors**
  - Ensure you have write access to `~/.confwatch`
- **How to uninstall?**
  - Run `./uninstall.sh` from the repo or remove `~/.confwatch` and clean up PATH in your shell config

---

## FAQ

**Q: Why are some files in the repo named with a long hash?**
A: This is the "safe name" — a unique identifier for each file, based on its absolute path. It prevents conflicts between files with the same name in different folders. In the UI and CLI you always see the original file path and short commit hashes.

**Q: How do I compare any two snapshots?**
A: In the web interface, open HISTORY for a file, select any two versions, and click [SHOW DIFF].

**Q: How do I update ConfWatch?**
A: Pull the latest code and run `./install.sh` again.

**Q: How do I add/remove files from monitoring?**
A: Edit `~/.confwatch/config/config.yml` and run `confwatch snapshot`.

**Q: How do I use a different port for the web interface?**
A: `confwatch web --port 9000`

**Q: How do I reset the web interface password?**
A: `confwatch reset-password` (with confirmation) or `confwatch reset-password --force`

**Q: What if I forgot my web interface password?**
A: Use `confwatch reset-password` to generate a new one.

**Q: How does automatic monitoring work?**
A: Run `confwatch daemon start` to monitor files. It uses watchdog (inotify) for instant detection or falls back to polling every 30 seconds. Creates snapshots automatically with `[AUTO]` prefix.

**Q: Can I access the web interface from another computer?**
A: Yes! The web server binds to `0.0.0.0:8080` by default, making it accessible from any IP. Just make sure your firewall allows the port.

**Q: How do I update ConfWatch?**
A: Run `confwatch update` to automatically update to the latest version. Your configuration and file history are preserved during updates.

**Q: What's the difference between web and web-daemon?**
A: `confwatch web` starts a one-time server, while `confwatch web-daemon` runs a persistent daemon that remembers its configuration and can be managed like a system service.

**Q: How do I enable autocompletion?**
A: Autocompletion is installed automatically. If it's not working, run `confwatch completion --install` and restart your shell.

**Q: How do I develop or contribute?**
A: See [Development](#development) below.

---

## Development

- Clone the repo and run `./install-dev.sh` (see above)
- All code is in `confwatch-module/` (core, cli, web)
- Web UI is in `confwatch/web/static/`
- To run tests: `python -m pytest`
- To run web in dev mode: `python -m confwatch.cli.main web --debug`
- PRs and issues welcome!

---

## License
[MIT](LICENSE)
