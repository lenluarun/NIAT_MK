#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Face Recognition Attendance System - Launcher
Choose between Terminal Interface and Web Interface
"""
import os
import sys
import subprocess
import time

from src.core.updater import update_system_from_github

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the application banner"""
    print("\n" + "="*70)
    print("E2C FACE RECOGNITION & ATTENDANCE SYSTEM")
    print("   Completely Offline | Real-time Processing | High Accuracy")
    print("="*70)

def print_menu():
    """Print the interface selection menu"""
    print("\n" + "-"*50)
    print(">>> SELECT YOUR PREFERRED INTERFACE")
    print("-"*50)
    print("1. [T] Terminal Interface (Console-based)")
    print("   + Classic command-line interface")
    print("   + Direct keyboard interaction")
    print("   + Cyberpunk-style terminal UI")
    print("   + Best for keyboard-focused users")
    print()
    print("2. [W] Web Interface (Browser-based)")
    print("   + Modern graphical user interface")
    print("   + Professional dashboard design")
    print("   + Real-time status updates")
    print("   + Mobile and desktop friendly")
    print()
    print("3. [U] Update System From GitHub")
    print("   + Pull the latest code and refresh dependencies")
    print("   + Best used after committing local changes")
    print()
    print("4. [X] Exit")
    print("-"*50)


def update_system():
    """Update the project from GitHub."""
    print("\n[UPDATE] Checking for updates from GitHub...")
    print("-"*50)
    result = update_system_from_github()

    if result["success"]:
        print("[OK] " + result["message"])
        if result.get("details"):
            print(result["details"])
        print("\n[INFO] Restart the launcher or web server to use the updated code.")
    else:
        print("[ERROR] " + result["message"])
        if result.get("details"):
            print(result["details"])

    input("\nPress ENTER to return to launcher...")

def launch_terminal_interface():
    """Launch the terminal interface"""
    print("\n[START] Launching Terminal Interface (enhanced if available)...")
    print("[INFO] Use mouse or keyboard to interact with enhanced console if supported")
    print("[INFO] Use Ctrl+C to stop any running operation")
    print("\n" + "-"*50)
    try:
        # Try to use the enhanced interactive UI with mouse support
        try:
            from src.utils import interactive_ui
            interactive_ui.launch_interactive()
        except Exception:
            # Fallback to legacy main.py launcher
            subprocess.run([sys.executable, "main.py"], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\n[WARN] Terminal interface interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error launching terminal interface: {e}")
    input("\nPress ENTER to return to launcher...")

def launch_web_interface():
    """Launch the web interface"""
    print("\n[START] Launching Web Interface...")
    print("[INFO] Web server will start on: http://localhost:5000")
    print("[INFO] Open your browser and navigate to the URL above")
    print("[WARN] Press Ctrl+C in this terminal to stop the web server")
    print("\n" + "-"*50)
    print("Starting Flask development server...")
    print("Please wait...\n")

    try:
        # Launch web_app.py
        process = subprocess.Popen([sys.executable, "web_app.py"], cwd=os.path.dirname(__file__))
        print("[OK] Web server started successfully!")
        print("[INFO] Access the interface at: http://localhost:5000")
        print("\n[INFO] The web server is running in the background.")
        print("[INFO] You can now open your browser and use the web interface.")
        print("[INFO] Press Ctrl+C to stop the server and return to this menu.\n")

        try:
            process.wait()  # Wait for the process to finish
        except KeyboardInterrupt:
            print("\n[WARN] Stopping web server...")
            process.terminate()
            process.wait()
            print("[OK] Web server stopped")

    except Exception as e:
        print(f"\n[ERROR] Error launching web interface: {e}")
    input("\nPress ENTER to return to launcher...")

def main():
    """Main launcher function"""
    while True:
        clear_screen()
        print_banner()
        print_menu()

        try:
            choice = input(">>> Enter your choice (1-4): ").strip()

            if choice == "1":
                launch_terminal_interface()
            elif choice == "2":
                launch_web_interface()
            elif choice == "3":
                update_system()
            elif choice == "4":
                print("\n[EXIT] Thank you for using Smart Attendance System!")
                print("[INFO] Powered by E2C TEAM\n")
                sys.exit(0)
            else:
                print("\n[ERROR] Invalid choice! Please enter 1, 2, 3, or 4.")
                input("Press ENTER to continue...")

        except KeyboardInterrupt:
            print("\n\n[WARN] Launcher interrupted by user")
            print("[EXIT] Goodbye!\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            input("Press ENTER to continue...")

if __name__ == "__main__":
    main()