"""
Colors and formatting for terminal output
"""

class Colors:
    """ANSI color codes for terminal"""
    # Regular Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright Colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background Colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    RESET_COLOR = '\033[39m'
    RESET_BG = '\033[49m'


# Theme definitions with color schemes
THEMES = {
    "neon": {
        "primary": Colors.BRIGHT_CYAN,
        "secondary": Colors.BRIGHT_MAGENTA,
        "accent": Colors.BRIGHT_BLUE,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_CYAN,
        "dim": Colors.DIM,
    },
    "matrix": {
        "primary": Colors.BRIGHT_GREEN,
        "secondary": Colors.GREEN,
        "accent": Colors.BRIGHT_GREEN,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_GREEN,
        "dim": Colors.DIM,
    },
    "abyss": {
        "primary": Colors.BRIGHT_BLUE,
        "secondary": Colors.BRIGHT_CYAN,
        "accent": Colors.BRIGHT_MAGENTA,
        "success": Colors.BRIGHT_CYAN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_BLUE,
        "dim": Colors.DIM,
    },
    "phantom": {
        "primary": Colors.BRIGHT_RED,
        "secondary": Colors.BRIGHT_MAGENTA,
        "accent": Colors.BRIGHT_YELLOW,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_RED,
        "dim": Colors.DIM,
    },
    "e2c": {
        "primary": Colors.BRIGHT_GREEN,
        "secondary": Colors.BRIGHT_CYAN,
        "accent": Colors.BRIGHT_YELLOW,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_CYAN,
        "dim": Colors.DIM,
    },
    "sunset": {
        "primary": Colors.BRIGHT_YELLOW,
        "secondary": Colors.BRIGHT_RED,
        "accent": Colors.BRIGHT_MAGENTA,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_YELLOW,
        "dim": Colors.DIM,
    },
    "ocean": {
        "primary": Colors.BRIGHT_CYAN,
        "secondary": Colors.BRIGHT_BLUE,
        "accent": Colors.BRIGHT_MAGENTA,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_CYAN,
        "dim": Colors.DIM,
    },
    "fire": {
        "primary": Colors.BRIGHT_RED,
        "secondary": Colors.BRIGHT_YELLOW,
        "accent": Colors.BRIGHT_MAGENTA,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_WHITE,
        "highlight": Colors.BRIGHT_RED,
        "dim": Colors.DIM,
    },
}


def get_theme(theme_name="neon"):
    """Get theme colors by name."""
    return THEMES.get(theme_name, THEMES["neon"])


def colored(text, color):
    """Apply color to text."""
    return f"{color}{text}{Colors.RESET}"


def bold(text):
    """Make text bold."""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def dim(text):
    """Make text dim."""
    return f"{Colors.DIM}{text}{Colors.RESET}"


def underline(text):
    """Underline text."""
    return f"{Colors.UNDERLINE}{text}{Colors.RESET}"


def success(text):
    """Format success message."""
    return colored(f"✓ {text}", Colors.BRIGHT_GREEN)


def error(text):
    """Format error message."""
    return colored(f"✗ {text}", Colors.BRIGHT_RED)


def warning(text):
    """Format warning message."""
    return colored(f"⚠ {text}", Colors.BRIGHT_YELLOW)


def info(text):
    """Format info message."""
    return colored(f"ℹ {text}", Colors.BRIGHT_CYAN)


def highlight(text):
    """Highlight text."""
    return colored(text, Colors.BRIGHT_CYAN)


def separator(char="─", length=60):
    """Create a separator line."""
    return char * length


def themed_colored(text, color_key, theme_name="neon"):
    """Apply theme-specific color to text."""
    theme = get_theme(theme_name)
    color = theme.get(color_key, Colors.RESET)
    return colored(text, color)
    RESET_FORMAT = '\033[0m'


def bold(text):
    """Make text bold"""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def colored(text, color):
    """Colorize text"""
    return f"{color}{text}{Colors.RESET}"


def success(text):
    """Green bold text"""
    return f"{Colors.BOLD}{Colors.BRIGHT_GREEN}{text}{Colors.RESET}"


def error(text):
    """Red bold text"""
    return f"{Colors.BOLD}{Colors.BRIGHT_RED}{text}{Colors.RESET}"


def warning(text):
    """Yellow bold text"""
    return f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}{text}{Colors.RESET}"


def info(text):
    """Blue bold text"""
    return f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{text}{Colors.RESET}"


def highlight(text, bg_color=Colors.BG_BLUE):
    """Highlight text with background"""
    return f"{bg_color}{Colors.WHITE}{Colors.BOLD}{text}{Colors.RESET}"


def separator(char="─", length=60, color=Colors.BRIGHT_CYAN):
    """Print a colored separator"""
    return f"{color}{char * length}{Colors.RESET}"
