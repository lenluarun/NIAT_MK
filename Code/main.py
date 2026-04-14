"""
Smart Face Recognition Attendance System - Main Module
Completely Offline | E2C TEAM
"""
import os
import sys
import check_camera
import capture_image
import train_image
import recognize
from camera_utils import detect_available_cameras
from ui_console import render_banner, clear_screen, print_card, boot_sequence
from colors import (Colors, bold, colored, success, error, warning, info, 
                   highlight, separator)
from storage_manager import get_storage_path, create_storage_folders
from data_manager import DataManager
from settings_manager import load_settings, update_setting

# Global variables
storage_path = None
storage_paths = None
data_manager = None
app_settings = None


def init_system():
    """Initialize the system and set up storage"""
    global storage_path, storage_paths, data_manager, app_settings
    
    clear_screen()
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
    app_settings = load_settings()
    boot_sequence(app_settings.get("boot_animation", True))
    
    print(f"{success('✓')} System initialized successfully!")
    print(f"{success('✓')} Storage Location: {bold(storage_path)}")
    print(f"{success('✓')} Active Camera Index: {bold(str(app_settings['camera_index']))}\n")
    input("Press ENTER to continue...")


def title_bar():
    """Display the main title bar"""
    clear_screen()
    render_banner(app_settings.get("ui_theme", "neon"))


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
    print(f"{colored('[5]', Colors.BRIGHT_CYAN)} {bold('► Camera Studio (Scan/Select)')}")
    print(f"{colored('[6]', Colors.BRIGHT_CYAN)} {bold('► Project Dashboard')}")
    print(f"{colored('[7]', Colors.BRIGHT_CYAN)} {bold('► Data Management')}")
    print(f"{colored('[8]', Colors.BRIGHT_CYAN)} {bold('► View Reports')}")
    print(f"{colored('[9]', Colors.BRIGHT_CYAN)} {bold('► System Settings')}")
    print(f"{colored('[10]', Colors.BRIGHT_CYAN)} {bold('► Quick Pipeline (Capture > Train > Recognize)')}")
    print(f"{colored('[11]', Colors.BRIGHT_CYAN)} {bold('► Exit')}\n")
    print(f"{info('📷')} Active Camera: {bold(str(app_settings['camera_index']))}  |  {info('🎯')} Capture Samples: {bold(str(app_settings['max_capture_samples']))}")
    
    print(colored(separator("─", 60), Colors.BRIGHT_YELLOW))
    
    while True:
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-11): "))
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
                camera_studio_menu()
                break
            elif choice == 6:
                project_dashboard()
                break
            elif choice == 7:
                data_management_menu()
                break
            elif choice == 8:
                view_reports_menu()
                break
            elif choice == 9:
                system_settings_menu()
                break
            elif choice == 10:
                quick_pipeline()
                break
            elif choice == 11:
                print(f"\n{success('✓')} Thank you for using Smart Attendance System!")
                print(f"{info('═')} Powered by E2C TEAM {info('═')}\n")
                sys.exit(0)
            else:
                print(error("⚠ Invalid Choice! Please enter 1-11."))
                main_menu()
        except ValueError:
            print(error("⚠ Invalid Input! Please enter a number between 1-11."))
            main_menu()


