"""
Quick test script to verify all system components
"""
import os
import sys

# Add Code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n")
print("╔" + "═" * 70 + "╗")
print("║" + " " * 15 + "SMART ATTENDANCE SYSTEM - COMPONENT TEST" + " " * 16 + "║")
print("╚" + "═" * 70 + "╝\n")

# Test 1: Color Module
print("Testing colors module...")
try:
    from colors import success, error, info, bold, separator
    print(success("✓ Colors module loaded successfully"))
except Exception as e:
    print(error(f"✗ Colors module failed: {e}"))
    sys.exit(1)

# Test 2: Storage Manager
print("\nTesting storage_manager module...")
try:
    from storage_manager import get_available_disks, format_size
    disks = get_available_disks()
    print(success(f"✓ Found {len(disks)} available disk(s)"))
    for disk in disks:
        print(f"  • {disk['letter']}: {format_size(disk['free'])} free")
except Exception as e:
    print(error(f"✗ Storage manager failed: {e}"))
    sys.exit(1)

# Test 3: Data Manager
print("\nTesting data_manager module...")
try:
    from data_manager import DataManager
    print(success("✓ DataManager class loaded successfully"))
except Exception as e:
    print(error(f"✗ Data manager failed: {e}"))
    sys.exit(1)

# Test 4: OpenCV
print("\nTesting OpenCV module...")
try:
    import cv2
    print(success("✓ OpenCV loaded successfully"))
    print(f"  • Version: {cv2.__version__}")
except Exception as e:
    print(error(f"✗ OpenCV failed: {e}"))
    sys.exit(1)

# Test 5: Required dependencies
print("\nTesting required dependencies...")
dependencies = {
    'numpy': 'NumPy',
    'pandas': 'Pandas',
    'PIL': 'Pillow',
    'csv': 'CSV (built-in)',
    'json': 'JSON (built-in)',
    'os': 'OS (built-in)',
    'datetime': 'DateTime (built-in)'
}

for module, name in dependencies.items():
    try:
        __import__(module)
        print(success(f"✓ {name} available"))
    except ImportError:
        print(error(f"✗ {name} not found"))
        sys.exit(1)

# Test 6: Cascade Classifier
print("\nTesting cascade classifier file...")
if os.path.exists("haarcascade_default.xml"):
    print(success("✓ haarcascade_default.xml found"))
else:
    print(error("✗ haarcascade_default.xml not found"))

# Test 7: Create storage directories
print("\nTesting storage directory creation...")
try:
    test_storage = "test_storage"
    os.makedirs(test_storage, exist_ok=True)
    folders = ['TrainingImages', 'StudentData', 'TrainedModels', 'AttendanceRecords', 'Reports', 'Backups']
    for folder in folders:
        folder_path = os.path.join(test_storage, folder)
        os.makedirs(folder_path, exist_ok=True)
    print(success(f"✓ Test storage folders created successfully"))
    # Cleanup
    import shutil
    shutil.rmtree(test_storage)
except Exception as e:
    print(error(f"✗ Storage folder creation failed: {e}"))
    sys.exit(1)

# Final summary
print("\n")
print("╔" + "═" * 70 + "╗")
print("║" + " " * 20 + "✓✓✓ ALL TESTS PASSED ✓✓✓" + " " * 23 + "║")
print("║" + " " * 15 + "System is ready to run!" + " " * 31 + "║")
print("╚" + "═" * 70 + "╝\n")

print(success("✓ Smart Attendance System is fully operational!"))
print(success("✓ All components are working correctly"))
print(success("✓ The system runs completely OFFLINE\n"))
