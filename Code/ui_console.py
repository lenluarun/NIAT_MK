"""
Terminal UI helpers for cyber-style interface.
"""
import os
import time
from colors import Colors, colored, separator


THEME_BANNERS = {
    "neon": [
        ("  ███╗   ██╗██╗ █████╗ ████████╗    ███╗   ███╗██╗  ██╗", Colors.BRIGHT_CYAN),
        ("  ████╗  ██║██║██╔══██╗╚══██╔══╝    ████╗ ████║██║ ██╔╝", Colors.BRIGHT_MAGENTA),
        ("  ██╔██╗ ██║██║███████║   ██║       ██╔████╔██║█████╔╝ ", Colors.BRIGHT_BLUE),
        ("  ██║╚██╗██║██║██╔══██║   ██║       ██║╚██╔╝██║██╔═██╗ ", Colors.BRIGHT_YELLOW),
        ("  ██║ ╚████║██║██║  ██║   ██║       ██║ ╚═╝ ██║██║  ██╗", Colors.BRIGHT_GREEN),
        ("  ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝", Colors.BRIGHT_CYAN),
    ],
    "metasploit": [
        ("  ███╗   ███╗███████╗████████╗ █████╗ ███████╗██████╗ ██╗      ██████╗ ██╗████████╗", Colors.BRIGHT_GREEN),
        ("  ████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██║     ██╔═══██╗██║╚══██╔══╝", Colors.BRIGHT_CYAN),
        ("  ██╔████╔██║█████╗     ██║   ███████║███████╗██████╔╝██║     ██║   ██║██║   ██║   ", Colors.BRIGHT_YELLOW),
        ("  ██║╚██╔╝██║██╔══╝     ██║   ██╔══██║╚════██║██╔═══╝ ██║     ██║   ██║██║   ██║   ", Colors.BRIGHT_MAGENTA),
        ("  ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████║██║     ███████╗╚██████╔╝██║   ██║   ", Colors.BRIGHT_RED),
        ("  ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ", Colors.BRIGHT_GREEN),
    ],
    "matrix": [
        ("  ▄▄    ▄ ▄▄▄▄▄ ▄▄▄▄  ▄▄▄▄▄   ▄▄   ▄▄ ▄▄▄▄", Colors.BRIGHT_GREEN),
        ("  ███  ███ █   █ █  █  █   █   ███ ███ █  █", Colors.GREEN),
        ("  █ ████ █ █▄▄▄█ █▄▄█  █▄▄▄█   █ ███ █ █▄▄█", Colors.BRIGHT_GREEN),
        ("  █  ██  █ █   █ █  █  █   █   █  █  █ █  █", Colors.GREEN),
        ("  █      █ █   █ █  █  █   █   █     █ █  █", Colors.BRIGHT_GREEN),
    ],
}


def clear_screen():
    os.system("cls")


def render_banner(theme="neon"):
    """Render theme banner with subtitle."""
    rows = THEME_BANNERS.get(theme, THEME_BANNERS["neon"])
    print("")
    for line, color in rows:
        print(colored(line, color))
    print(colored(separator("═", 96), Colors.BRIGHT_CYAN))
    print(colored("  SMART FACE ATTENDANCE // CYBER CONSOLE // OFFLINE MODE", Colors.BRIGHT_WHITE))
    print(colored("  Powered by E2C TEAM", Colors.BRIGHT_YELLOW))
    print("")


def print_card(title, lines):
    """Print a boxed info card."""
    width = 74
    print(colored("┌" + "─" * width + "┐", Colors.BRIGHT_CYAN))
    print(colored(f"│ {title.ljust(width - 1)}│", Colors.BRIGHT_CYAN))
    print(colored("├" + "─" * width + "┤", Colors.BRIGHT_CYAN))
    for line in lines:
        line_text = str(line)[:width - 2]
        print(colored(f"│ {line_text.ljust(width - 1)}│", Colors.BRIGHT_WHITE))
    print(colored("└" + "─" * width + "┘", Colors.BRIGHT_CYAN))


def boot_sequence(enabled=True):
    """Render a short startup boot sequence."""
    if not enabled:
        return
    stages = [
        "Loading secure modules...",
        "Checking local encrypted storage...",
        "Attaching camera drivers...",
        "Warming recognition engine...",
        "System ready.",
    ]
    for idx, stage in enumerate(stages, 1):
        print(colored(f"[{idx}/5] {stage}", Colors.BRIGHT_GREEN))
        time.sleep(0.15)
