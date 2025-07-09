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
- **Easy install/uninstall** (user and dev modes)
- **Isolated virtualenv** (no system Python pollution)

---

## Installation

### One-line install (recommended for users)

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/conf-watch/main/install.sh | bash
```

- Installs to `~/.confwatch/`
- Adds `confwatch` to your PATH (via .bashrc/.zshrc)
- Creates virtualenv, config, repo, web, launcher
- All dependencies are installed automatically

### Development install (for contributors)

```bash
git clone https://github.com/yourusername/conf-watch.git
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
confwatch web [options]           # Start web interface
confwatch reset-password          # Reset web interface password
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
confwatch web --port 9000
confwatch reset-password --force
```

---

## Web Interface

- Start with `confwatch web` (default: http://localhost:8080)
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
[MIT](LICENCE)