def check_camera_option():
    """Check camera option"""
    check_camera.camer(app_settings['camera_index'])
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def capture_faces_option():
    """Capture faces option"""
    capture_image.takeImages(
        storage_paths,
        data_manager,
        camera_index=app_settings['camera_index'],
        max_samples=app_settings['max_capture_samples']
    )
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def train_images_option():
    """Train images option"""
    train_image.TrainImages(storage_paths)
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def recognize_faces_option():
    """Recognize faces option"""
    recognize.recognize_attendence(
        storage_paths,
        data_manager,
        camera_index=app_settings['camera_index'],
        pass_mark=app_settings['recognition_pass_mark']
    )
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def camera_studio_menu():
    """Camera utility and selection menu."""
    global app_settings
    while True:
        os.system('cls')
        print("\n")
        print(highlight("╔" + "═" * 68 + "╗"))
        print(highlight("║" + " " * 23 + "CAMERA STUDIO" + " " * 32 + "║"))
        print(highlight("╚" + "═" * 68 + "╝"))
        print(f"\n{info('📷')} Active Camera Index: {bold(str(app_settings['camera_index']))}")
        print(f"{colored('[1]', Colors.BRIGHT_GREEN)} {bold('► Scan Available Cameras')}")
        print(f"{colored('[2]', Colors.BRIGHT_GREEN)} {bold('► Set Active Camera')}")
        print(f"{colored('[3]', Colors.BRIGHT_GREEN)} {bold('► Test Active Camera')}")
        print(f"{colored('[4]', Colors.BRIGHT_GREEN)} {bold('► Back to Main Menu')}\n")

        try:
            choice = int(input(f"{info('➤')} Enter Your Choice (1-4): "))
            if choice == 1:
                cameras = detect_available_cameras()
                print("\n" + separator("─", 70))
                if not cameras:
                    print(error("✗ No cameras detected in index range 0-5."))
                else:
                    print(success(f"✓ Found {len(cameras)} camera(s):"))
                    for cam in cameras:
                        print(f"  • Index {cam['index']} | {cam['resolution']} | {cam['fps']} FPS")
                print(separator("─", 70))
                input("\nPress ENTER to continue...")
            elif choice == 2:
                cam_index = input(f"{info('➤')} Enter camera index: ").strip()
                if not cam_index.isdigit():
                    print(error("✗ Camera index must be numeric."))
                    input("Press ENTER to continue...")
                    continue
                app_settings = update_setting("camera_index", int(cam_index))
                print(success(f"✓ Active camera set to index {cam_index}."))
                input("Press ENTER to continue...")
            elif choice == 3:
                check_camera.camer(app_settings['camera_index'])
                input("\nPress ENTER to continue...")
            elif choice == 4:
                main_menu()
                return
            else:
                print(error("⚠ Invalid choice!"))
        except ValueError:
            print(error("⚠ Invalid input!"))


def project_dashboard():
    """Display useful project analytics."""
    os.system('cls')
    training_count = len(os.listdir(storage_paths['TrainingImages']))
    model_count = len([f for f in os.listdir(storage_paths['TrainedModels']) if f.endswith(".yml")])
    attendance_count = len([f for f in os.listdir(storage_paths['AttendanceRecords']) if f.endswith(".csv")])
    student_count = len(data_manager.get_all_students())

    print_card(
        "PROJECT DASHBOARD",
        [
            f"Registered Students        : {student_count}",
            f"Captured Training Images   : {training_count}",
            f"Trained Model Files        : {model_count}",
            f"Attendance CSV Files       : {attendance_count}",
            f"Active Camera Index        : {app_settings['camera_index']}",
            f"Capture Sample Target      : {app_settings['max_capture_samples']}",
            f"Recognition Pass Mark      : {app_settings['recognition_pass_mark']}",
            f"UI Theme                   : {app_settings.get('ui_theme', 'neon')}",
        ]
    )
    print("\n" + separator("═", 70))
    input("\nPress ENTER to return to Main Menu...")
    main_menu()


