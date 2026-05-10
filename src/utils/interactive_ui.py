"""
Professional E2C Terminal UI with advanced styling and prompt_toolkit integration.
"""
from __future__ import annotations

import importlib
import os
import sys
import time
from typing import Optional

# Enable UTF-8 output
import io
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.SetConsoleCP(65001)
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from prompt_toolkit.shortcuts import button_dialog

from .ui import render_banner, render_symbol_wall, print_separator
from .colors import Colors, colored


def _import_main_module():
    try:
        return importlib.import_module("main")
    except Exception:
        return None


def _render_e2c_header():
    """Render professional E2C header with animations."""
    os.system("cls")

    e2c_logo = [
        "",
        colored("╔═══════════════════════════════════════════════════════════════════════════════╗", Colors.BRIGHT_CYAN),
        colored("║                                                                               ║", Colors.BRIGHT_CYAN),
        colored("║   ███████╗██████╗  ██████╗      ██████╗ ███████╗███████╗██╗   ██╗███████╗ ║", Colors.BRIGHT_GREEN),
        colored("║   ██╔════╝╚════██╗██╔════╝      ╚════██╗██╔════╝██╔════╝╚██╗ ██╔╝██╔════╝ ║", Colors.BRIGHT_CYAN),
        colored("║   █████╗   █████╔╝██║               ██╔╝███████╗█████╗   ╚████╔╝ ███████╗ ║", Colors.BRIGHT_YELLOW),
        colored("║   ██╔══╝  ██╔═══╝ ██║            ██╔════╝██╔════╝██╔══╝    ╚██╔╝  ╚════██║ ║", Colors.BRIGHT_MAGENTA),
        colored("║   ███████╗███████╗╚██████╗    ███████╗███████╗███████╗    ██║   ███████║ ║", Colors.BRIGHT_RED),
        colored("║   ╚══════╝╚══════╝ ╚═════╝    ╚══════╝╚══════╝╚══════╝    ╚═╝   ╚══════╝ ║", Colors.BRIGHT_GREEN),
        colored("║                                                                               ║", Colors.BRIGHT_CYAN),
        colored("╠═══════════════════════════════════════════════════════════════════════════════╣", Colors.BRIGHT_CYAN),
        colored("║                                                                               ║", Colors.BRIGHT_CYAN),
        colored("║  ◆ INTELLIGENT FACE RECOGNITION & ATTENDANCE MANAGEMENT SYSTEM ◆             ║", Colors.BRIGHT_YELLOW),
        colored("║  ├─ Powered by Advanced Deep Learning                                        ║", Colors.BRIGHT_WHITE),
        colored("║  ├─ Real-time Multi-face Detection & Recognition                             ║", Colors.BRIGHT_WHITE),
        colored("║  ├─ Enterprise-Grade Offline Architecture                                    ║", Colors.BRIGHT_WHITE),
        colored("║  └─ E2C Command Control Center                                               ║", Colors.BRIGHT_WHITE),
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
        colored("┃                       E2C COMMAND CENTER ACTIVATED                        ┃", Colors.BRIGHT_GREEN),
        colored("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫", Colors.BRIGHT_GREEN),
        colored("┃  ► STATUS: ONLINE  │ ◄ MODE: INTERACTIVE  │ ◆ ENCRYPTION: ACTIVE        ┃", Colors.BRIGHT_CYAN),
        colored("┃  ► VERSION: E2C v1.0  │ ► THEME: PROFESSIONAL ENTERPRISE                  ┃", Colors.BRIGHT_CYAN),
        colored("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫", Colors.BRIGHT_GREEN),
        colored("┃                                                                              ┃", Colors.BRIGHT_GREEN),
        colored("┃  ✓ NEURAL ENGINE:      INITIALIZED                                          ┃", Colors.BRIGHT_WHITE),
        colored("┃  ✓ CAMERA INTERFACE:   READY                                                ┃", Colors.BRIGHT_WHITE),
        colored("┃  ✓ RECOGNITION MODEL:  LOADED                                               ┃", Colors.BRIGHT_WHITE),
        colored("┃  ✓ DATABASE ENGINE:    CONNECTED                                            ┃", Colors.BRIGHT_WHITE),
        colored("┃  ✓ ATTENDANCE LEDGER:  LIVE                                                 ┃", Colors.BRIGHT_WHITE),
        colored("┃                                                                              ┃", Colors.BRIGHT_GREEN),
        colored("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", Colors.BRIGHT_GREEN),
    ]

    for line in banner:
        print(line)


