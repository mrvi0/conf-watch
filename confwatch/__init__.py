"""
ConfWatch - Configuration File Monitor

A powerful tool for monitoring configuration files, maintaining version history,
and providing easy rollback capabilities.
"""

__version__ = "3.5.0"
__author__ = "Mr Vi"
__email__ = "support@b4dcat.ru"

from .core.scanner import FileScanner
from .core.storage import GitStorage, SQLiteStorage
from .core.diff import DiffViewer

__all__ = [
    "FileScanner",
    "GitStorage", 
    "SQLiteStorage",
    "DiffViewer",
] 