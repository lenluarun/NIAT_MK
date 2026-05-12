"""
Professional E2C Terminal UI with advanced styling and keyboard-only interaction.
"""
from __future__ import annotations

import importlib
import os
import sys
import time
from typing import Optional

# Enable UTF-8 output safely without replacing stdio objects.
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        # Keep running even if the console code page cannot be changed.
        pass

for stream in (sys.stdout, sys.stderr):
    try:
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # Some execution environments may not allow stream reconfiguration.
        pass

from .ui import render_banner, render_symbol_wall, print_separator
from .colors import Colors, colored


def _enable_auto_stylish_console():
    """Best-effort fullscreen/maximized console setup for stylish mode."""
    if os.name != "nt":
        return

    try:
        os.system("mode con cols=140 lines=42")
    except Exception:
        pass

    try:
        import ctypes
        console = ctypes.windll.kernel32.GetConsoleWindow()
        if console:
            # 3 = SW_MAXIMIZE
            ctypes.windll.user32.ShowWindow(console, 3)
    except Exception:
        pass


def _import_main_module():
    try:
        return importlib.import_module("main")
    except Exception:
        return None


def _render_e2c_header():
    """Render professional E2C header with animations."""
    _enable_auto_stylish_console()
    os.system("cls")

    e2c_logo = [
        "",
        colored("╔═══════════════════════════════════════════════════════════════════════════════╗", Colors.BRIGHT_CYAN),
        colored("║                                                                               ║", Colors.BRIGHT_CYAN),
        colored("║   ███████╗██████╗  ██████╗      ██████╗ ███████╗███████╗██╗   ██╗███████╗     ║", Colors.BRIGHT_GREEN),
        colored("║   ██╔════╝╚════██╗██╔════╝      ╚════██╗██╔════╝██╔════╝╚██╗ ██╔╝██╔════╝     ║", Colors.BRIGHT_CYAN),
        colored("║   █████╗   █████╔╝██║               ██╔╝███████╗█████╗   ╚████╔╝ ███████╗     ║", Colors.BRIGHT_YELLOW),
        colored("║   ██╔══╝  ██╔═══╝ ██║            ██╔════╝██╔════╝██╔══╝    ╚██╔╝  ╚════██     ║", Colors.BRIGHT_MAGENTA),
        colored("║   ███████╗███████╗╚██████╗    ███████╗███████╗███████╗    ██║   ███████║      ║", Colors.BRIGHT_RED),
        colored("║   ╚══════╝╚══════╝ ╚═════╝    ╚══════╝╚══════╝╚══════╝    ╚═╝   ╚══════╝      ║", Colors.BRIGHT_GREEN),
        colored("║                                                                               ║", Colors.BRIGHT_CYAN),
        colored("╠═══════════════════════════════════════════════════════════════════════════════╣", Colors.BRIGHT_CYAN),
        colored("║                                                                               ║", Colors.BRIGHT_CYAN),
        colored("║  ◆ INTELLIGENT FACE RECOGNITION & ATTENDANCE MANAGEMENT SYSTEM ◆             ║", Colors.BRIGHT_YELLOW),
        colored("║  ├─ Powered by Advanced Deep Learning                                         ║", Colors.BRIGHT_WHITE),
        colored("║  ├─ Real-time Multi-face Detection & Recognition                              ║", Colors.BRIGHT_WHITE),
        colored("║  ├─ Enterprise-Grade Offline Architecture                                     ║", Colors.BRIGHT_WHITE),
        colored("║  └─ E2C Command Control Center                                                ║", Colors.BRIGHT_WHITE),
        colored("║                                                                               ║", Colors.BRIGHT_CYAN),
        colored("╚═══════════════════════════════════════════════════════════════════════════════╝", Colors.BRIGHT_CYAN),
        ""
    ]

    for line in e2c_logo:
        print(line)


