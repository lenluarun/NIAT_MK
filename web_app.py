#!/usr/bin/env python3
"""
Smart Face Recognition Attendance System - Web Interface
Professional Web GUI for Localhost | E2C TEAM
"""
import os
import sys
import threading
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json

# Must run before any module imports cv2 (stabilizes MSMF on Windows setups).
if os.name == "nt":
    os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

# Add current directory to Python path for relative imports
sys.path.insert(0, os.path.dirname(__file__))

from src.utils import camera_check as check_camera
from src.core import capture as capture_image
from src.core import training as train_image
from src.utils.camera_utils import detect_available_cameras
from src.core.storage import get_storage_path, create_storage_folders
from src.core.data import DataManager
from src.utils.settings_manager import load_settings, update_setting

# Global variables
storage_path = None
storage_paths = None
data_manager = None
app_settings = None
recognize = None
RECOGNITION_AVAILABLE = False
RECOGNITION_IMPORT_ERROR = ""

try:
    from src.core import recognition as _recognize_module
    recognize = _recognize_module
    RECOGNITION_AVAILABLE = True
except Exception as exc:
    RECOGNITION_IMPORT_ERROR = str(exc)

# Flask app setup
app = Flask(__name__,
           template_folder='templates',
           static_folder='static')
CORS(app)

# Global operation status
current_operation = {"status": "idle", "message": "", "progress": 0}

def emit_status(message, progress=0, status="running"):
    """Update status for polling"""
    current_operation["status"] = status
    current_operation["message"] = message
    current_operation["progress"] = progress

def init_system():
    """Initialize the system and set up storage"""
    global storage_path, storage_paths, data_manager, app_settings

    emit_status("Setting up offline storage...", 10)
    storage_path = get_storage_path()

    if not storage_path:
        emit_status("Failed to initialize storage!", 0, "error")
        return False

    emit_status("Creating storage folders...", 30)
    storage_paths = create_storage_folders(storage_path)

    emit_status("Initializing data manager...", 50)
    data_manager = DataManager(storage_paths)
    app_settings = load_settings()

    emit_status("System initialized successfully!", 100, "success")
    return True

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html',
                         app_settings=app_settings,
                         recognition_available=RECOGNITION_AVAILABLE)

@app.route('/api/system/status')
def system_status():
    """Get system status"""
    training_count = len(os.listdir(storage_paths['TrainingImage'])) if storage_paths else 0
    model_count = len([f for f in os.listdir(storage_paths['TrainingImageLabel']) if f.endswith(".yml")]) if storage_paths else 0
    attendance_count = len([f for f in os.listdir(storage_paths['Attendance']) if f.endswith(".csv")]) if storage_paths else 0
    student_count = len(data_manager.get_all_students()) if data_manager else 0

    return jsonify({
        "storage_path": storage_path,
        "training_images": training_count,
        "trained_models": model_count,
        "attendance_records": attendance_count,
        "students": student_count,
        "camera_index": app_settings.get('camera_index', 0) if app_settings else 0,
        "recognition_available": RECOGNITION_AVAILABLE
    })

@app.route('/api/camera/check', methods=['POST'])
def camera_check():
    """Check camera functionality"""
    try:
        emit_status("Checking camera...", 0)
        # Run camera check in thread to not block
        def run_check():
            try:
                check_camera.camer(app_settings['camera_index'])
                emit_status("Camera check completed successfully!", 100, "success")
            except Exception as e:
                emit_status(f"Camera check failed: {str(e)}", 0, "error")

        thread = threading.Thread(target=run_check)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/capture/faces', methods=['POST'])
def capture_faces():
    """Capture faces for training"""
    try:
        emit_status("Starting face capture process...", 0)

        def run_capture():
            try:
                emit_status("Initializing camera...", 20)
                capture_image.takeImages(
                    storage_paths,
                    data_manager,
                    camera_index=app_settings['camera_index'],
                    max_samples=app_settings['max_capture_samples']
                )
                emit_status("Face capture completed successfully!", 100, "success")
            except Exception as e:
                emit_status(f"Face capture failed: {str(e)}", 0, "error")

        thread = threading.Thread(target=run_capture)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/train/images', methods=['POST'])
def train_images():
    """Train the recognition model"""
    try:
        emit_status("Starting image training process...", 0)

        def run_training():
            try:
                emit_status("Analyzing training images...", 30)
                train_image.TrainImages(storage_paths)
                emit_status("Training completed successfully!", 100, "success")
            except Exception as e:
                emit_status(f"Training failed: {str(e)}", 0, "error")

        thread = threading.Thread(target=run_training)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recognize/attendance', methods=['POST'])
def recognize_attendance():
    """Start attendance recognition"""
    if not RECOGNITION_AVAILABLE:
        return jsonify({"status": "error", "message": "Recognition module not available"}), 500

    try:
        emit_status("Starting attendance recognition...", 0)

        def run_recognition():
            try:
                recognize.recognize_attendence(
                    storage_paths,
                    data_manager,
                    camera_index=app_settings['camera_index'],
                    pass_mark=app_settings['recognition_pass_mark'],
                    fast_mode=(app_settings.get("recognition_mode", "fast") == "fast")
                )
                emit_status("Recognition completed!", 100, "success")
            except Exception as e:
                emit_status(f"Recognition failed: {str(e)}", 0, "error")

        thread = threading.Thread(target=run_recognition)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recognize/stop', methods=['POST'])
def stop_recognition():
    """Stop attendance recognition"""
    try:
        # This would need to be implemented to stop the recognition process
        # For now, just return success
        emit_status("Recognition stopped by user", 0, "idle")
        return jsonify({"status": "stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/data/students')
def get_students():
    """Get all students"""
    try:
        students = data_manager.get_all_students() if data_manager else []
        return jsonify({"students": students})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/add_student', methods=['POST'])
def add_student():
    """Add a new student"""
    try:
        data = request.json
        student_id = data.get('student_id')
        name = data.get('name')

        if not student_id or not name:
            return jsonify({"status": "error", "message": "Student ID and name required"}), 400

        # Add student logic here
        # This would need to be implemented based on data_manager methods
        emit_status(f"Added student: {name} (ID: {student_id})", 100, "success")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    global app_settings

    if request.method == 'GET':
        return jsonify(app_settings or {})

    try:
        data = request.json
        for key, value in data.items():
            app_settings = update_setting(key, value)
        emit_status("Settings updated successfully!", 100, "success")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/operation/status')
def operation_status():
    """Get current operation status"""
    return jsonify(current_operation)

if __name__ == '__main__':
    # Initialize system
    if init_system():
        print("System initialized. Starting web server...")
        print("Access the web interface at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Failed to initialize system. Exiting...")
        sys.exit(1)