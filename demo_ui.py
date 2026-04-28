#!/usr/bin/env python3
"""
Demo script for the enhanced terminal UI features.
"""
import sys
import os

# Add Code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Code'))

from colors import get_theme, themed_colored
from ui_console import (
    render_banner, render_symbol_wall, show_spinner,
    show_progress_bar, show_tqdm_progress, print_separator,
    print_menu_item, print_status_box, clear_screen
)

def demo_themes():
    """Demo all available themes."""
    themes = ["neon", "e2c", "matrix", "abyss", "phantom", "sunset", "ocean", "fire"]
    for theme in themes:
        clear_screen()
        print(f"\n🎨 Theme: {theme.upper()}")
        render_banner(theme)
        render_symbol_wall(theme)
        print_separator("═", 60, theme)
        print(themed_colored("✓ This is a success message", "success", theme))
        print(themed_colored("ℹ This is an info message", "info", theme))
        print(themed_colored("⚠ This is a warning message", "warning", theme))
        print(themed_colored("✗ This is an error message", "error", theme))
        input("\nPress ENTER for next theme...")

def demo_ui_elements():
    """Demo UI elements."""
    clear_screen()
    print("\n🔧 UI Elements Demo")
    print_separator("═", 60, "neon")

    # Menu items
    print_menu_item("1", "Camera Check", "neon")
    print_menu_item("2", "Capture Faces", "neon")
    print_menu_item("3", "Train Images", "neon")

    print_separator("─", 60, "neon")

    # Status box
    print_status_box(
        "SYSTEM STATUS",
        [
            "✓ Camera: Connected",
            "✓ Storage: Ready",
            "✓ Models: Loaded",
            "⚠ Recognition: Limited"
        ],
        "neon"
    )

def demo_progress():
    """Demo progress bars and spinners."""
    clear_screen()
    print("\n⏳ Progress Demo")
    print_separator("═", 60, "neon")

    print("🔄 Spinner Demo:")
    show_spinner("Processing data...", 2, "neon")

    print("\n📊 Progress Bar Demo:")
    show_progress_bar(20, "Training model", "neon")

    print("\n📈 TQDM Progress Demo:")
    show_tqdm_progress(50, "Processing images")

if __name__ == "__main__":
    print("🎭 Enhanced Terminal UI Demo")
    print("Choose demo:")
    print("1. Theme Showcase")
    print("2. UI Elements")
    print("3. Progress Indicators")
    print("4. All Demos")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
        demo_themes()
    elif choice == "2":
        demo_ui_elements()
    elif choice == "3":
        demo_progress()
    elif choice == "4":
        demo_themes()
        demo_ui_elements()
        demo_progress()
    else:
        print("Invalid choice")

    print("\n✨ Demo complete!")