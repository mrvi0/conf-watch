"""
ConfWatch - Configuration File Monitor

A powerful tool for monitoring configuration files, maintaining version history,
and providing easy rollback capabilities.
"""

__version__ = "1.0.0"
__author__ = "ConfWatch Team"
__email__ = "confwatch@example.com"

from .core.scanner import FileScanner
from .core.storage import GitStorage, SQLiteStorage
from .core.diff import DiffViewer

__all__ = [
    "FileScanner",
    "GitStorage", 
    "SQLiteStorage",
    "DiffViewer",
] 