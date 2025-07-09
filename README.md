# ConfWatch - Configuration File Monitor

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

ConfWatch is a Python-based tool for monitoring and versioning configuration files. It provides both command-line interface and web interface for managing configuration file changes.

## Features

- **File Monitoring**: Monitor multiple configuration files simultaneously
- **Version Control**: Automatic Git-based versioning of file changes
- **Diff Viewing**: View differences between file versions
- **Web Interface**: Modern web UI for managing files and viewing changes
- **CLI Interface**: Command-line tools for automation
- **Virtual Environment**: Isolated Python environment to avoid system conflicts

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/conf-watch.git
cd conf-watch

# Install ConfWatch
./install.sh
```

### Basic Usage

```bash
# List monitored files
confwatch list

# Create snapshot of a file
confwatch snapshot ~/.bashrc

# View differences
confwatch diff ~/.bashrc

# View file history
confwatch history ~/.bashrc

# Start web interface
confwatch web
```

## Installation Details

The installer creates:

- **Virtual Environment**: `~/.confwatch/venv/` - Isolated Python environment
- **Configuration**: `~/.confwatch/config/config.yml` - List of monitored files
- **Repository**: `~/.confwatch/repo/` - Git repository for file versions
- **Web Interface**: `~/.confwatch/web/` - Web UI files
- **Launcher**: `~/.confwatch/confwatch` - Executable script

### Requirements

- Python 3.7 or higher
- Git
- pip

### Dependencies

All dependencies are installed in a virtual environment:

- Flask - Web framework
- PyYAML - Configuration file parsing
- GitPython - Git operations
- Click - CLI framework
- Watchdog - File system monitoring

## Configuration

Edit `~/.confwatch/config/config.yml` to specify which files to monitor:

```yaml
# ConfWatch Configuration
# List of files to monitor (one per line, starting with -)

# Shell configuration files
- ~/.bashrc
- ~/.zshrc
- ~/.bash_profile

# SSH configuration
- ~/.ssh/config

# Git configuration
- ~/.gitconfig

# Editor configuration
- ~/.vimrc
- ~/.config/nvim/init.vim

# Application configuration
- ~/.config/terminator/config
- ~/.config/alacritty/alacritty.yml

# Environment files
- ~/.env
- ~/.bash_aliases
```

## Commands

### CLI Commands

```bash
confwatch list                    # List monitored files
confwatch snapshot [files...]     # Create snapshots
confwatch diff <file>             # Show differences
confwatch history <file>          # Show file history
confwatch web [options]           # Start web interface
```

### Web Interface Options

```bash
confwatch web                     # Start on localhost:8080
confwatch web --port 9000         # Use custom port
confwatch web --host 0.0.0.0      # Bind to all interfaces
confwatch web --debug             # Enable debug mode
```

## Web Interface

The web interface provides:

- **File List**: View all monitored files with status
- **Diff Viewer**: Side-by-side diff comparison
- **History**: View file change history
- **Snapshot Creation**: Create snapshots from the web UI
- **Real-time Updates**: Refresh to see latest changes

Access the web interface at `http://localhost:8080` after running `confwatch web`.

## Architecture

```
confwatch/
├── core/              # Core functionality
│   ├── scanner.py     # File scanning and monitoring
│   ├── storage.py     # Git-based file storage
│   └── diff.py        # Diff generation and viewing
├── web/               # Web interface
│   └── app.py         # Flask web application
└── cli/               # Command-line interface
    └── main.py        # CLI entry point
```

## Development

### Setup Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Run development server
python -m confwatch.cli.main web --debug
```

### Project Structure

```
conf-watch/
├── confwatch/         # Main package
├── requirements.txt   # Python dependencies
├── install.sh        # Installation script
├── uninstall.sh      # Uninstallation script
└── README.md         # This file
```

## Troubleshooting

### Common Issues

1. **"Python not found"**: Install Python 3.7+ from python.org
2. **"pip not found"**: Install pip: `python3 -m ensurepip --upgrade`
3. **"Git not found"**: Install Git from git-scm.com
4. **Permission errors**: Ensure you have write access to `~/.confwatch`

### Logs

Check the terminal output for error messages. The web interface also shows errors in the browser console.

### Reinstallation

If you encounter issues, you can reinstall:

```bash
./uninstall.sh
./install.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check this README and inline code comments
- **Web Interface**: Use the built-in help and status messages

---

**ConfWatch** - Keep your configuration files under control! 🔍 