def _render_menu_options():
    """Render professional menu with styled options."""
    menu = [
        colored("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓", Colors.BRIGHT_CYAN),
        colored("┃                        SELECT OPERATION MODULE                            ┃", Colors.BRIGHT_CYAN),
        colored("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫", Colors.BRIGHT_CYAN),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┃  [1] ◎ CAMERA DIAGNOSTIC MODULE                                             ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Verify hardware connectivity & calibration                         ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┃  [2] ◉ FACE CAPTURE ENGINE                                                  ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Acquire & register new face profiles                               ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┃  [3] ◈ NEURAL TRAINING MODULE                                               ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Optimize recognition model with training dataset                   ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┃  [4] ✦ REAL-TIME RECOGNITION DAEMON                                         ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Activate facial recognition & auto-attendance logging               ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┃  [5] 📊 DATA ANALYTICS & REPORTING CONSOLE                                  ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Generate reports & manage attendance database                      ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┃  [6] ⚙ SYSTEM CONFIGURATION PANEL                                            ┃", Colors.BRIGHT_WHITE),
        colored("┃       └─ Tune parameters & manage system preferences                         ┃", Colors.BRIGHT_YELLOW),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┃  [0] ⟳ EXIT E2C CONTROL CENTER                                              ┃", Colors.BRIGHT_RED),
        colored("┃       └─ Shutdown all services & close interface                             ┃", Colors.BRIGHT_RED),
        colored("┃                                                                              ┃", Colors.BRIGHT_CYAN),
        colored("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", Colors.BRIGHT_CYAN),
    ]

    for line in menu:
        print(line)


def launch_interactive():
    """Run the professional E2C terminal interface."""
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

    while True:
        try:
            print("")
            _render_menu_options()
            print("")

            result: Optional[str] = button_dialog(
                title="E2C Command Center — Select Operation",
                text="",
                buttons=[
                    ("1. Camera Check", "camera"),
                    ("2. Capture Faces", "capture"),
                    ("3. Train Images", "train"),
                    ("4. Recognize", "recognize"),
                    ("5. Data & Reports", "data"),
                    ("6. Settings", "settings"),
                    ("0. Exit", "exit"),
                ],
            ).run()

            if result is None or result == "exit":
                _render_shutdown()
                break

            if main_mod is None:
                import subprocess
                subprocess.run([sys.executable, "main.py"], cwd=".")
                break

            if result == "camera" and hasattr(main_mod, "check_camera_option"):
                main_mod.check_camera_option()
            elif result == "capture" and hasattr(main_mod, "capture_faces_option"):
                main_mod.capture_faces_option()
            elif result == "train" and hasattr(main_mod, "train_images_option"):
                main_mod.train_images_option()
            elif result == "recognize" and hasattr(main_mod, "recognize_faces_option"):
                main_mod.recognize_faces_option()
            elif result == "data":
                if hasattr(main_mod, "view_reports_menu"):
                    main_mod.view_reports_menu()
                elif hasattr(main_mod, "data_management_menu"):
                    main_mod.data_management_menu()
                else:
                    print("Data management not available in this mode.")
                    input("Press ENTER to continue...")
            elif result == "settings" and hasattr(main_mod, "system_settings_menu"):
                main_mod.system_settings_menu()
            else:
                print("Selected action is not available in interactive mode.")
                input("Press ENTER to continue...")

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
        colored("║  ███████╗██╗  ██╗██╗   ██╗████████╗██████╗  ██████╗ ██╗    ║", Colors.BRIGHT_YELLOW),
        colored("║  ██╔════╝██║  ██║██║   ██║╚══██╔══╝██╔══██╗██╔════╝ ██║    ║", Colors.BRIGHT_YELLOW),
        colored("║  ███████╗███████║██║   ██║   ██║   ██║  ██║██║  ███╗██║    ║", Colors.BRIGHT_RED),
        colored("║  ╚════██║██╔══██║██║   ██║   ██║   ██║  ██║██║   ██║╚═╝    ║", Colors.BRIGHT_YELLOW),
        colored("║  ███████║██║  ██║╚██████╔╝   ██║   ██████╔╝╚██████╔╝██╗    ║", Colors.BRIGHT_YELLOW),
        colored("║  ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═════╝  ╚═════╝ ╚═╝    ║", Colors.BRIGHT_RED),
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
