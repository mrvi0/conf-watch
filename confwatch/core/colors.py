"""
Terminal color utilities for ConfWatch.
Provides colored output for better readability.
"""

import sys
import os


class Colors:
    """ANSI color codes for terminal output."""
    
    # Basic colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Reset
    RESET = '\033[0m'
    
    @classmethod
    def is_supported(cls) -> bool:
        """Check if terminal supports colors."""
        # Check if stdout is a terminal and colors are supported
        if not sys.stdout.isatty():
            return False
        
        # Check TERM environment variable
        term = os.environ.get('TERM', '')
        if 'color' in term or term in ['xterm', 'xterm-256color', 'screen', 'linux']:
            return True
        
        # Check NO_COLOR environment variable
        if os.environ.get('NO_COLOR'):
            return False
        
        return True


def colored(text: str, color: str = '', style: str = '') -> str:
    """
    Return colored text if terminal supports it.
    
    Args:
        text: Text to color
        color: Color name (red, green, yellow, blue, magenta, cyan, white, gray)
        style: Style name (bold, underline)
    
    Returns:
        Colored text or plain text if colors not supported
    """
    if not Colors.is_supported():
        return text
    
    color_map = {
        'red': Colors.RED,
        'green': Colors.GREEN,
        'yellow': Colors.YELLOW,
        'blue': Colors.BLUE,
        'magenta': Colors.MAGENTA,
        'cyan': Colors.CYAN,
        'white': Colors.WHITE,
        'gray': Colors.GRAY,
    }
    
    style_map = {
        'bold': Colors.BOLD,
        'underline': Colors.UNDERLINE,
    }
    
    prefix = ''
    if style and style in style_map:
        prefix += style_map[style]
    if color and color in color_map:
        prefix += color_map[color]
    
    if prefix:
        return f"{prefix}{text}{Colors.RESET}"
    return text


def print_colored(text: str, color: str = '', style: str = '', **kwargs):
    """Print colored text."""
    print(colored(text, color, style), **kwargs)


def print_header(text: str, color: str = 'cyan', style: str = 'bold'):
    """Print a colored header."""
    print_colored(f"[{text}]", color, style)


def print_success(text: str):
    """Print success message in green."""
    print_colored(f"✅ {text}", 'green')


def print_error(text: str):
    """Print error message in red."""
    print_colored(f"❌ {text}", 'red')


def print_warning(text: str):
    """Print warning message in yellow."""
    print_colored(f"⚠️  {text}", 'yellow')


def print_info(text: str):
    """Print info message in blue."""
    print_colored(f"ℹ️  {text}", 'blue') 