def quick_pipeline():
    """Run complete flow in one menu option."""
    print_card(
        "QUICK PIPELINE MODE",
        [
            "Step 1: Capture faces",
            "Step 2: Train model",
            "Step 3: Start recognition",
            "Press Ctrl+C anytime to stop the current step."
        ]
    )
    start = input(f"\n{info('➤')} Start quick pipeline now? (Y/N): ").strip().lower()
    if start != "y":
        print(warning("⚠ Quick pipeline canceled."))
        input("Press ENTER to return...")
        main_menu()
        return
    capture_image.takeImages(
        storage_paths,
        data_manager,
        camera_index=app_settings['camera_index'],
        max_samples=app_settings['max_capture_samples']
    )
    train_image.TrainImages(storage_paths)
    recognize.recognize_attendence(
        storage_paths,
        data_manager,
        camera_index=app_settings['camera_index'],
        pass_mark=app_settings['recognition_pass_mark']
    )
    input(f"\n{success('✓')} Quick pipeline completed. Press ENTER to return...")
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
    global app_settings
    while True:
        os.system('cls')
        print("\n")
        print(highlight("╔" + "═" * 68 + "╗"))
        print(highlight("║" + " " * 22 + "SYSTEM SETTINGS" + " " * 31 + "║"))
        print(highlight("╚" + "═" * 68 + "╝"))
        
        print(f"\n{colored('[1]', Colors.BRIGHT_BLUE)} {bold('► Change Storage Location')}")
        print(f"{colored('[2]', Colors.BRIGHT_BLUE)} {bold('► Set Capture Sample Limit')}")
        print(f"{colored('[3]', Colors.BRIGHT_BLUE)} {bold('► Set Recognition Pass Mark')}")
        print(f"{colored('[4]', Colors.BRIGHT_BLUE)} {bold('► Switch UI Theme (Neon/Metasploit/Matrix)')}")
        print(f"{colored('[5]', Colors.BRIGHT_BLUE)} {bold('► Toggle Boot Animation')}")
        print(f"{colored('[6]', Colors.BRIGHT_BLUE)} {bold('► View System Info')}")
        print(f"{colored('[7]', Colors.BRIGHT_BLUE)} {bold('► Back to Main Menu')}\n")
        
        print(colored(separator("─", 60), Colors.BRIGHT_YELLOW))
        
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-7): "))
            if choice == 1:
                print(f"\n{warning('⚠')} Changing storage location...")
                input("Press ENTER to continue...")
                init_system()
            elif choice == 2:
                sample_limit = input(f"{info('➤')} Enter new capture sample limit (20-500): ").strip()
                if sample_limit.isdigit() and 20 <= int(sample_limit) <= 500:
                    app_settings = update_setting("max_capture_samples", int(sample_limit))
                    print(success(f"✓ Capture sample limit updated to {sample_limit}."))
                else:
                    print(error("✗ Invalid limit. Choose a number between 20 and 500."))
                input("Press ENTER to continue...")
            elif choice == 3:
                pass_mark = input(f"{info('➤')} Enter recognition pass mark (40-90): ").strip()
                if pass_mark.isdigit() and 40 <= int(pass_mark) <= 90:
                    app_settings = update_setting("recognition_pass_mark", int(pass_mark))
                    print(success(f"✓ Recognition pass mark updated to {pass_mark}."))
                else:
                    print(error("✗ Invalid mark. Choose a number between 40 and 90."))
                input("Press ENTER to continue...")
            elif choice == 4:
                theme = input(f"{info('➤')} Enter theme (neon/metasploit/matrix): ").strip().lower()
                if theme in ("neon", "metasploit", "matrix"):
                    app_settings = update_setting("ui_theme", theme)
                    print(success(f"✓ UI theme switched to {theme}."))
                else:
                    print(error("✗ Invalid theme."))
                input("Press ENTER to continue...")
            elif choice == 5:
                current = bool(app_settings.get("boot_animation", True))
                app_settings = update_setting("boot_animation", not current)
                mode = "enabled" if not current else "disabled"
                print(success(f"✓ Boot animation {mode}."))
                input("Press ENTER to continue...")
            elif choice == 6:
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
                print(f"{bold('Active Camera:')} {colored(str(app_settings['camera_index']), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Capture Samples:')} {colored(str(app_settings['max_capture_samples']), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Pass Mark:')} {colored(str(app_settings['recognition_pass_mark']), Colors.BRIGHT_GREEN)}")
                print(f"{bold('UI Theme:')} {colored(str(app_settings.get('ui_theme', 'neon')), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Boot Animation:')} {colored(str(app_settings.get('boot_animation', True)), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Team:')} {highlight('E2C TEAM')}")
                print(f"{bold('Version:')} 3.0 (Cyber UI Edition)\n")
                input("Press ENTER to continue...")
            elif choice == 7:
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

