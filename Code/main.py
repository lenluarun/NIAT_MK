"""
Smart Face Recognition Attendance System - Main Module
Completely Offline | E2C TEAM
"""
import os
import sys

# Must run before any module imports cv2 (stabilizes MSMF on some Windows setups).
if os.name == "nt":
    os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

import check_camera
import capture_image
import train_image
from camera_utils import detect_available_cameras
from ui_console import (
    render_banner, clear_screen, print_card, boot_sequence,
    render_symbol_wall, render_hud_status, print_menu_block
)
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
recognize = None
RECOGNITION_AVAILABLE = False
RECOGNITION_IMPORT_ERROR = ""

try:
    import recognize as _recognize_module
    recognize = _recognize_module
    RECOGNITION_AVAILABLE = True
except Exception as exc:
    RECOGNITION_IMPORT_ERROR = str(exc)


def configure_console_encoding():
    """Force UTF-8 output on Windows to avoid Unicode print crashes."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # Keep app running even if reconfiguration is unavailable.
        pass


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
    if not RECOGNITION_AVAILABLE:
        print(warning("⚠ Recognition module unavailable."))
        print(warning(f"⚠ Reason: {RECOGNITION_IMPORT_ERROR}"))
        print(info("ℹ Capture/Train/Camera features are still available.\n"))
    input("Press ENTER to continue...")


def title_bar():
    """Display the main title bar"""
    clear_screen()
    render_banner(app_settings.get("ui_theme", "neon"))
    render_symbol_wall(app_settings.get("ui_theme", "neon"))


def main_menu():
    """Display main menu with all options"""
    title_bar()
    if app_settings.get("hud_mode", True):
        render_hud_status(
            "CONTROL DECK",
            [
                ("Active Cam", app_settings["camera_index"]),
                ("Samples", app_settings["max_capture_samples"]),
                ("Pass Mark", app_settings["recognition_pass_mark"]),
                ("Rec Mode", app_settings.get("recognition_mode", "fast")),
                ("Theme", app_settings.get("ui_theme", "neon")),
            ],
        )
    print_menu_block(
        "MAIN MENU // CHOOSE MODULE",
        [
            ("1", "► Camera Check"),
            ("2", "► Capture Faces"),
            ("3", "► Train Images"),
            ("4", "► Recognize & Attendance"),
            ("5", "► Camera Studio (Scan/Select)"),
            ("6", "► Project Dashboard"),
            ("7", "► Data Management"),
            ("8", "► View Reports"),
            ("9", "► System Settings"),
            ("10", "► Quick Pipeline (Capture > Train > Recognize)"),
            ("11", "► Exit"),
        ],
        accent=Colors.BRIGHT_CYAN
    )
    
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
    try:
        check_camera.camer(app_settings['camera_index'])
    except KeyboardInterrupt:
        print(warning("\n⚠ Camera check canceled by user."))
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def capture_faces_option():
    """Capture faces option"""
    try:
        capture_image.takeImages(
            storage_paths,
            data_manager,
            camera_index=app_settings['camera_index'],
            max_samples=app_settings['max_capture_samples']
        )
    except KeyboardInterrupt:
        print(warning("\n⚠ Face capture canceled by user."))
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def train_images_option():
    """Train images option"""
    try:
        train_image.TrainImages(storage_paths)
    except KeyboardInterrupt:
        print(warning("\n⚠ Training canceled by user."))
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def recognize_faces_option():
    """Recognize faces option"""
    if not RECOGNITION_AVAILABLE:
        print(error("✗ Recognition is disabled because required dependency failed to load."))
        print(warning(f"⚠ Details: {RECOGNITION_IMPORT_ERROR}"))
        input("\nPress ENTER to return to Main Menu...")
        main_menu()
        return
    try:
        recognize.recognize_attendence(
            storage_paths,
            data_manager,
            camera_index=app_settings['camera_index'],
            pass_mark=app_settings['recognition_pass_mark'],
            fast_mode=(app_settings.get("recognition_mode", "fast") == "fast")
        )
    except KeyboardInterrupt:
        print(warning("\n⚠ Recognition canceled by user."))
    input(f"\n{success('✓')} Press ENTER to return to Main Menu...")
    main_menu()


def camera_studio_menu():
    """Camera utility and selection menu."""
    global app_settings
    while True:
        title_bar()
        render_hud_status(
            "CAMERA STUDIO",
            [
                ("Active Camera", app_settings["camera_index"]),
                ("Scan Range", app_settings.get("camera_scan_range", 5)),
                ("HUD", "ON" if app_settings.get("hud_mode", True) else "OFF"),
            ],
        )
        print_menu_block(
            "CAMERA OPERATIONS",
            [
                ("1", "► Scan Available Cameras"),
                ("2", "► Set Active Camera (manual index)"),
                ("3", "► Test Active Camera"),
                ("4", "► Smart Select Camera From List"),
                ("5", "► Show Active Camera Details"),
                ("6", "► Back to Main Menu"),
            ],
            accent=Colors.BRIGHT_GREEN
        )

        try:
            choice = int(input(f"{info('➤')} Enter Your Choice (1-6): "))
            if choice == 1:
                cameras = detect_available_cameras(app_settings.get("camera_scan_range", 5))
                print("\n" + separator("─", 70))
                if not cameras:
                    print(error("✗ No cameras detected in configured index range."))
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
                cameras = detect_available_cameras(app_settings.get("camera_scan_range", 5))
                if not cameras:
                    print(error("✗ No cameras available for smart selection."))
                    input("Press ENTER to continue...")
                    continue
                print(success("✓ Available cameras:"))
                for cam in cameras:
                    print(f"  [{cam['index']}] {cam['resolution']} @ {cam['fps']} FPS")
                selected = input(f"{info('➤')} Choose camera index from list: ").strip()
                if not selected.isdigit():
                    print(error("✗ Selection must be numeric."))
                else:
                    target = int(selected)
                    if any(cam["index"] == target for cam in cameras):
                        app_settings = update_setting("camera_index", target)
                        print(success(f"✓ Active camera switched to {target}."))
                    else:
                        print(error("✗ Selected index is not in scanned camera list."))
                input("Press ENTER to continue...")
            elif choice == 5:
                cameras = detect_available_cameras(app_settings.get("camera_scan_range", 5))
                current = next((cam for cam in cameras if cam["index"] == app_settings["camera_index"]), None)
                if current:
                    print_card(
                        "ACTIVE CAMERA PROFILE",
                        [
                            f"Camera Index   : {current['index']}",
                            f"Resolution     : {current['resolution']}",
                            f"Reported FPS   : {current['fps']}",
                            f"Scan Range     : 0-{app_settings.get('camera_scan_range', 5)}",
                            "Status         : Ready",
                        ],
                    )
                else:
                    print(warning("⚠ Active camera not detected in current scan range."))
                input("\nPress ENTER to continue...")
            elif choice == 6:
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
    if not RECOGNITION_AVAILABLE:
        print(error("✗ Quick pipeline unavailable because recognition module is disabled."))
        print(info("ℹ You can still run capture + training manually from the main menu."))
        print(warning(f"⚠ Details: {RECOGNITION_IMPORT_ERROR}"))
        input("\nPress ENTER to return to Main Menu...")
        main_menu()
        return
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
    try:
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
            pass_mark=app_settings['recognition_pass_mark'],
            fast_mode=(app_settings.get("recognition_mode", "fast") == "fast")
        )
    except KeyboardInterrupt:
        print(warning("\n⚠ Quick pipeline canceled by user."))
        input("Press ENTER to return...")
        main_menu()
        return
    input(f"\n{success('✓')} Quick pipeline completed. Press ENTER to return...")
    main_menu()


def data_management_menu():
    """Data management menu"""
    while True:
        title_bar()
        print_menu_block(
            "DATA MANAGEMENT OPTIONS",
            [
                ("1", "► View All Students"),
                ("2", "► Add Single Student"),
                ("3", "► Add Multiple Students (Bulk)"),
                ("4", "► Delete Student"),
                ("5", "► Complete Database Reset (Password Protected)"),
                ("6", "► Back to Main Menu"),
            ],
            accent=Colors.BRIGHT_GREEN
        )
        
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-6): "))
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
                        print(success(f"✓ Student {student_id} and related training images deleted successfully!"))
                    else:
                        print(error(f"✗ Failed to delete student {student_id}!"))
                    input("Press ENTER to continue...")
                except Exception as e:
                    print(error(f"✗ Error: {e}"))
                    input("Press ENTER to continue...")
            elif choice == 5:
                print(warning("⚠ This will clear Student database, Training images, and Trained models."))
                print(info("ℹ Attendance report files are not deleted."))
                confirm = input(f"{info('➤')} Type RESET to continue: ").strip()
                if confirm != "RESET":
                    print(warning("⚠ Reset canceled."))
                    input("Press ENTER to continue...")
                    continue
                pwd = input(f"{info('🔐')} Enter reset password: ").strip()
                ok, msg = data_manager.reset_database(pwd)
                if ok:
                    print(success(f"✓ {msg}"))
                else:
                    print(error(f"✗ Reset failed: {msg}"))
                input("Press ENTER to continue...")
            elif choice == 6:
                main_menu()
                break
            else:
                print(error("⚠ Invalid Choice!"))
        except ValueError:
            print(error("⚠ Invalid Input!"))


def view_reports_menu():
    """View reports menu"""
    while True:
        title_bar()
        print_menu_block(
            "REPORTS CENTER",
            [
                ("1", "► Attendance Report"),
                ("2", "► Student Database Report"),
                ("3", "► Back to Main Menu"),
            ],
            accent=Colors.BRIGHT_MAGENTA
        )
        
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
        title_bar()
        print_menu_block(
            "SYSTEM SETTINGS",
            [
                ("1", "► Change Storage Location"),
                ("2", "► Set Capture Sample Limit"),
                ("3", "► Set Recognition Pass Mark"),
                ("4", "► Set Recognition Mode (Fast/Accurate)"),
                ("5", "► Switch UI Theme (Neon/E2C/Matrix/Abyss/Phantom)"),
                ("6", "► Toggle Boot Animation"),
                ("7", "► Configure Camera Scan Range"),
                ("8", "► Toggle HUD Status Panel"),
                ("9", "► View System Info"),
                ("10", "► Back to Main Menu"),
            ],
            accent=Colors.BRIGHT_BLUE
        )
        
        try:
            choice = int(input(f"\n{info('➤')} Enter Your Choice (1-10): "))
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
                mode = input(f"{info('➤')} Enter recognition mode (fast/accurate): ").strip().lower()
                if mode in ("fast", "accurate"):
                    app_settings = update_setting("recognition_mode", mode)
                    print(success(f"✓ Recognition mode set to {mode}."))
                else:
                    print(error("✗ Invalid mode. Use fast or accurate."))
                input("Press ENTER to continue...")
            elif choice == 5:
                theme = input(f"{info('➤')} Enter theme (neon/e2c/matrix/abyss/phantom): ").strip().lower()
                if theme in ("neon", "e2c", "matrix", "abyss", "phantom"):
                    app_settings = update_setting("ui_theme", theme)
                    print(success(f"✓ UI theme switched to {theme}."))
                else:
                    print(error("✗ Invalid theme."))
                input("Press ENTER to continue...")
            elif choice == 6:
                current = bool(app_settings.get("boot_animation", True))
                app_settings = update_setting("boot_animation", not current)
                mode = "enabled" if not current else "disabled"
                print(success(f"✓ Boot animation {mode}."))
                input("Press ENTER to continue...")
            elif choice == 7:
                scan_range = input(f"{info('➤')} Enter camera scan max index (1-20): ").strip()
                if scan_range.isdigit() and 1 <= int(scan_range) <= 20:
                    app_settings = update_setting("camera_scan_range", int(scan_range))
                    print(success(f"✓ Camera scan range updated to 0-{scan_range}."))
                else:
                    print(error("✗ Invalid range. Choose a number between 1 and 20."))
                input("Press ENTER to continue...")
            elif choice == 8:
                current = bool(app_settings.get("hud_mode", True))
                app_settings = update_setting("hud_mode", not current)
                mode = "enabled" if not current else "disabled"
                print(success(f"✓ HUD panel {mode}."))
                input("Press ENTER to continue...")
            elif choice == 9:
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
                print(f"{bold('Camera Scan Range:')} {colored(str(app_settings.get('camera_scan_range', 5)), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Capture Samples:')} {colored(str(app_settings['max_capture_samples']), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Pass Mark:')} {colored(str(app_settings['recognition_pass_mark']), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Recognition Mode:')} {colored(str(app_settings.get('recognition_mode', 'fast')), Colors.BRIGHT_GREEN)}")
                print(f"{bold('UI Theme:')} {colored(str(app_settings.get('ui_theme', 'neon')), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Boot Animation:')} {colored(str(app_settings.get('boot_animation', True)), Colors.BRIGHT_GREEN)}")
                print(f"{bold('HUD Mode:')} {colored(str(app_settings.get('hud_mode', True)), Colors.BRIGHT_GREEN)}")
                print(f"{bold('Team:')} {highlight('E2C TEAM')}")
                print(f"{bold('Version:')} 4.0 (Cinematic UI Edition)\n")
                input("Press ENTER to continue...")
            elif choice == 10:
                main_menu()
                break
            else:
                print(error("⚠ Invalid Choice!"))
        except ValueError:
            print(error("⚠ Invalid Input!"))


if __name__ == "__main__":
    try:
        configure_console_encoding()
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

