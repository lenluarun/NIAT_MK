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