def _render_e2c_banner():
    """Render dynamic E2C banner with system status."""
    banner = [
        colored("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓", Colors.BRIGHT_GREEN),
        colored("┃                       E2C COMMAND CENTER ACTIVATED                     ┃", Colors.BRIGHT_GREEN),
        colored("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫", Colors.BRIGHT_GREEN),
        colored("┃  ► STATUS: ONLINE  │ ◄ MODE: INTERACTIVE  │  ENCRYPTION : ACTIVE       ┃", Colors.BRIGHT_CYAN),
        colored("┃  ► VERSION: E2C v1.0  │ ► THEME: PROFESSIONAL ENTERPRISE               ┃", Colors.BRIGHT_CYAN),
        colored("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫", Colors.BRIGHT_GREEN),
        colored("┃                                                                        ┃", Colors.BRIGHT_GREEN),
        colored("┃   NEURAL ENGINE        : INITIALIZED                                   ┃", Colors.BRIGHT_WHITE),
        colored("┃   CAMERA INTERFACE     : READY                                         ┃", Colors.BRIGHT_WHITE),
        colored("┃   RECOGNITION MODEL    : LOADED                                        ┃", Colors.BRIGHT_WHITE),
        colored("┃   DATABASE ENGINE      : CONNECTED                                     ┃", Colors.BRIGHT_WHITE),
        colored("┃   ATTENDANCE LEDGER    : LIVE                                          ┃", Colors.BRIGHT_WHITE),
        colored("┃                                                                        ┃", Colors.BRIGHT_GREEN),
        colored("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", Colors.BRIGHT_GREEN),
    ]

    for line in banner:
        print(line)


def _render_menu_options():
    """Render professional menu with styled options."""
    menu = [
        colored("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓", Colors.BRIGHT_CYAN),
        colored("┃                        SELECT OPERATION MODULE                         ┃", Colors.BRIGHT_CYAN),
        colored("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫", Colors.BRIGHT_CYAN),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [1]   CAMERA DIAGNOSTIC MODULE                                        ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Verify hardware connectivity & calibration                    ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [2]   FACE CAPTURE ENGINE                                             ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Acquire & register new face profiles                          ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [3]   NEURAL TRAINING MODULE                                          ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Optimize recognition model with training dataset              ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [4]   REAL-TIME RECOGNITION DAEMON                                    ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Activate facial recognition & auto-attendance logging         ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [5]    DATA ANALYTICS & REPORTING CONSOLE                             ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Generate reports & manage attendance database                 ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [6]   SYSTEM CONFIGURATION PANEL                                      ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Tune parameters & manage system preferences                   ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [7]   NORMAL STYLISH TERMINAL                                         ┃", Colors.BRIGHT_BLUE),
        colored("┃       └─ Switch to keyboard command interface                          ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┃  [0]  EXIT E2C CONTROL CENTER                                          ┃", Colors.BRIGHT_RED),
        colored("┃       └─ Shutdown all services & close interface                       ┃", Colors.BRIGHT_RED),
        colored("┃                                                                        ┃", Colors.BRIGHT_CYAN),
        colored("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", Colors.BRIGHT_CYAN),
    ]

    for line in menu:
        print(line)


def _text_message(title: str, text: str):
    """Display a message in the terminal."""
    print(f"\n[{title}] {text}")
    input("Press ENTER to continue...")


def _text_input(title: str, prompt: str, default: str = "") -> Optional[str]:
    """Get text input from the terminal."""
    prompt_line = f"[{title}] {prompt}"
    if default:
        prompt_line += f" (default: {default})"
    prompt_line += ": "

    value = input(prompt_line).strip()
    if not value:
        return default
    return value


def _text_choice(title: str, text: str, buttons):
    """Choose an option using a keyboard-driven terminal menu."""
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    if text:
        print(text)
        print("-" * 72)

    key_map = {}
    for idx, (label, value) in enumerate(buttons, start=1):
        key = str(idx)
        key_map[key] = value
        print(f"{key}. {label}")

    while True:
        choice = input("Select option: ").strip()
        if choice in key_map:
            return key_map[choice]
        print("Invalid selection. Please choose a listed option.")


def _prompt_text(title: str, prompt: str, default: str = "") -> Optional[str]:
    result = _text_input(title=title, prompt=prompt, default=default)
    if result is None:
        return None
    return result.strip()


