"""
Smart Face Recognition Attendance System - Launcher
Completely Offline | E2C TEAM
"""
import os
import sys

# Add Code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Code'))

import check_camera
import capture_image
import train_image
import recognize
from colors import (Colors, bold, colored, success, error, warning, info, 
                   highlight, separator)
from storage_manager import get_storage_path, create_storage_folders
from data_manager import DataManager

# Global variables
storage_path = None
storage_paths = None
data_manager = None


def init_system():
    """Initialize the system and set up storage"""
    global storage_path, storage_paths, data_manager
    
    os.system('cls')
    print("\n")
    print(highlight("╔" + "═" * 68 + "╗"))
    print(highlight("║" + " " * 10 + "INITIALIZING SMART ATTENDANCE SYSTEM" + " " * 23 + "║"))
    print(highlight("╚" + "═" * 68 + "╝"))
    
    print(f"\n{info('⏳')} Setting up offline storage...")
    storage_path = get_storage_path()
    
    if not storage_path:
        print(error("✗ Failed to initialize storage!"))
        sys.exit(1)
    
    print(f"{info('⏳')} Creating storage folders...")
    storage_paths = create_storage_folders(storage_path)
    
    print(f"{info('⏳')} Initializing data manager...")
    data_manager = DataManager(storage_paths)
    
    print(f"{success('✓')} System initialized successfully!")
    print(f"{success('✓')} Storage Location: {bold(storage_path)}\n")
    input("Press ENTER to continue...")


def title_bar():
    """Display the main title bar"""
    os.system('cls')
    print("\n")
    print(colored(highlight("╔" + "═" * 68 + "╗"), Colors.BRIGHT_CYAN))
    print(colored(highlight("║     SMART FACE RECOGNITION ATTENDANCE SYSTEM              ║"), Colors.BRIGHT_CYAN))
    print(colored(highlight("║                  Powered by E2C TEAM                      ║"), Colors.BRIGHT_CYAN))
    print(colored(highlight("║              ✓ COMPLETELY OFFLINE SYSTEM ✓                ║"), Colors.BRIGHT_CYAN))
    print(colored(highlight("╚" + "═" * 68 + "╝"), Colors.BRIGHT_CYAN))
    print("\n")


def main_menu():
    """Display main menu with all options"""
    title_bar()
    
    print(colored(separator("─", 60), Colors.BRIGHT_YELLOW))
    print(highlight("┌" + "─" * 58 + "┐"))
    print(highlight("│" + " " * 20 + bold("MAIN MENU") + " " * 29 + "│"))
    print(highlight("└" + "─" * 58 + "┘"))
    
    print(f"\n{colored('[1]', Colors.BRIGHT_CYAN)} {bold('► Camera Check')}")
    print(f"{colored('[2]', Colors.BRIGHT_CYAN)} {bold('► Capture Faces')}")
    print(f"{colored('[3]', Colors.BRIGHT_CYAN)} {bold('► Train Images')}")
    print(f"{colored('[4]', Colors.BRIGHT_CYAN)} {bold('► Recognize & Attendance')}")
    print(f"{colored('[5]', Colors.BRIGHT_CYAN)} {bold('► Data Management')}")
    print(f"{colored('[6]', Colors.BRIGHT_CYAN)} {bold('► View Reports')}")
    print(f"{colored('[7]', Colors.BRIGHT_CYAN)} {bold('► System Settings')}")
    print(f"{colored('[8]', Colors.BRIGHT_CYAN)} {bold('► Exit')}\n")
    
    print(colored(separator("─", 60), Colors.BRIGHT_YELLOW))
    
    while True:
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-8): "))
            if choice == 1:
                check_camera_option()
                break
            elif choice == 2:
                capture_faces_option()
                break
            elif choice == 3:
                train_images_option()
                break
            elif choice == 4:
                recognize_faces_option()
                break
            elif choice == 5:
                data_management_menu()
                break
            elif choice == 6:
                view_reports_menu()
                break
            elif choice == 7:
                system_settings_menu()
                break
            elif choice == 8:
                print(f"\n{success('✓')} Thank you for using Smart Attendance System!")
                print(f"{info('═')} Powered by E2C TEAM {info('═')}\n")
                sys.exit(0)
            else:
                print(error("⚠ Invalid Choice! Please enter 1-8."))
                main_menu()
        except ValueError:
            print(error("⚠ Invalid Input! Please enter a number between 1-8."))
            main_menu()


