"""
ConfWatch Daemon Module
Provides file monitoring and automatic snapshot creation.
"""

from .watcher import FileWatcher
from .daemon import DaemonManager

__all__ = [
    "FileWatcher",
    "DaemonManager",
] 