"""
Storage manager for selecting and managing data storage location
"""
import os
import json
import shutil
from pathlib import Path
from ..utils.colors import success, error, warning, info, bold, separator, highlight


CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'storage_config.json')


def get_available_disks():
    """Get all available disk drives"""
    disks = []
    if os.name == 'nt':  # Windows
        import string
        for drive in string.ascii_uppercase:
            drive_letter = f"{drive}:\\"
            if os.path.exists(drive_letter):
                try:
                    total, used, free = shutil.disk_usage(drive_letter)
                    disks.append({
                        'letter': drive,
                        'path': drive_letter,
                        'total': total,
                        'free': free,
                        'used': used
                    })
                except:
                    pass
    return disks


def format_size(bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


def select_storage_location():
    """Allow user to select storage location"""
    os.system('cls')
    print("\n")
    print(highlight("╔" + "═" * 68 + "╗"))
    print(highlight("║" + " " * 15 + "SELECT STORAGE LOCATION FOR ATTENDANCE DATA" + " " * 12 + "║"))
    print(highlight("╚" + "═" * 68 + "╝"))
    
    disks = get_available_disks()
    
    if not disks:
        print(error("✗ No disk drives found!"))
        return None
    
    print(info("\n📀 Available Disk Drives:"))
    print(separator("─", 70))
    
    for idx, disk in enumerate(disks, 1):
        free_space = format_size(disk['free'])
        total_space = format_size(disk['total'])
        drive_str = f"{disk['letter']}:\\"
        print(f"\n  {bold(f'[{idx}]')} {bold(drive_str)} - {bold(free_space)} free of {bold(total_space)}")
    
    print("\n" + separator("─", 70))
    
    while True:
        try:
            choice = int(input(f"\n{bold('➤')} Select drive (1-{len(disks)}): "))
            if 1 <= choice <= len(disks):
                selected_disk = disks[choice - 1]
                base_path = os.path.join(selected_disk['path'], "E2C_Attendance_System")
                
                print(f"\n{info('⏳')} Creating storage directory...")
                os.makedirs(base_path, exist_ok=True)
                
                config = {
                    'storage_path': base_path,
                    'disk_letter': selected_disk['letter'],
                    'disk_path': selected_disk['path']
                }
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=4)
                
                print(f"{success('✓')} Storage location set successfully!")
                print(f"{info('📁')} Path: {bold(base_path)}\n")
                return base_path
            else:
                print(warning("⚠ Invalid choice!"))
        except ValueError:
            print(warning("⚠ Please enter a valid number!"))


def get_storage_path():
    """Get the storage path, prompt if not configured"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                path = config.get('storage_path')
                if os.path.exists(path):
                    return path
        except:
            pass
    
    # Default to src directory
    return os.path.join(os.path.dirname(__file__), '..', '..', 'src')


def create_storage_folders(base_path):
    """Create necessary storage folders"""
    folders = [
        'models',
        'data',
        'reports'
    ]
    
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
    
    return {
        'TrainingImage': os.path.join(base_path, 'models', 'TrainingImage'),
        'TrainingImageLabel': os.path.join(base_path, 'models', 'TrainingImageLabel'),
        'StudentData': os.path.join(base_path, 'data', 'StudentDetails'),
        'Attendance': os.path.join(base_path, 'data', 'Attendance'),
        'Models': os.path.join(base_path, 'models'),
        'Reports': os.path.join(base_path, 'reports')
    }
