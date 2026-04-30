#!/usr/bin/env python3
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
    print("🤖 SMART FACE RECOGNITION ATTENDANCE SYSTEM")
    print("   Completely Offline | Real-time Processing | High Accuracy")
    print("="*70)

def print_menu():
    """Print the interface selection menu"""
    print("\n" + "─"*50)
    print("🎯 SELECT YOUR PREFERRED INTERFACE")
    print("─"*50)
    print("1. 💻 Terminal Interface (Console-based)")
    print("   • Classic command-line interface")
    print("   • Direct keyboard interaction")
    print("   • Cyberpunk-style terminal UI")
    print("   • Best for keyboard-focused users")
    print()
    print("2. 🌐 Web Interface (Browser-based)")
    print("   • Modern graphical user interface")
    print("   • Professional dashboard design")
    print("   • Real-time status updates")
    print("   • Mobile and desktop friendly")
    print()
    print("3. ⬆️ Update System From GitHub")
    print("   • Pull the latest code and refresh dependencies")
    print("   • Best used after committing local changes")
    print()
    print("4. ❌ Exit")
    print("─"*50)


def update_system():
    """Update the project from GitHub."""
    print("\n⬆️ Checking for updates from GitHub...")
    print("─"*50)
    result = update_system_from_github()

    if result["success"]:
        print("✅ " + result["message"])
        if result.get("details"):
            print(result["details"])
        print("\n💡 Restart the launcher or web server to use the updated code.")
    else:
        print("❌ " + result["message"])
        if result.get("details"):
            print(result["details"])

    input("\nPress ENTER to return to launcher...")

def launch_terminal_interface():
    """Launch the terminal interface"""
    print("\n🚀 Launching Terminal Interface...")
    print("💡 Use Ctrl+C to stop any running operation")
    print("📝 Press ENTER to return to menus after operations")
    print("\n" + "─"*50)
    try:
        # Launch main.py
        subprocess.run([sys.executable, "main.py"], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\n⚠ Terminal interface interrupted by user")
    except Exception as e:
        print(f"\n❌ Error launching terminal interface: {e}")
    input("\nPress ENTER to return to launcher...")

def launch_web_interface():
    """Launch the web interface"""
    print("\n🚀 Launching Web Interface...")
    print("🌐 Web server will start on: http://localhost:5000")
    print("💡 Open your browser and navigate to the URL above")
    print("⚠ Press Ctrl+C in this terminal to stop the web server")
    print("\n" + "─"*50)
    print("Starting Flask development server...")
    print("Please wait...\n")

    try:
        # Launch web_app.py
        process = subprocess.Popen([sys.executable, "web_app.py"], cwd=os.path.dirname(__file__))
        print("✅ Web server started successfully!")
        print("🌐 Access the interface at: http://localhost:5000")
        print("\n💡 The web server is running in the background.")
        print("💡 You can now open your browser and use the web interface.")
        print("💡 Press Ctrl+C to stop the server and return to this menu.\n")

        try:
            process.wait()  # Wait for the process to finish
        except KeyboardInterrupt:
            print("\n⚠ Stopping web server...")
            process.terminate()
            process.wait()
            print("✅ Web server stopped")

    except Exception as e:
        print(f"\n❌ Error launching web interface: {e}")
    input("\nPress ENTER to return to launcher...")

def main():
    """Main launcher function"""
    while True:
        clear_screen()
        print_banner()
        print_menu()

        try:
            choice = input("👆 Enter your choice (1-3): ").strip()

            if choice == "1":
                launch_terminal_interface()
            elif choice == "2":
                launch_web_interface()
            elif choice == "3":
                update_system()
            elif choice == "4":
                print("\n👋 Thank you for using Smart Attendance System!")
                print("🚀 Powered by E2C TEAM\n")
                sys.exit(0)
            else:
                print("\n❌ Invalid choice! Please enter 1, 2, 3, or 4.")
                input("Press ENTER to continue...")

        except KeyboardInterrupt:
            print("\n\n⚠ Launcher interrupted by user")
            print("👋 Goodbye!\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press ENTER to continue...")

if __name__ == "__main__":
    main()