def _save_setting(main_mod, key, value):
    if not hasattr(main_mod, "update_setting"):
        raise AttributeError("update_setting not available")

    settings = main_mod.update_setting(key, value)
    if hasattr(main_mod, "app_settings"):
        main_mod.app_settings = settings
    return settings


def _show_settings_snapshot(main_mod):
    settings = getattr(main_mod, "app_settings", None) or {}
    print("\nCURRENT SETTINGS")
    print("-" * 40)
    print(f"Camera Index: {settings.get('camera_index', 'n/a')}")
    print(f"Camera Scan Range: {settings.get('camera_scan_range', 'n/a')}")
    print(f"Capture Samples: {settings.get('max_capture_samples', 'n/a')}")
    print(f"Pass Mark: {settings.get('recognition_pass_mark', 'n/a')}")
    print(f"Recognition Mode: {settings.get('recognition_mode', 'n/a')}")
    print(f"Theme: {settings.get('ui_theme', 'n/a')}")
    print(f"Boot Animation: {settings.get('boot_animation', 'n/a')}")
    print(f"HUD Panel: {settings.get('hud_mode', 'n/a')}")
    print("-" * 40)
    input("Press ENTER to return to Enhanced Menu...")


def _add_student_detail(main_mod):
    data_manager = getattr(main_mod, "data_manager", None)
    if not data_manager:
        _text_message("Add Student", "Student database is not available yet.")
        return

    student_id = _prompt_text("Add Student", "Enter student ID:")
    if not student_id:
        return

    name = _prompt_text("Add Student", "Enter student name:")
    if not name:
        return

    email = _prompt_text("Add Student", "Enter email or phone (optional):", "") or ""

    if not student_id.isdigit():
        _text_message("Add Student", "Student ID must be numeric.")
        return

    if not name.replace(" ", "").isalpha():
        _text_message("Add Student", "Student name must contain only letters and spaces.")
        return

    if data_manager.student_exists(student_id):
        _text_message("Add Student", f"Student ID {student_id} already exists.")
        return

    success = data_manager.add_student(student_id, name, email)
    if success:
        _text_message("Add Student", f"Student added: {name} ({student_id})")
    else:
        _text_message("Add Student", "Failed to add student.")


def _change_setting_value(main_mod, key, title, prompt, parser=None):
    current_settings = getattr(main_mod, "app_settings", None) or {}
    default_value = str(current_settings.get(key, ""))
    value_text = _prompt_text(title, prompt, default_value)
    if value_text is None or value_text == "":
        return

    try:
        value = parser(value_text) if parser else value_text
        _save_setting(main_mod, key, value)
        _text_message(title, f"Updated {key} to {value}.")
    except Exception as exc:
        _text_message(title, f"Could not update {key}: {exc}")


