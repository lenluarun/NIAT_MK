"""
Terminal UI helpers for cinematic cyber-style interface.
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
    "abyss": [
        ("   ▄▄▄       ▄▄▄▄   ▄██   ▄      ▄▄▄▄▄▄▄▄▄▄▄      ▄▄      ▄▄ ▄▄   ▄▄", Colors.BRIGHT_BLUE),
        ("  █   █     ██  ██ ██ ██ ██     ██  ██  ██  ██    █  █    █  █  █ █  █", Colors.BRIGHT_CYAN),
        ("  █▄▄▄█     ██  ██ ██▄██ ██     ██  ██  ██  ██    █▄▄█    █  █   █   █", Colors.BRIGHT_MAGENTA),
        ("  █   █     ██  ██ ██ ▀█ ██     ██  ██  ██  ██    █  █    █  █       █", Colors.BRIGHT_BLUE),
        ("  █   █      ▀▀▀▀  ██  █ █▄▄▄▄▄ ██      ██  ██    █  █    █▄▄█       █", Colors.BRIGHT_CYAN),
    ],
    "phantom": [
        ("  ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗", Colors.BRIGHT_RED),
        ("  ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║", Colors.BRIGHT_MAGENTA),
        ("  ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║", Colors.BRIGHT_YELLOW),
        ("  ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║", Colors.BRIGHT_CYAN),
        ("  ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║", Colors.BRIGHT_GREEN),
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


def render_symbol_wall(theme="neon"):
    """Render symbol-based 'image' wall below banner."""
    art_by_theme = {
        "metasploit": [
            "  ╔═══════════════════════[ RED-OPS GRID ]═══════════════════════╗",
            "  ║  ◉ TARGET FEEDS   ▣ CAMERA STREAMS   ✦ MODEL INTELLIGENCE    ║",
            "  ║  ░▒▓████▓▒░       ╔═╗╔═╗╔╦╗         █▀█ █ █ █▀▀ █▀█         ║",
            "  ║  ░▒▓████▓▒░       ║  ╠═╣║║║         █▀▀ █▀█ █▀  █▄█         ║",
            "  ║  ░▒▓████▓▒░       ╚═╝╩ ╩╩ ╩         ▀   ▀ ▀ ▀▀▀ ▀ ▀         ║",
            "  ╚═══════════════════════════════════════════════════════════════╝",
        ],
        "matrix": [
            "  ┌────────────────────[ MATRIX SENSOR ARRAY ]────────────────────┐",
            "  │  0101 11 0001 1110    [◉] HUMAN FACE SIGNAL LOCKED            │",
            "  │  ████▒▒██  ██▒▒██     [▣] CAMERA NODE STREAMING               │",
            "  │  0011 01 1110 1001    [✦] ATTENDANCE LEDGER LIVE              │",
            "  └────────────────────────────────────────────────────────────────┘",
        ],
        "phantom": [
            "  ┏━━━━━━━━━━━━━━━━━━━━━━[ PHANTOM VAULT ]━━━━━━━━━━━━━━━━━━━━━━┓",
            "  ┃   ▲ NIGHT VISION CORE      ◆ ID SIGNATURE ANALYTICS         ┃",
            "  ┃  ╱█╲   ╱█╲   ╱█╲            ● CAMERA PATH AUTO-ROUTING       ┃",
            "  ┃  ╲█╱   ╲█╱   ╲█╱            ■ PREDICTION FILTER 4D           ┃",
            "  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛",
        ],
        "abyss": [
            "  ╓───────────────────────[ ABYSS DEPTH VIEW ]──────────────────────╖",
            "  ║   ~~~~~~      ~~~~~~      ~~~~~~      ~~~~~~      ~~~~~~        ║",
            "  ║   ◍◍◍◍◍      ◍◍◍◍◍      ◍◍◍◍◍      ◍◍◍◍◍      ◍◍◍◍◍         ║",
            "  ║   CAMERA NODES TRACK: [ FACE ] [ MOTION ] [ LUMINANCE ]         ║",
            "  ╙───────────────────────────────────────────────────────────────────╜",
        ],
        "neon": [
            "  ╭───────────────────────[ NEON COMMAND GLASS ]──────────────────────╮",
            "  │  ✶ ✷ ✸  LIVE HUD   |   ◉ FACE LOCK   |   ▣ CAMERA BUS   |   ✦ AI  │",
            "  │  ▄▄▄ ▄▄▄ ▄▄▄        |   ▒▒▒▒▒▒▒▒▒▒   |   ████████████             │",
            "  │  ▀▀▀ ▀▀▀ ▀▀▀        |   ░░░░░░░░░░   |   ▓▓▓▓▓▓▓▓▓▓▓▓             │",
            "  ╰─────────────────────────────────────────────────────────────────────╯",
        ],
    }
    for line in art_by_theme.get(theme, art_by_theme["neon"]):
        print(colored(line, Colors.BRIGHT_CYAN))
    print("")


def render_hud_status(title, stats):
    """Print compact HUD status bar."""
    print(colored(f"╔══ {title} " + "═" * 60, Colors.BRIGHT_YELLOW))
    pairs = [f"{key}: {value}" for key, value in stats]
    print(colored("║ " + "  |  ".join(pairs), Colors.BRIGHT_WHITE))
    print(colored("╚" + "═" * 74, Colors.BRIGHT_YELLOW))
    print("")


def print_menu_block(title, items, accent=Colors.BRIGHT_CYAN):
    """Print a stylish numbered menu block."""
    print(colored("┏" + "━" * 72 + "┓", accent))
    print(colored(f"┃ {title.ljust(70)} ┃", accent))
    print(colored("┣" + "━" * 72 + "┫", accent))
    for key, label in items:
        entry = f"[{key}]  {label}"
        print(colored(f"┃ {entry.ljust(70)} ┃", Colors.BRIGHT_WHITE))
    print(colored("┗" + "━" * 72 + "┛", accent))


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