def check_camera_option():
    """Check camera option"""
    check_camera.camer()
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def capture_faces_option():
    """Capture faces option"""
    capture_image.takeImages(storage_paths, data_manager)
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def train_images_option():
    """Train images option"""
    train_image.TrainImages(storage_paths)
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def recognize_faces_option():
    """Recognize faces option"""
    recognize.recognize_attendence(storage_paths, data_manager)
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def data_management_menu():
    """Data management menu"""
    while True:
        os.system('cls')
        print("\n")
        print(highlight("╔" + "═" * 68 + "╗"))
        print(highlight("║" + " " * 18 + "DATA MANAGEMENT OPTIONS" + " " * 27 + "║"))
        print(highlight("╚" + "═" * 68 + "╝"))
        
        print(f"\n{colored('[1]', Colors.BRIGHT_GREEN)} {bold('► View All Students')}")
        print(f"{colored('[2]', Colors.BRIGHT_GREEN)} {bold('► Add Single Student')}")
        print(f"{colored('[3]', Colors.BRIGHT_GREEN)} {bold('► Add Multiple Students (Bulk)')}")
        print(f"{colored('[4]', Colors.BRIGHT_GREEN)} {bold('► Delete Student')}")
        print(f"{colored('[5]', Colors.BRIGHT_GREEN)} {bold('► Back to Main Menu')}\n")
        
        print(colored(separator("─", 60), Colors.BRIGHT_YELLOW))
        
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-5): "))
            if choice == 1:
                data_manager.display_all_students()
                input("Press ENTER to continue...")
            elif choice == 2:
                data_manager.add_single_student_interactive()
                input("Press ENTER to continue...")
            elif choice == 3:
                data_manager.add_bulk_students_interactive()
                input("Press ENTER to continue...")
            elif choice == 4:
                try:
                    student_id = input(f"\n{info('➤')} Enter Student ID to delete: ")
                    if data_manager.delete_student(student_id):
                        print(success(f"✓ Student {student_id} deleted successfully!"))
                    else:
                        print(error(f"✗ Failed to delete student {student_id}!"))
                    input("Press ENTER to continue...")
                except Exception as e:
                    print(error(f"✗ Error: {e}"))
                    input("Press ENTER to continue...")
            elif choice == 5:
                main_menu()
                break
            else:
                print(error("⚠ Invalid Choice!"))
        except ValueError:
            print(error("⚠ Invalid Input!"))


def view_reports_menu():
    """View reports menu"""
    while True:
        os.system('cls')
        print("\n")
        print(highlight("╔" + "═" * 68 + "╗"))
        print(highlight("║" + " " * 23 + "VIEW REPORTS" + " " * 33 + "║"))
        print(highlight("╚" + "═" * 68 + "╝"))
        
        print(f"\n{colored('[1]', Colors.BRIGHT_MAGENTA)} {bold('► Attendance Report')}")
        print(f"{colored('[2]', Colors.BRIGHT_MAGENTA)} {bold('► Student Database Report')}")
        print(f"{colored('[3]', Colors.BRIGHT_MAGENTA)} {bold('► Back to Main Menu')}\n")
        
        print(colored(separator("─", 60), Colors.BRIGHT_YELLOW))
        
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-3): "))
            if choice == 1:
                data_manager.generate_attendance_report()
                input("Press ENTER to continue...")
            elif choice == 2:
                data_manager.display_all_students()
                input("Press ENTER to continue...")
            elif choice == 3:
                main_menu()
                break
            else:
                print(error("⚠ Invalid Choice!"))
        except ValueError:
            print(error("⚠ Invalid Input!"))


def system_settings_menu():
    """System settings menu"""
    while True:
        os.system('cls')
        print("\n")
        print(highlight("╔" + "═" * 68 + "╗"))
        print(highlight("║" + " " * 22 + "SYSTEM SETTINGS" + " " * 31 + "║"))
        print(highlight("╚" + "═" * 68 + "╝"))
        
        print(f"\n{colored('[1]', Colors.BRIGHT_BLUE)} {bold('► Change Storage Location')}")
        print(f"{colored('[2]', Colors.BRIGHT_BLUE)} {bold('► View System Info')}")
        print(f"{colored('[3]', Colors.BRIGHT_BLUE)} {bold('► Back to Main Menu')}\n")
        
        print(colored(separator("─", 60), Colors.BRIGHT_YELLOW))
        
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-3): "))
            if choice == 1:
                print(f"\n{warning('⚠')} Changing storage location...")
                input("Press ENTER to continue...")
                init_system()
            elif choice == 2:
                os.system('cls')
                print("\n")
                print(highlight("╔" + "═" * 68 + "╗"))
                print(highlight("║" + " " * 22 + "SYSTEM INFORMATION" + " " * 29 + "║"))
                print(highlight("╚" + "═" * 68 + "╝"))
                print(f"\n{bold('System Name:')} Smart Face Recognition Attendance System")
                print(f"{bold('Status:')} {success('✓ ONLINE')}")
                print(f"{bold('Mode:')} {info('COMPLETELY OFFLINE')}")
                print(f"{bold('Storage Type:')} {success('Local Storage')}")
                print(f"{bold('Storage Path:')} {colored(storage_path, Colors.BRIGHT_CYAN)}")
                print(f"{bold('Team:')} {highlight('E2C TEAM')}")
                print(f"{bold('Version:')} 2.0 (Enhanced)\n")
                input("Press ENTER to continue...")
            elif choice == 3:
                main_menu()
                break
            else:
                print(error("⚠ Invalid Choice!"))
        except ValueError:
            print(error("⚠ Invalid Input!"))


if __name__ == "__main__":
    try:
        init_system()
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{warning('⚠')} System interrupted by user.")
        print(f"{info('═')} Powered by E2C TEAM {info('═')}\n")
        sys.exit(0)
    except Exception as e:
        print(error(f"\n✗ An error occurred: {e}"))
        print(f"{info('═')} Powered by E2C TEAM {info('═')}\n")
        sys.exit(1)