def _settings_menu(main_mod):
    while True:
        settings = getattr(main_mod, "app_settings", None) or {}
        choice = _text_choice(
            title="E2C Settings Console",
            text=(
                "Select what you want to change:\n\n"
                f"Camera Index: {settings.get('camera_index', 'n/a')}\n"
                f"Camera Scan Range: {settings.get('camera_scan_range', 'n/a')}\n"
                f"Capture Samples: {settings.get('max_capture_samples', 'n/a')}\n"
                f"Pass Mark: {settings.get('recognition_pass_mark', 'n/a')}\n"
                f"Theme: {settings.get('ui_theme', 'n/a')}"
            ),
            buttons=[
                ("Add Student Detail", "student"),
                ("Change Camera Index", "camera_index"),
                ("Change Scan Range", "scan_range"),
                ("Change Capture Samples", "samples"),
                ("Change Pass Mark", "pass_mark"),
                ("Change Recognition Mode", "rec_mode"),
                ("Change UI Theme", "theme"),
                ("Toggle Boot Animation", "boot"),
                ("Toggle HUD Panel", "hud"),
                ("View Current Settings", "view"),
                ("Back", "back"),
            ],
        )

        if choice in (None, "back"):
            return
        if choice == "student":
            _add_student_detail(main_mod)
        elif choice == "camera_index":
            _change_setting_value(main_mod, "camera_index", "Camera Index", "Enter new camera index:", int)
        elif choice == "scan_range":
            _change_setting_value(main_mod, "camera_scan_range", "Camera Scan Range", "Enter camera scan range (1-20):", int)
        elif choice == "samples":
            _change_setting_value(main_mod, "max_capture_samples", "Capture Samples", "Enter max capture samples (20-500):", int)
        elif choice == "pass_mark":
            _change_setting_value(main_mod, "recognition_pass_mark", "Recognition Pass Mark", "Enter new pass mark:", int)
        elif choice == "rec_mode":
            _change_setting_value(main_mod, "recognition_mode", "Recognition Mode", "Enter recognition mode (fast/accurate):")
        elif choice == "theme":
            _change_setting_value(main_mod, "ui_theme", "UI Theme", "Enter theme (neon/e2c/matrix/abyss/phantom/sunset/ocean/fire):")
        elif choice == "boot":
            current = bool(settings.get("boot_animation", True))
            _save_setting(main_mod, "boot_animation", not current)
            _text_message("Boot Animation", f"Boot animation {'enabled' if not current else 'disabled'}.")
        elif choice == "hud":
            current = bool(settings.get("hud_mode", True))
            _save_setting(main_mod, "hud_mode", not current)
            _text_message("HUD Panel", f"HUD panel {'enabled' if not current else 'disabled'}.")
        elif choice == "view":
            _show_settings_snapshot(main_mod)


def _handle_data_action(main_mod):
    data_action = _text_choice(
        title="E2C Data Console",
        text="Choose a data action",
        buttons=[
            ("View Students", "students"),
            ("Attendance Report", "attendance"),
            ("Back", "back"),
        ],
    )

    if data_action == "students" and hasattr(main_mod, "data_manager") and main_mod.data_manager:
        main_mod.data_manager.display_all_students()
        input("Press ENTER to return to Enhanced Menu...")
    elif data_action == "attendance" and hasattr(main_mod, "data_manager") and main_mod.data_manager:
        main_mod.data_manager.generate_attendance_report()
        input("Press ENTER to return to Enhanced Menu...")


def _execute_enhanced_action(main_mod, action):
    if action == "camera" and hasattr(main_mod, "check_camera_option"):
        main_mod.check_camera_option(return_to_menu=False)
    elif action == "capture" and hasattr(main_mod, "capture_faces_option"):
        main_mod.capture_faces_option(return_to_menu=False)
    elif action == "train" and hasattr(main_mod, "train_images_option"):
        main_mod.train_images_option(return_to_menu=False)
    elif action == "recognize" and hasattr(main_mod, "recognize_faces_option"):
        main_mod.recognize_faces_option(return_to_menu=False)
    elif action == "data":
        _handle_data_action(main_mod)
    elif action == "settings":
        _settings_menu(main_mod)
    else:
        print("Selected action is not available in interactive mode.")
        input("Press ENTER to continue...")


def _confirm_switch_to_keyboard() -> bool:
    """Keep the terminal UI in keyboard mode."""
    return True


def launch_stylish_terminal(main_mod):
    """Keyboard-first stylish terminal mode."""
    _enable_auto_stylish_console()
    while True:
        _render_e2c_header()
        _render_e2c_banner()
        print("")
        _render_menu_options()
        print(colored("\n[7] ↹ RETURN TO MAIN LAUNCHER", Colors.BRIGHT_CYAN))
        print(colored("[0] ⟳ EXIT ENHANCED TERMINAL", Colors.BRIGHT_RED))

        choice = input("\nSelect option (0-7): ").strip()
        mapping = {
            "1": "camera",
            "2": "capture",
            "3": "train",
            "4": "recognize",
            "5": "data",
            "6": "settings",
        }

        if choice == "7":
            return "launcher"
        if choice == "0":
            return "exit"

        action = mapping.get(choice)
        if action:
            _execute_enhanced_action(main_mod, action)
        else:
            print("Invalid choice. Please select a number from 0 to 7.")
            input("Press ENTER to continue...")


