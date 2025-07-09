# ConfWatch 🔍

[English](#english) | [Русский](docs/ru/README.md)

---

## English

### What is ConfWatch?

ConfWatch is a powerful configuration file monitoring tool that tracks changes in your system configuration files, maintains version history, and provides easy rollback capabilities.

### 🚀 Quick Install

```bash
# Install in one command
curl -fsSL https://raw.githubusercontent.com/yourusername/conf-watch/main/install.sh | bash
```

The installer will automatically detect your system and install the appropriate version:
- **Python version** (if Python 3.8+ is available) - Full-featured with web interface
- **Bash version** (fallback) - Lightweight, no dependencies

### 🧠 Key Features

- **📁 File Monitoring**: Automatically tracks changes in configuration files (`.bashrc`, `/etc/nginx/nginx.conf`, `.env`, `~/.config/`, etc.)
- **💾 Version History**: Stores every version in SQLite or Git repository
- **🔍 Diff Viewing**: Shows differences between versions with syntax highlighting
- **↩️ Rollback**: Easily revert to previous versions
- **🔔 Notifications**: Optional alerts via Telegram, email, and other channels
- **🏷️ Version Tagging**: Tag snapshots with meaningful comments
- **🔒 Encryption**: Secure storage for sensitive configuration data
- **🌐 Web Interface**: Beautiful web UI for managing configurations (planned)
- **🔄 Sync**: Synchronize history between multiple machines

### 🧪 How It Works

#### 1. Scanning
ConfWatch periodically scans specified file paths for changes:

```yaml
watch:
  - ~/.bashrc
  - ~/.config/nvim/init.vim
  - /etc/nginx/nginx.conf
  - ~/projects/.env
```

#### 2. Change Detection
Each file is hashed (SHA256) and compared with the previous version. If the hash changes, a new copy is saved.

#### 3. Storage Options
- **Git Repository**: Easy diffing, built-in history, sync capabilities
- **SQLite Database**: Simple embedded format, easy web integration, compression support

### 🚀 Quick Start

#### Installation

**Option 1: One-command install (Recommended)**
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/conf-watch/main/install.sh | bash
```

**Option 2: Manual installation**
```bash
# Clone the repository
git clone https://github.com/yourusername/conf-watch.git
cd conf-watch

# Run installer
./install.sh
```

The installer automatically chooses the best version for your system:
- **Python version**: Full-featured with web interface, notifications, encryption
- **Bash version**: Lightweight, works everywhere, no dependencies

#### Basic Usage

```bash
# Create initial snapshot
confwatch snapshot

# View differences
confwatch diff ~/.bashrc

# Tag a version
confwatch tag ~/.bashrc "after nvm installation"

# Start monitoring daemon
confwatchd --config ~/confwatch.yml
```

### 📋 Configuration

Create `~/.confwatch/config.yml`:

```yaml
# Files to monitor
watch:
  - ~/.bashrc
  - ~/.zshrc
  - ~/.config/nvim/init.vim
  - /etc/nginx/nginx.conf
  - ~/projects/.env

# Storage settings
storage:
  type: "sqlite"  # or "git"
  path: "~/.confwatch/database.db"

# Notification settings
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"

# Monitoring settings
monitoring:
  interval: 300  # seconds
  auto_test:
    nginx: "nginx -t"
    apache: "apache2ctl configtest"
```

### 🔍 Usage Examples

#### Manual Mode
```bash
# Create snapshot
confwatch snapshot

# View differences
confwatch diff /etc/hosts

# List all versions
confwatch history ~/.bashrc

# Rollback to previous version
confwatch rollback ~/.bashrc --version 3
```

#### Daemon Mode
```bash
# Start monitoring daemon
confwatchd --config ~/confwatch.yml

# Check daemon status
confwatchd status

# Stop daemon
confwatchd stop
```

### 🎯 Advanced Features

#### Version Tagging
```bash
# Tag current version
confwatch tag ~/.bashrc "after installing nodejs"

# List tags
confwatch tags ~/.bashrc

# Rollback to tagged version
confwatch rollback ~/.bashrc --tag "after installing nodejs"
```

#### Auto-testing Configurations
```bash
# Test nginx config after changes
confwatch auto-test nginx

# Test apache config
confwatch auto-test apache
```

#### Encryption
```bash
# Enable encryption for sensitive files
confwatch encrypt ~/.env

# Decrypt for viewing
confwatch decrypt ~/.env
```

### 🌐 Web Interface

**Bash Version:**
```bash
# Start web server
cd ~/.confwatch/web
./api.sh

# Open in browser
open http://localhost:8080
```

**Python Version:**
```bash
# Start web server
confwatch web

# Open in browser
open http://localhost:5000
```

The web interface provides:
- File list with change frequency
- Beautiful diff viewer with syntax highlighting
- One-click rollback functionality
- Audit trail with user and timestamp information
- Real-time monitoring dashboard

### 🔧 Development

#### Prerequisites
- Python 3.8+
- SQLite3 or Git
- Optional: Telegram Bot API token

#### Building from Source
```bash
git clone https://github.com/yourusername/conf-watch.git
cd conf-watch
pip install -e .
```

#### Running Tests
```bash
pytest tests/
```

### 📦 Project Structure

```
conf-watch/
├── python/                    # Python version (full-featured)
│   ├── confwatch/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── scanner.py
│   │   │   ├── storage.py
│   │   │   └── diff.py
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── daemon/
│   │   └── web/
│   ├── tests/
│   └── requirements.txt
├── bash/                      # Bash version (lightweight)
│   ├── confwatch             # Main script
│   ├── confwatchd            # Daemon script
│   └── web/
│       ├── index.html        # Web interface
│       └── api.sh            # API server
├── docs/
│   ├── ru/
│   │   └── README.md
│   └── en/
├── install.sh                 # Smart installer
└── README.md
```

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 