"""
Terminal UI helpers for cinematic cyber-style interface.
"""
import os
import time
from .colors import Colors, colored, separator, get_theme, themed_colored
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from tqdm import tqdm

console = Console()


THEME_BANNERS = {
    "neon": [
        ("  ███╗   ██╗██╗ █████╗ ████████╗    ███╗   ███╗██╗  ██╗", Colors.BRIGHT_CYAN),
        ("  ████╗  ██║██║██╔══██╗╚══██╔══╝    ████╗ ████║██║ ██╔╝", Colors.BRIGHT_MAGENTA),
        ("  ██╔██╗ ██║██║███████║   ██║       ██╔████╔██║█████╔╝ ", Colors.BRIGHT_BLUE),
        ("  ██║╚██╗██║██║██╔══██║   ██║       ██║╚██╔╝██║██╔═██╗ ", Colors.BRIGHT_YELLOW),
        ("  ██║ ╚████║██║██║  ██║   ██║       ██║ ╚═╝ ██║██║  ██╗", Colors.BRIGHT_GREEN),
        ("  ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝", Colors.BRIGHT_CYAN),
    ],
    "e2c": [
        ("  ███████╗██████╗  ██████╗      █████╗ ████████╗████████╗███████╗███╗   ██╗██████╗ ", Colors.BRIGHT_GREEN),
        ("  ██╔════╝╚════██╗██╔════╝     ██╔══██╗╚══██╔══╝╚══██╔══╝██╔════╝████╗  ██║██╔══██╗", Colors.BRIGHT_CYAN),
        ("  █████╗   █████╔╝██║          ███████║   ██║      ██║   █████╗  ██╔██╗ ██║██║  ██║", Colors.BRIGHT_YELLOW),
        ("  ██╔══╝  ██╔═══╝ ██║          ██╔══██║   ██║      ██║   ██╔══╝  ██║╚██╗██║██║  ██║", Colors.BRIGHT_MAGENTA),
        ("  ███████╗███████╗╚██████╗     ██║  ██║   ██║      ██║   ███████╗██║ ╚████║██████╔╝", Colors.BRIGHT_RED),
        ("  ╚══════╝╚══════╝ ╚═════╝     ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═══╝╚═════╝ ", Colors.BRIGHT_GREEN),
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
    "sunset": [
        ("  ███████╗██╗   ██╗███╗   ██╗███████╗███████╗████████╗", Colors.BRIGHT_YELLOW),
        ("  ██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝╚══██╔══╝", Colors.BRIGHT_RED),
        ("  ███████╗██║   ██║██╔██╗ ██║███████╗█████╗     ██║   ", Colors.BRIGHT_MAGENTA),
        ("  ╚════██║██║   ██║██║╚██╗██║╚════██║██╔══╝     ██║   ", Colors.BRIGHT_YELLOW),
        ("  ███████║╚██████╔╝██║ ╚████║███████║███████╗   ██║   ", Colors.BRIGHT_RED),
        ("  ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝   ", Colors.BRIGHT_MAGENTA),
    ],
    "ocean": [
        ("   ██████╗  ██████╗███████╗ █████╗ ███╗   ██╗", Colors.BRIGHT_CYAN),
        ("  ██╔═══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║", Colors.BRIGHT_BLUE),
        ("  ██║   ██║██║     █████╗  ███████║██╔██╗ ██║", Colors.BRIGHT_MAGENTA),
        ("  ██║   ██║██║     ██╔══╝  ██╔══██║██║╚██╗██║", Colors.BRIGHT_CYAN),
        ("  ╚██████╔╝╚██████╗███████╗██║  ██║██║ ╚████║", Colors.BRIGHT_BLUE),
        ("   ╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝", Colors.BRIGHT_MAGENTA),
    ],
    "fire": [
        ("  ███████╗██╗██████╗ ███████╗", Colors.BRIGHT_RED),
        ("  ██╔════╝██║██╔══██╗██╔════╝", Colors.BRIGHT_YELLOW),
        ("  █████╗  ██║██████╔╝█████╗  ", Colors.BRIGHT_MAGENTA),
        ("  ██╔══╝  ██║██╔══██╗██╔══╝  ", Colors.BRIGHT_RED),
        ("  ██║     ██║██║  ██║███████╗", Colors.BRIGHT_YELLOW),
        ("  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝", Colors.BRIGHT_MAGENTA),
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
        "e2c": [
            "  ╔═══════════════════[ E2C ATTENDANCE CONTROL GRID ]══════════════════╗",
            "  ║  ◉ FACE FEEDS     ▣ CAMERA STREAMS   ✦ ATTENDANCE INTELLIGENCE     ║",
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
        "sunset": [
            "  ┌───────────────────────[ SUNSET HORIZON ]───────────────────────┐",
            "  │  🌅 SUNRISE PROTOCOL   |   🔥 FACE DETECTION   |   🌇 ATTENDANCE  │",
            "  │  ████████              |   ██████████████     |   ██████████████  │",
            "  │  ▓▓▓▓▓▓▓▓              |   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒     |   ░░░░░░░░░░░░░░  │",
            "  └───────────────────────────────────────────────────────────────────┘",
        ],
        "ocean": [
            "  ╭───────────────────────[ OCEAN DEPTHS ]───────────────────────╮",
            "  │  🌊 WAVE ANALYSIS      |   🐟 FACE RECOGNITION |   🐳 ATTENDANCE  │",
            "  │  ~~~~~~~~              |   ███████████████    |   ██████████████ │",
            "  │  ░░░░░░░░              |   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒    |   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │",
            "  ╰─────────────────────────────────────────────────────────────────╯",
        ],
        "fire": [
            "  ┏━━━━━━━━━━━━━━━━━━━━━━━[ FIRESTORM CORE ]━━━━━━━━━━━━━━━━━━━━━━━┓",
            "  ┃   🔥 FLAME DETECTOR     |   💥 FACE IGNITION    |   🌋 ATTENDANCE ┃",
            "  ┃  ██████████████         |   ████████████████   |   ██████████████ ┃",
            "  ┃  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒         |   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   |   ░░░░░░░░░░░░░░ ┃",
            "  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛",
        ],
    }
    for line in art_by_theme.get(theme, art_by_theme["neon"]):
        print(themed_colored(line, "primary", theme))
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
        print(themed_colored(f"[{idx}/5] {stage}", "success"))
        time.sleep(0.15)


def show_spinner(message, duration=2, theme="neon"):
    """Show an animated spinner for a task."""
    theme_colors = get_theme(theme)
    with console.status(f"[{theme_colors['primary']}] {message}", spinner="dots"):
        time.sleep(duration)


def show_progress_bar(total, description="Processing", theme="neon"):
    """Show a progress bar for a task."""
    theme_colors = get_theme(theme)
    # Convert ANSI colors to Rich colors
    rich_colors = {
        "neon": {"complete": "bright_cyan", "finished": "bright_green"},
        "matrix": {"complete": "green", "finished": "bright_green"},
        "abyss": {"complete": "bright_blue", "finished": "bright_cyan"},
        "phantom": {"complete": "bright_red", "finished": "bright_magenta"},
        "sunset": {"complete": "bright_yellow", "finished": "bright_red"},
        "ocean": {"complete": "bright_cyan", "finished": "bright_blue"},
        "fire": {"complete": "bright_red", "finished": "bright_yellow"},
        "e2c": {"complete": "bright_green", "finished": "bright_cyan"},
    }
    colors = rich_colors.get(theme, rich_colors["neon"])
    
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[{colors['complete']}]{description}"),
        BarColumn(complete_style=colors['complete'], finished_style=colors['finished']),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(description, total=total)
        for i in range(total):
            time.sleep(0.1)  # Simulate work
            progress.update(task, advance=1)


def show_tqdm_progress(total, description="Processing"):
    """Show a tqdm progress bar."""
    for i in tqdm(range(total), desc=description, unit="item", ncols=80, colour="green"):
        time.sleep(0.05)  # Simulate work


def print_separator(char="═", length=60, theme="neon"):
    """Print a themed separator line with Unicode symbols."""
    theme_colors = get_theme(theme)
    symbols = {
        "neon": "✦",
        "matrix": "█",
        "abyss": "◍",
        "phantom": "▲",
        "sunset": "🌅",
        "ocean": "🌊",
        "fire": "🔥",
        "e2c": "◉",
    }
    symbol = symbols.get(theme, "✦")
    sep = f"{symbol} {char * (length - 4)} {symbol}"
    print(themed_colored(sep, "highlight", theme))


def print_menu_item(number, text, theme="neon"):
    """Print a menu item with Unicode symbols."""
    print(themed_colored(f"[{number}] {text}", "info", theme))


def print_status_box(title, items, theme="neon"):
    """Print a status box with Unicode borders."""
    theme_colors = get_theme(theme)
    width = 60
    borders = {
        "neon": ("╔", "╗", "╚", "╝", "║", "═"),
        "matrix": ("┌", "┐", "└", "┘", "│", "─"),
        "abyss": ("╓", "╖", "╙", "╜", "║", "─"),
        "phantom": ("┏", "┓", "┗", "┛", "┃", "━"),
        "sunset": ("╔", "╗", "╚", "╝", "║", "═"),
        "ocean": ("╭", "╮", "╰", "╯", "│", "─"),
        "fire": ("┏", "┓", "┗", "┛", "┃", "━"),
        "e2c": ("╔", "╗", "╚", "╝", "║", "═"),
    }
    tl, tr, bl, br, vert, horiz = borders.get(theme, borders["neon"])
    
    print(themed_colored(f"{tl}{horiz * width}{tr}", "primary", theme))
    print(themed_colored(f"{vert} {title.center(width - 2)} {vert}", "primary", theme))
    print(themed_colored(f"{tl}{horiz * width}{tr}", "primary", theme))
    for item in items:
        print(themed_colored(f"{vert} {str(item).ljust(width - 2)} {vert}", "info", theme))
    print(themed_colored(f"{bl}{horiz * width}{br}", "primary", theme))


def print_section_header(title, theme="neon", width=72):
    """Print an enhanced section header with decorative elements."""
    theme_colors = get_theme(theme)
    print(colored("", Colors.RESET))
    print(themed_colored(f"  ▸ {title.upper()} " + "─" * (width - len(title) - 6), "highlight", theme))
    print(colored("", Colors.RESET))


def print_table_header(headers, widths=None, theme="neon"):
    """Print a formatted table header."""
    if widths is None:
        widths = [20] * len(headers)
    header_str = " │ ".join(h.ljust(w)[:w] for h, w in zip(headers, widths))
    print(themed_colored(f"  {header_str}", "primary", theme))
    divider = " ─ ".join("─" * w for w in widths)
    print(themed_colored(f"  {divider}", "highlight", theme))


def print_loading_animation(duration=1, theme="neon"):
    """Print an animated loading sequence."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_time = time.time()
    idx = 0
    while time.time() - start_time < duration:
        print(themed_colored(f"  {frames[idx % len(frames)]} Processing...", "success", theme), end="\r")
        time.sleep(0.1)
        idx += 1
    print(" " * 40, end="\r")  # Clear the line


def print_success_message(message, theme="neon"):
    """Print a success message with styling."""
    print(themed_colored(f"  ✓ {message}", "success", theme))


def print_warning_message(message, theme="neon"):
    """Print a warning message with styling."""
    print(themed_colored(f"  ⚠ {message}", "warning", theme))


def print_error_message(message, theme="neon"):
    """Print an error message with styling."""
    print(themed_colored(f"  ✗ {message}", "danger", theme))


def print_info_message(message, theme="neon"):
    """Print an info message with styling."""
    print(themed_colored(f"  ℹ {message}", "info", theme))