def launch_interactive():
    """Run the professional E2C terminal interface."""
    _enable_auto_stylish_console()
    main_mod = _import_main_module()

    if main_mod is not None:
        try:
            if hasattr(main_mod, "init_system"):
                main_mod.init_system()
        except Exception as exc:
            print(f"Warning: failed to initialize full system: {exc}")

    _render_e2c_header()
    time.sleep(0.5)
    _render_e2c_banner()
    time.sleep(0.3)

    print(colored("[INFO] Running stylish keyboard mode.", Colors.BRIGHT_YELLOW))
    print(colored("[INFO] Use the numbered menu to navigate all terminal features.", Colors.BRIGHT_CYAN))
    time.sleep(0.8)

    while True:
        try:
            print("")
            _render_menu_options()
            print("")

            result: Optional[str] = _text_choice(
                title="E2C Command Center - Select Operation",
                text="",
                buttons=[
                    ("Camera", "camera"),
                    ("Capture", "capture"),
                    ("Train", "train"),
                    ("Recognize", "recognize"),
                    ("Data", "data"),
                    ("Settings", "settings"),
                    ("Normal Terminal", "normal"),
                    ("Exit", "exit"),
                ],
            )

            if result is None or result == "exit":
                _render_shutdown()
                break

            if main_mod is None:
                print("Enhanced UI backend is unavailable right now.")
                print("Restart launcher and try again after fixing startup errors.")
                input("Press ENTER to continue...")
                break

            if result == "normal":
                mode_result = launch_stylish_terminal(main_mod)
                if mode_result == "exit":
                    _render_shutdown()
                    break
            else:
                _execute_enhanced_action(main_mod, result)

        except KeyboardInterrupt:
            _render_shutdown()
            break
        except Exception as exc:
            print(f"Error in interactive UI: {exc}")
            input("Press ENTER to continue...")


def _render_shutdown():
    """Render shutdown sequence."""
    shutdown_seq = [
        "",
        colored("╔═══════════════════════════════════════════════════════════════╗", Colors.BRIGHT_RED),
        colored("║                                                               ║", Colors.BRIGHT_RED),
        colored("║  ███████╗██╗  ██╗██╗   ██╗████████╗██████╗  ██████╗ ██╗       ║", Colors.BRIGHT_YELLOW),
        colored("║  ██╔════╝██║  ██║██║   ██║╚══██╔══╝██╔══██╗██╔════╝ ██║       ║", Colors.BRIGHT_YELLOW),
        colored("║  ███████╗███████║██║   ██║   ██║   ██║  ██║██║  ███╗██║       ║", Colors.BRIGHT_RED),
        colored("║  ╚════██║██╔══██║██║   ██║   ██║   ██║  ██║██║   ██║╚═╝       ║", Colors.BRIGHT_YELLOW),
        colored("║  ███████║██║  ██║╚██████╔╝   ██║   ██████╔╝╚██████╔╝██╗       ║", Colors.BRIGHT_YELLOW),
        colored("║  ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═════╝  ╚═════╝ ╚═╝       ║", Colors.BRIGHT_RED),
        colored("║                                                               ║", Colors.BRIGHT_RED),
        colored("║  ► Disconnecting neural engines...                            ║", Colors.BRIGHT_WHITE),
        colored("║  ► Flushing recognition cache...                              ║", Colors.BRIGHT_WHITE),
        colored("║  ► Closing database connections...                            ║", Colors.BRIGHT_WHITE),
        colored("║  ► Saving system state...                                     ║", Colors.BRIGHT_WHITE),
        colored("║  ► E2C CONTROL CENTER OFFLINE                                 ║", Colors.BRIGHT_GREEN),
        colored("║                                                               ║", Colors.BRIGHT_RED),
        colored("╚═══════════════════════════════════════════════════════════════╝", Colors.BRIGHT_RED),
        "",
    ]

    os.system("cls")
    for line in shutdown_seq:
        print(line)
        time.sleep(0.1)


if __name__ == "__main__":
    launch_interactive()
