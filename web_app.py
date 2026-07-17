#!/usr/bin/env python3
"""
Smart Face Recognition Attendance System - Web Interface
Professional Web GUI for Localhost | E2C TEAM
"""
import os
import sys
import threading
import time
import csv
import cv2
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import json

from reportlab.lib import colors as pdf_colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph

# Must run before any module imports cv2 (stabilizes MSMF on Windows setups).
if os.name == "nt":
    os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")

# Add current directory to Python path for relative imports
sys.path.insert(0, os.path.dirname(__file__))

from src.utils import camera_check as check_camera
from src.core import capture as capture_image
from src.core import training as train_image
from src.core.updater import update_system_from_github
from src.utils.camera_utils import detect_available_cameras
from src.core.storage import get_storage_path, create_storage_folders
from src.core.data import DataManager
from src.utils.settings_manager import load_settings, update_setting
from src.core.biometric import BiometricManager

# Global variables
storage_path = None
storage_paths = None
data_manager = None
biometric_manager = None
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
last_recognition_result = {"marked": False, "student_id": None, "student_name": None, "message": ""}
pending_enrollment = {"student_id": None, "slot": 0}
preview_state = {"active": False, "frame": None, "label": ""}
camera_check_stop_event = threading.Event()
capture_stop_event = threading.Event()
recognition_stop_event = threading.Event()
recognition_running = False


def update_preview_frame(frame, label=None):
    if frame is None:
        return
    ok, buffer = cv2.imencode('.jpg', frame)
    if not ok:
        return
    preview_state["frame"] = buffer.tobytes()
    if label is not None:
        preview_state["label"] = label


def clear_preview_frame():
    preview_state["frame"] = None
    preview_state["label"] = ""


def preview_stream():
    boundary = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
    while True:
        frame = preview_state.get("frame")
        if frame:
            yield boundary + frame + b'\r\n'
        else:
            time.sleep(0.12)
            continue
        time.sleep(0.06)

def emit_status(message, progress=0, status="running"):
    """Update status for polling"""
    current_operation["status"] = status
    current_operation["message"] = message
    current_operation["progress"] = progress


def _attendance_directory():
    if not storage_paths:
        return None
    return storage_paths.get('Attendance') or storage_paths.get('AttendanceRecords')


def _attendance_files():
    attendance_dir = _attendance_directory()
    if not attendance_dir or not os.path.exists(attendance_dir):
        return []
    return sorted([f for f in os.listdir(attendance_dir) if f.lower().endswith('.csv')], reverse=True)


def _read_attendance_csv(file_name):
    attendance_dir = _attendance_directory()
    if not attendance_dir:
        return None

    file_path = os.path.join(attendance_dir, file_name)
    if not os.path.exists(file_path):
        return None

    records = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file_handle:
        reader = csv.reader(file_handle)
        next(reader, None)
        for row in reader:
            if not row or len(row) < 4:
                continue
            if len(row) >= 5:
                student_id, name, email, date_value, time_value = row[:5]
            else:
                student_id, name, date_value, time_value = row[:4]
                email = ''
            records.append({
                'student_id': str(student_id).strip().lstrip('0'),
                'name': str(name).strip(),
                'email': str(email).strip(),
                'date': str(date_value).strip(),
                'time': str(time_value).strip(),
            })

    all_students = data_manager.get_all_students() if data_manager else []
    marked_ids = {record['student_id'] for record in records}
    present_students = [record for record in records]
    absent_students = [
        student for student in all_students
        if str(student.get('id', '')).strip().lstrip('0') not in marked_ids
    ]

    return {
        'file_name': file_name,
        'file_path': file_path,
        'date': file_name.replace('Attendance_', '').replace('.csv', ''),
        'total_students': len(all_students),
        'present_count': len(present_students),
        'absent_count': len(absent_students),
        'records': present_students,
        'absent_students': absent_students,
    }


def _recognition_snapshot():
    files = _attendance_files()
    if not files:
        return {'file_name': None, 'record_count': 0, 'last_record': None}

    latest = _read_attendance_csv(files[0])
    if not latest:
        return {'file_name': None, 'record_count': 0, 'last_record': None}

    return {
        'file_name': latest['file_name'],
        'record_count': latest['present_count'],
        'last_record': latest['records'][-1] if latest['records'] else None,
    }


def _camera_scan_snapshot():
    scan_range = int(app_settings.get('camera_scan_range', 5)) if app_settings else 5
    cameras = detect_available_cameras(scan_range)
    return {
        'scan_range': scan_range,
        'cameras': cameras,
        'active_camera': app_settings.get('camera_index', 0) if app_settings else 0,
    }


def _build_recognition_result(before_snapshot):
    after_snapshot = _recognition_snapshot()
    if after_snapshot['record_count'] > before_snapshot.get('record_count', 0) and after_snapshot.get('last_record'):
        record = after_snapshot['last_record']
        return {
            'marked': True,
            'student_id': record.get('student_id'),
            'student_name': record.get('name'),
            'message': f"Recognized and marked: {record.get('name')} ({record.get('student_id')})",
        }

    return {
        'marked': False,
        'student_id': None,
        'student_name': None,
        'message': 'No user recognized or attendance was not marked.',
    }


def _export_attendance_pdf_file(report_data):
    attendance_dir = _attendance_directory()
    if not attendance_dir:
        raise FileNotFoundError('Attendance directory is not available')

    pdf_name = report_data['file_name'].replace('.csv', '_Report.pdf')
    pdf_path = os.path.join(attendance_dir, pdf_name)
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elements = []

    title_style = styles['Heading1']
    title_style.alignment = 1
    title_style.textColor = pdf_colors.HexColor('#1D4ED8')
    elements.append(Paragraph('SMART ATTENDANCE REPORT', title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Session: {report_data['file_name']}", styles['Normal']))
    elements.append(Paragraph(f"Present: {report_data['present_count']} | Absent: {report_data['absent_count']} | Total: {report_data['total_students']}", styles['Normal']))
    elements.append(Spacer(1, 16))

    summary_table = Table([
        ['Session', 'Present', 'Absent', 'Total'],
        [report_data['file_name'], str(report_data['present_count']), str(report_data['absent_count']), str(report_data['total_students'])]
    ], colWidths=[220, 80, 80, 80])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#CBD5E1')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    if report_data['records']:
        present_rows = [['ID', 'Name', 'Email', 'Time']]
        for record in report_data['records']:
            present_rows.append([record['student_id'], record['name'], record['email'] or '-', record['time'] or '-'])
        present_table = Table(present_rows, colWidths=[80, 180, 180, 70])
        present_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#16A34A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor('#F8FAFC')]),
        ]))
        elements.append(Paragraph('Present Students', styles['Heading2']))
        elements.append(present_table)
        elements.append(Spacer(1, 16))

    if report_data['absent_students']:
        absent_rows = [['ID', 'Name', 'Email']]
        for student in report_data['absent_students']:
            absent_rows.append([
                str(student.get('id', '')),
                str(student.get('name', '')),
                str(student.get('email', '')) or '-',
            ])
        absent_table = Table(absent_rows, colWidths=[80, 210, 170])
        absent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor('#DC2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor('#FEF2F2')]),
        ]))
        elements.append(Paragraph('Absent Students', styles['Heading2']))
        elements.append(absent_table)

    doc.build(elements)
    return pdf_path

def init_system():
    """Initialize the system and set up storage"""
    global storage_path, storage_paths, data_manager, app_settings, biometric_manager

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
    
    emit_status("Initializing biometric manager...", 75)
    biometric_manager = BiometricManager(storage_paths, data_manager)

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
    latest_report = _recognition_snapshot()

    return jsonify({
        "storage_path": storage_path,
        "training_images": training_count,
        "trained_models": model_count,
        "attendance_records": attendance_count,
        "students": student_count,
        "camera_index": app_settings.get('camera_index', 0) if app_settings else 0,
        "camera_scan_range": app_settings.get('camera_scan_range', 5) if app_settings else 5,
        "max_capture_samples": app_settings.get('max_capture_samples', 50) if app_settings else 50,
        "recognition_pass_mark": app_settings.get('recognition_pass_mark', 80) if app_settings else 80,
        "recognition_mode": app_settings.get('recognition_mode', 'fast') if app_settings else 'fast',
        "ui_theme": app_settings.get('ui_theme', 'e2c') if app_settings else 'e2c',
        "boot_animation": app_settings.get('boot_animation', True) if app_settings else True,
        "hud_mode": app_settings.get('hud_mode', True) if app_settings else True,
        "recognition_available": RECOGNITION_AVAILABLE,
        "recognition_import_error": RECOGNITION_IMPORT_ERROR,
        "latest_attendance": latest_report['file_name'],
        "camera_count": 1,
        "preview_active": preview_state.get("active", False),
    })

@app.route('/api/camera/check', methods=['POST'])
def camera_check():
    """Check camera functionality"""
    try:
        emit_status("Checking camera...", 0)
        camera_check_stop_event.clear()  # Clear stop event on new check
        # Run camera check in thread to not block
        def run_check():
            try:
                preview_state["active"] = True
                check_camera.camer(app_settings['camera_index'], frame_callback=lambda frame: update_preview_frame(frame, "camera-check"), show_window=False, stop_event=camera_check_stop_event)
                emit_status("Camera check completed successfully!", 100, "success")
            except Exception as e:
                emit_status(f"Camera check failed: {str(e)}", 0, "error")
            finally:
                preview_state["active"] = False
                clear_preview_frame()

        thread = threading.Thread(target=run_check)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/camera/check/stop', methods=['POST'])
def stop_camera_check():
    """Stop the camera check"""
    try:
        camera_check_stop_event.set()
        emit_status("Camera check stopped.", 100, "warning")
        return jsonify({"status": "stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/camera/scan')
def camera_scan():
    """Scan available camera devices."""
    try:
        return jsonify(_camera_scan_snapshot())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/camera/set', methods=['POST'])
def camera_set():
    """Update the active camera index (supports USB index or IP/URL for network cameras)."""
    global app_settings
    try:
        payload = request.get_json(silent=True) or {}
        camera_source = payload.get('camera_source')
        
        if camera_source is None:
            return jsonify({"status": "error", "message": "camera_source is required"}), 400

        # If it's numeric, treat as USB index
        try:
            camera_index = int(camera_source)
            app_settings = update_setting('camera_index', camera_index)
            emit_status(f"Active camera set to USB Index {camera_index}", 100, "success")
            return jsonify({
                "status": "success",
                "camera_index": camera_index,
                "camera_type": "usb"
            })
        except (TypeError, ValueError):
            pass
        
        # If not numeric, treat as IP/URL for network camera
        camera_source_str = str(camera_source).strip()
        if not camera_source_str:
            return jsonify({"status": "error", "message": "camera_source cannot be empty"}), 400
        
        # Support formats: http://192.168.1.100:8080/video or rtsp://... or IP address
        app_settings = update_setting('camera_index', camera_source_str)
        emit_status(f"Active camera set to network source: {camera_source_str}", 100, "success")
        return jsonify({
            "status": "success",
            "camera_source": camera_source_str,
            "camera_type": "network"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/capture/faces', methods=['POST'])
def capture_faces():
    """Capture faces for training"""
    try:
        payload = request.get_json(silent=True) or {}
        student_id = str(payload.get('student_id', '')).strip()
        student_name = str(payload.get('name', '')).strip()
        student_email = str(payload.get('email', '')).strip()
        quick_pipeline = bool(payload.get('quick_pipeline', False))
        max_samples = payload.get('max_samples', app_settings.get('max_capture_samples', 50) if app_settings else 50)

        try:
            max_samples = int(max_samples)
        except (TypeError, ValueError):
            max_samples = app_settings.get('max_capture_samples', 50) if app_settings else 50

        if not student_id or not student_name:
            return jsonify({"status": "error", "message": "Student ID and name are required"}), 400

        if not data_manager:
            return jsonify({"status": "error", "message": "Student database is not available"}), 500

        emit_status("Starting face capture process...", 0)
        capture_stop_event.clear()

        def run_capture():
            global last_recognition_result
            try:
                preview_state["active"] = True
                if not data_manager.student_exists(student_id):
                    data_manager.add_student(student_id, student_name, student_email)

                emit_status("Initializing camera...", 20)
                capture_image.takeImages(
                    storage_paths,
                    data_manager,
                    camera_index=app_settings['camera_index'],
                    max_samples=max_samples,
                    student_id=student_id,
                    student_name=student_name,
                    frame_callback=lambda frame: update_preview_frame(frame, "capture"),
                    show_window=False,
                    stop_event=capture_stop_event
                )

                if capture_stop_event.is_set():
                    emit_status("Face capture stopped by user.", 100, "warning")
                    return

                if quick_pipeline:
                    emit_status("Training model from captured images...", 70)
                    train_image.TrainImages(storage_paths)

                    if RECOGNITION_AVAILABLE:
                        emit_status("Running attendance recognition...", 85)
                        recognition_stop_event.clear()
                        before_snapshot = _recognition_snapshot()
                        recognize.recognize_attendence(
                            storage_paths,
                            data_manager,
                            camera_index=app_settings['camera_index'],
                            pass_mark=app_settings['recognition_pass_mark'],
                            fast_mode=(app_settings.get("recognition_mode", "fast") == "fast"),
                            stop_event=recognition_stop_event
                        )
                        last_recognition_result = _build_recognition_result(before_snapshot)
                        emit_status(last_recognition_result['message'], 100, "success")
                    else:
                        emit_status("Capture and training completed. Recognition unavailable.", 100, "success")
                else:
                    emit_status("Face capture completed successfully!", 100, "success")
            except Exception as e:
                emit_status(f"Face capture failed: {str(e)}", 0, "error")
            finally:
                preview_state["active"] = False
                clear_preview_frame()

        thread = threading.Thread(target=run_capture)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "started", "quick_pipeline": quick_pipeline})
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

def start_recognition_internal():
    """Start face recognition background process"""
    global recognition_running
    if recognition_running:
        return "started", "Already running"

    emit_status("Starting attendance recognition...", 0)
    recognition_stop_event.clear()
    before_snapshot = _recognition_snapshot()

    def handle_face_match(student_id, name):
        """Handle face recognition match for OLED and Web"""
        if biometric_manager:
            biometric_manager.last_match = {
                "type": "Face",
                "id": student_id,
                "name": name,
                "timestamp": time.time()
            }

    def run_recognition():
        global last_recognition_result, recognition_running
        try:
            recognition_running = True
            preview_state["active"] = True
            recognize.recognize_attendence(
                storage_paths,
                data_manager,
                camera_index=app_settings['camera_index'],
                pass_mark=app_settings['recognition_pass_mark'],
                fast_mode=(app_settings.get("recognition_mode", "fast") == "fast"),
                frame_callback=lambda frame: update_preview_frame(frame, "recognition"),
                match_callback=handle_face_match,
                show_window=False,
                max_runtime_seconds=45,
                stop_event=recognition_stop_event
            )
            
            if recognition_stop_event.is_set():
                emit_status("Recognition stopped by user", 100, "warning")
                return

            last_recognition_result = _build_recognition_result(before_snapshot)
            emit_status(last_recognition_result['message'], 100, "success")
        except Exception as e:
            emit_status(f"Recognition failed: {str(e)}", 0, "error")
        finally:
            recognition_running = False
            preview_state["active"] = False
            clear_preview_frame()

    thread = threading.Thread(target=run_recognition)
    thread.daemon = True
    thread.start()
    return "started", "Started"


@app.route('/api/recognize/attendance', methods=['POST'])
def recognize_attendance():
    """Start attendance recognition"""
    if not RECOGNITION_AVAILABLE:
        return jsonify({"status": "error", "message": "Recognition module not available"}), 500

    try:
        status, msg = start_recognition_internal()
        if status == "error":
            return jsonify({"status": "error", "message": msg}), 500
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/capture/stop', methods=['POST'])
def stop_capture():
    """Stop the face capture process"""
    try:
        capture_stop_event.set()
        recognition_stop_event.set() # Also stop recognition if in quick pipeline
        emit_status("Capture process stopping...", 100, "warning")
        return jsonify({"status": "stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/recognize/stop', methods=['POST'])
def stop_recognition():
    """Stop attendance recognition"""
    try:
        recognition_stop_event.set()
        emit_status("Recognition process stopping...", 100, "warning")
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
        student_id = str(data.get('student_id', '')).strip()
        name = str(data.get('name', '')).strip()
        email = str(data.get('email', '')).strip()

        if not student_id or not name:
            return jsonify({"status": "error", "message": "Student ID and name required"}), 400

        if not data_manager:
            return jsonify({"status": "error", "message": "Student database is not available"}), 500

        if data_manager.student_exists(student_id):
            return jsonify({"status": "error", "message": f"Student ID {student_id} already exists"}), 409

        if not data_manager.add_student(student_id, name, email):
            return jsonify({"status": "error", "message": "Failed to add student"}), 500

        emit_status(f"Added student: {name} (ID: {student_id})", 100, "success")
        return jsonify({"status": "success", "student": {"student_id": student_id, "name": name, "email": email}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/data/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    """Delete a student record."""
    try:
        if not data_manager:
            return jsonify({"status": "error", "message": "Student database is not available"}), 500

        if not data_manager.delete_student(student_id):
            return jsonify({"status": "error", "message": f"Student ID {student_id} not found"}), 404

        emit_status(f"Deleted student: {student_id}", 100, "success")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/data/reset', methods=['POST'])
def reset_database():
    """Reset student records, training images, and trained models."""
    try:
        payload = request.get_json(silent=True) or {}
        confirmation = str(payload.get('confirmation', '')).strip().upper()
        password = str(payload.get('password', '')).strip()
        full_reset = bool(payload.get('full_reset', False))

        if confirmation != 'RESET':
            return jsonify({"status": "error", "message": "Type RESET to confirm the reset"}), 400

        if not data_manager:
            return jsonify({"status": "error", "message": "Student database is not available"}), 500

        ok, message = data_manager.reset_database(password)
        if not ok:
            return jsonify({"status": "error", "message": message}), 400
            
        if full_reset and biometric_manager:
            biometric_manager.empty_sensor_db = True

        emit_status(message, 100, "success")
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reports/summary')
def reports_summary():
    """Return a simple reports overview for the dashboard."""
    try:
        attendance_files = []
        report_files = []

        if storage_paths:
            attendance_dir = storage_paths.get('Attendance') or storage_paths.get('AttendanceRecords')
            reports_dir = storage_paths.get('Reports')

            if attendance_dir and os.path.exists(attendance_dir):
                for file_name in sorted(os.listdir(attendance_dir), reverse=True):
                    if file_name.lower().endswith('.csv'):
                        file_path = os.path.join(attendance_dir, file_name)
                        attendance_files.append({
                            'name': file_name,
                            'path': file_path,
                            'size': os.path.getsize(file_path),
                        })

            if reports_dir and os.path.exists(reports_dir):
                for file_name in sorted(os.listdir(reports_dir), reverse=True):
                    if file_name.lower().endswith(('.txt', '.csv', '.pdf')):
                        file_path = os.path.join(reports_dir, file_name)
                        report_files.append({
                            'name': file_name,
                            'path': file_path,
                            'size': os.path.getsize(file_path),
                        })

        summary = {
            'students': len(data_manager.get_all_students()) if data_manager else 0,
            'attendance_files': len(attendance_files),
            'report_files': len(report_files),
            'latest_attendance': attendance_files[0] if attendance_files else None,
            'latest_report': report_files[0] if report_files else None,
            'attendance_files_list': attendance_files[:10],
            'report_files_list': report_files[:10],
        }

        return jsonify(summary)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reports/files')
def reports_files():
    """List attendance reports available in the dashboard."""
    try:
        reports = []
        for file_name in _attendance_files():
            report_data = _read_attendance_csv(file_name)
            if report_data:
                reports.append({
                    'file_name': report_data['file_name'],
                    'date': report_data['date'],
                    'present_count': report_data['present_count'],
                    'absent_count': report_data['absent_count'],
                    'total_students': report_data['total_students'],
                })
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/reports/view/<path:report_name>')
def view_report(report_name):
    """Return a detailed attendance report for browser rendering."""
    try:
        report_data = _read_attendance_csv(report_name)
        if not report_data:
            return jsonify({'status': 'error', 'message': 'Report not found'}), 404

        return jsonify({'status': 'success', 'report': report_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/reports/export/<path:report_name>', methods=['POST'])
def export_report(report_name):
    """Export the selected attendance report to PDF."""
    try:
        report_data = _read_attendance_csv(report_name)
        if not report_data:
            return jsonify({'status': 'error', 'message': 'Report not found'}), 404

        pdf_path = _export_attendance_pdf_file(report_data)
        pdf_name = os.path.basename(pdf_path)
        return jsonify({
            'status': 'success',
            'pdf_name': pdf_name,
            'download_url': f'/api/reports/download/{pdf_name}',
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/reports/download/<path:pdf_name>')
def download_report(pdf_name):
    """Download a generated report PDF."""
    attendance_dir = _attendance_directory()
    if not attendance_dir:
        return jsonify({'status': 'error', 'message': 'Attendance directory is not available'}), 500

    pdf_path = os.path.join(attendance_dir, pdf_name)
    if not os.path.exists(pdf_path):
        return jsonify({'status': 'error', 'message': 'PDF not found'}), 404

    return send_from_directory(attendance_dir, pdf_name, as_attachment=True)

@app.route('/api/data/edit_student/<student_id>', methods=['POST'])
def edit_student(student_id):
    """Edit student details (name/email)"""
    try:
        if not data_manager:
            return jsonify({"status": "error", "message": "Student database is not available"}), 500
        
        payload = request.get_json(silent=True) or {}
        name = str(payload.get('name', '')).strip()
        email = str(payload.get('email', '')).strip()
        
        if not name:
            return jsonify({"status": "error", "message": "Name is required"}), 400
        
        # Update student details in the database
        if data_manager.update_student(student_id, name, email):
            emit_status(f"Updated student {student_id}", 100, "success")
            return jsonify({"status": "success", "message": f"Student {student_id} updated successfully"})
        else:
            return jsonify({"status": "error", "message": f"Student {student_id} not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reports/delete/<path:report_name>', methods=['POST'])
def delete_attendance_report(report_name):
    """Delete an attendance CSV file"""
    try:
        attendance_dir = _attendance_directory()
        if not attendance_dir:
            return jsonify({"status": "error", "message": "Attendance directory is not available"}), 500
        
        file_path = os.path.join(attendance_dir, report_name)
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "Report not found"}), 404
        
        # Verify it's a CSV file
        if not report_name.lower().endswith('.csv'):
            return jsonify({"status": "error", "message": "Invalid file type"}), 400
        
        os.remove(file_path)
        emit_status(f"Deleted attendance report: {report_name}", 100, "success")
        return jsonify({"status": "success", "message": f"Report {report_name} deleted"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reports/delete-pdf/<path:pdf_name>', methods=['POST'])
def delete_pdf_report(pdf_name):
    """Delete a generated PDF report"""
    try:
        attendance_dir = _attendance_directory()
        if not attendance_dir:
            return jsonify({"status": "error", "message": "Attendance directory is not available"}), 500
        
        file_path = os.path.join(attendance_dir, pdf_name)
        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "PDF not found"}), 404
        
        # Verify it's a PDF file
        if not pdf_name.lower().endswith('.pdf'):
            return jsonify({"status": "error", "message": "Invalid file type"}), 400
        
        os.remove(file_path)
        emit_status(f"Deleted PDF report: {pdf_name}", 100, "success")
        return jsonify({"status": "success", "message": f"PDF {pdf_name} deleted"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reports/close_session/<report_name>', methods=['POST'])
def close_session(report_name):
    """Close the session and send absent emails to students not marked present."""
    if not data_manager:
        return jsonify({"status": "error", "message": "System not initialized"}), 500

    try:
        csv_path = os.path.join(_attendance_directory(), report_name)
        if not os.path.exists(csv_path):
            return jsonify({"status": "error", "message": "Report file not found"}), 404

        # Extract date from filename (e.g., Attendance_2026-06-09.csv -> 2026-06-09)
        date_str = report_name.replace('Attendance_', '').replace('.csv', '')

        # Get present students
        present_df = pd.read_csv(csv_path, dtype={'Id': str})
        if 'Id' not in present_df.columns:
            return jsonify({"status": "error", "message": "Invalid report format"}), 400

        present_ids = set(present_df['Id'].astype(str).str.strip().str.lstrip('0'))

        # Get all students
        all_students = data_manager.get_all_students()
        absent_students = []
        for s in all_students:
            sid = str(s.get('id', '')).strip().lstrip('0')
            if sid and sid not in present_ids:
                absent_students.append(s)

        if not absent_students:
            return jsonify({"status": "success", "absent_count": 0, "message": "All students are present."})

        # Send emails in a background thread to prevent UI blocking
        import threading
        from src.core.email_service import send_absent_email

        def notify_absentees():
            for s in absent_students:
                send_absent_email(s.get('name', 'Unknown Student'), s.get('email', ''), date_str)

        t = threading.Thread(target=notify_absentees)
        t.daemon = True
        t.start()

        return jsonify({"status": "success", "absent_count": len(absent_students), "message": f"Sending absent notices to {len(absent_students)} students."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reports/download-csv/<report_name>')
def download_attendance_csv(report_name):
    """Download attendance CSV file"""
    attendance_dir = _attendance_directory()
    if not attendance_dir:
        return jsonify({"status": "error", "message": "Attendance directory is not available"}), 500
    
    file_path = os.path.join(attendance_dir, report_name)
    if not os.path.exists(file_path) or not report_name.lower().endswith('.csv'):
        return jsonify({"status": "error", "message": "File not found"}), 404
    
    return send_from_directory(attendance_dir, report_name, as_attachment=True)


@app.route('/api/reports/export-excel/<path:report_name>')
def export_attendance_excel(report_name):
    """Export attendance report to Excel (CSV format)"""
    try:
        report_data = _read_attendance_csv(report_name)
        if not report_data:
            return jsonify({"status": "error", "message": "Report not found"}), 404
        
        attendance_dir = _attendance_directory()
        excel_name = report_name.replace('.csv', '_Export.csv')
        excel_path = os.path.join(attendance_dir, excel_name)
        
        with open(excel_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(['ATTENDANCE SESSION EXPORT', report_data['file_name'], f"Total: {report_data['total_students']}", f"Present: {report_data['present_count']}", f"Absent: {report_data['absent_count']}"])
            writer.writerow([])
            
            # Present students
            writer.writerow(['PRESENT STUDENTS'])
            writer.writerow(['Student ID', 'Name', 'Email', 'Date', 'Time'])
            for record in report_data['records']:
                writer.writerow([record['student_id'], record['name'], record['email'], record['date'], record['time']])
            
            writer.writerow([])
            # Absent students
            writer.writerow(['ABSENT STUDENTS'])
            writer.writerow(['Student ID', 'Name', 'Email'])
            for student in report_data['absent_students']:
                writer.writerow([student.get('id', ''), student.get('name', ''), student.get('email', '')])
        
        return jsonify({
            "status": "success",
            "excel_name": excel_name,
            "download_url": f'/api/reports/download-csv/{excel_name}'
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/reports/statistics')
def attendance_statistics():
    """Get attendance statistics"""
    try:
        attendance_files = _attendance_files()
        students = data_manager.get_all_students() if data_manager else []
        
        total_marked = 0
        daily_data = {}
        student_attendance = {}
        
        for file_name in attendance_files:
            report_data = _read_attendance_csv(file_name)
            if report_data:
                daily_data[report_data['date']] = {
                    'date': report_data['date'],
                    'present': report_data['present_count'],
                    'absent': report_data['absent_count'],
                    'total': report_data['total_students'],
                }
                total_marked += report_data['present_count']
                
                # Track individual student attendance
                for record in report_data['records']:
                    sid = record['student_id']
                    if sid not in student_attendance:
                        student_attendance[sid] = {'name': record['name'], 'present': 0, 'sessions': 0}
                    student_attendance[sid]['present'] += 1
                    student_attendance[sid]['sessions'] += 1
        
        # Add absent sessions to student records
        for file_name in attendance_files:
            report_data = _read_attendance_csv(file_name)
            if report_data:
                for student in report_data['absent_students']:
                    sid = str(student.get('id', '')).strip().lstrip('0')
                    if sid and sid not in student_attendance:
                        student_attendance[sid] = {'name': student.get('name', 'Unknown'), 'present': 0, 'sessions': 0}
                    if sid and sid in student_attendance:
                        student_attendance[sid]['sessions'] += 1
        
        return jsonify({
            'total_marked': total_marked,
            'total_students': len(students),
            'total_sessions': len(attendance_files),
            'daily_data': sorted(daily_data.values(), key=lambda x: x['date'], reverse=True)[:30],
            'student_attendance': student_attendance,
            'attendance_files': len(attendance_files),
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/data/import-students', methods=['POST'])
def import_students_bulk():
    """Import students from CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({"status": "error", "message": "Only CSV files are accepted"}), 400
        
        if not data_manager:
            return jsonify({"status": "error", "message": "Student database is not available"}), 500
        
        added = 0
        skipped = 0
        errors = []
        
        try:
            stream = file.stream.read().decode('UTF8', errors='ignore').split('\n')
            csv_reader = csv.reader(stream)
            next(csv_reader, None)  # Skip header
            
            for row in csv_reader:
                if not row or len(row) < 2:
                    continue
                
                student_id = str(row[0]).strip()
                name = str(row[1]).strip()
                email = str(row[2]).strip() if len(row) > 2 else ''
                
                if not student_id or not name:
                    skipped += 1
                    continue
                
                try:
                    if not data_manager.student_exists(student_id):
                        data_manager.add_student(student_id, name, email)
                        added += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append(f"Row {student_id}: {str(e)}")
            
            message = f"Imported {added} students"
            if skipped > 0:
                message += f", {skipped} skipped"
            if errors:
                message += f", {len(errors)} errors"
            
            emit_status(message, 100, "success")
            return jsonify({
                "status": "success",
                "added": added,
                "skipped": skipped,
                "errors": errors
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to parse CSV: {str(e)}"}), 400
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


@app.route('/api/system/update', methods=['POST'])
def update_system():
    """Update the system from GitHub."""
    try:
        emit_status("Updating system from GitHub...", 0)

        def run_update():
            try:
                emit_status("Pulling latest code...", 25)
                result = update_system_from_github()
                if result.get("success"):
                    emit_status("System updated successfully from GitHub. Restart the server to use the changes.", 100, "success")
                else:
                    emit_status(f"Update failed: {result.get('message', 'Unknown error')}", 0, "error")
            except Exception as e:
                emit_status(f"Update failed: {str(e)}", 0, "error")

        thread = threading.Thread(target=run_update)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/operation/status')
def operation_status():
    """Get current operation status"""
    # Include last recognition result so the UI can display student popups
    try:
        result = dict(current_operation)
        result['last_recognition_result'] = last_recognition_result
        result['preview_active'] = preview_state.get("active", False)
        result['recognition_running'] = recognition_running
        if 'trigger_download' in current_operation:
            del current_operation['trigger_download']
        return jsonify(result)
    except Exception:
        # If result is already created, make sure we still try to delete trigger_download
        if 'trigger_download' in current_operation:
            del current_operation['trigger_download']
        return jsonify(current_operation)


@app.route('/api/camera/preview')
def camera_preview():
    """Stream the current camera preview into the web UI."""
    return Response(stream_with_context(preview_stream()), mimetype='multipart/x-mixed-replace; boundary=frame')

# ─── BIOMETRIC INTEGRATION ROUTES ───

@app.route('/api/controller/poll', methods=['GET'])
def controller_poll():
    """Endpoint for ESP32 Controller to poll for commands"""
    if not biometric_manager:
        return jsonify({"status": "error"}), 500
    
    sensor_ready = request.args.get('sensor_ready', '0') == '1'
    biometric_manager.controller_status = "online" if sensor_ready else "online (sensor error)"
    
    # Check for recent matches to display on OLED
    oled_line1 = "SYSTEM READY" if sensor_ready else "SENSOR ERROR"
    oled_line2 = "Face & Finger"
    oled_line3 = "Scan now..."
    
    enroll_slot = 0
    if pending_enrollment.get("slot", 0) > 0:
        enroll_slot = pending_enrollment["slot"]
        oled_line1 = "ENROLL MODE"
        oled_line2 = f"Slot #{enroll_slot}"
        oled_line3 = "Place finger..."
    elif hasattr(biometric_manager, "last_match") and (time.time() - biometric_manager.last_match.get("timestamp", 0)) < 5:
        # Show match for 5 seconds
        match = biometric_manager.last_match
        oled_line1 = f"{match['type']} MATCHED!"
        oled_line2 = match['name'][:20] # Truncate if too long
        oled_line3 = f"ID: {match['id']}"
    
    if time.time() < getattr(biometric_manager, "stats_display_until", 0):
        oled_line1, oled_line2, oled_line3 = biometric_manager.stats_lines

    response = {
        "esp32_cam_ip": biometric_manager.esp32_cam_ip,
        "oled_line1": oled_line1,
        "oled_line2": oled_line2,
        "oled_line3": oled_line3,
        "enroll_slot": enroll_slot,
        "delete_slot": 0,  # Set to > 0 to trigger deletion
        "empty_sensor_db": getattr(biometric_manager, "empty_sensor_db", False), # Set to True to wipe sensor
        "unlock_duration": getattr(biometric_manager, "unlock_duration", 0),
        "hazard": getattr(biometric_manager, "hazard", False),
        "preview_active": preview_state.get("active", False)
    }

    # Auto-reset one-time triggers
    if getattr(biometric_manager, "unlock_duration", 0) > 0:
        biometric_manager.unlock_duration = 0
    if getattr(biometric_manager, "empty_sensor_db", False):
        biometric_manager.empty_sensor_db = False

    return jsonify(response)

@app.route('/api/controller/event', methods=['POST'])
def controller_event():
    """Endpoint for ESP32 Controller to post events (matches, errors)"""
    global last_recognition_result, pending_enrollment
    if not biometric_manager:
        return jsonify({"status": "error"}), 500
        
    data = request.get_json(silent=True) or {}
    action = data.get('action', '')
    slot = data.get('slot', 0)
    status = data.get('status', '')
    confidence = data.get('confidence', 0)

    biometric_manager.last_fp_event = {
        "slot": slot,
        "action": action,
        "timestamp": time.time()
    }

    if action == "button_press":
        button_id = str(slot)
        if button_id in biometric_manager.button_states:
            import datetime
            now_str = datetime.datetime.now().strftime('%H:%M:%S')
            biometric_manager.button_states[button_id]["last_pressed"] = now_str

        if slot == 1: # Start/Stop Cam Preview
            if not preview_state.get("active", False):
                emit_status("Checking camera...", 0)
                camera_check_stop_event.clear()
                def run_check():
                    try:
                        preview_state["active"] = True
                        check_camera.camer(app_settings['camera_index'], frame_callback=lambda frame: update_preview_frame(frame, "camera-check"), show_window=False, stop_event=camera_check_stop_event)
                        emit_status("Camera check completed successfully!", 100, "success")
                    except Exception as e:
                        emit_status(f"Camera check failed: {str(e)}", 0, "error")
                    finally:
                        preview_state["active"] = False
                        clear_preview_frame()
                thread = threading.Thread(target=run_check)
                thread.daemon = True
                thread.start()
                emit_status("Camera preview started by physical button", 100, "success")
            else:
                camera_check_stop_event.set()
                emit_status("Camera preview stopped by physical button", 100, "warning")
            return jsonify({"status": "success", "preview_active": preview_state.get("active", False)})

        elif slot == 2: # OLED Stats Display
            students = data_manager.get_all_students()
            total_students = len(students)
            enrolled_fps = sum(1 for s in students if s.get('fp_slot') and str(s['fp_slot']).strip() != "")

            present_count = 0
            absent_count = total_students

            # Find today's report or latest report
            files = _attendance_files()
            if files:
                today_date = datetime.datetime.now().strftime('%Y-%m-%d')
                today_file = f"Attendance_{today_date}.csv"
                if today_file in files:
                    report_data = _read_attendance_csv(today_file)
                    if report_data:
                        present_count = report_data.get('present_count', 0)
                        absent_count = report_data.get('absent_count', total_students)
                else:
                    report_data = _read_attendance_csv(files[0])
                    if report_data:
                        present_count = report_data.get('present_count', 0)
                        absent_count = report_data.get('absent_count', total_students)

            biometric_manager.stats_display_until = time.time() + 8 # Show for 8 seconds
            biometric_manager.stats_lines = [
                f"Total Reg: {total_students}",
                f"Present: {present_count}",
                f"Absent:  {absent_count}"
            ]
            emit_status(f"Physical Button 2: Stats displayed on OLED (Reg: {total_students}, Pres: {present_count}, Abs: {absent_count})", 100, "success")
            return jsonify({"status": "success"})

        elif slot == 3: # Download PDF
            files = _attendance_files()
            if files:
                latest_file = files[0]
                try:
                    report_data = _read_attendance_csv(latest_file)
                    if report_data:
                        pdf_path = _export_attendance_pdf_file(report_data)
                        pdf_name = os.path.basename(pdf_path)
                        current_operation["trigger_download"] = f"/api/reports/download/{pdf_name}"
                        emit_status(f"Physical Button 3: PDF download triggered for {latest_file}", 100, "success")
                        return jsonify({"status": "success", "pdf_name": pdf_name})
                except Exception as e:
                    emit_status(f"Physical Button 3: PDF export error: {str(e)}", 0, "error")
                    return jsonify({"status": "error", "message": str(e)}), 500
            else:
                emit_status("Physical Button 3: No attendance logs found to export", 0, "error")
                return jsonify({"status": "error", "message": "No reports found"}), 404

            return jsonify({"status": "success"})

        elif slot == 4: # Toggle Face Recognition
            global recognition_running
            if not recognition_running:
                status, msg = start_recognition_internal()
                if status == "error":
                    emit_status(f"Physical Button 4: Recognition start failed: {msg}", 0, "error")
                    return jsonify({"status": "error", "message": msg}), 500
                emit_status("Physical Button 4: Face recognition started", 100, "success")
            else:
                recognition_stop_event.set()
                emit_status("Physical Button 4: Face recognition stopped", 100, "warning")
            return jsonify({"status": "success", "recognition_active": recognition_running})
    
    if action == "enroll_success" and slot > 0:
        student_id = pending_enrollment["student_id"]
        if student_id:
            biometric_manager.map_slot_to_student(slot, student_id)
            emit_status(f"Fingerprint enrolled successfully for ID {student_id}", 100, "success")
            
            # Sync to ESP32-CAM SD Card for name lookup
            threading.Thread(target=biometric_manager.sync_hardware_database, daemon=True).start()

        pending_enrollment = {"student_id": None, "slot": 0}
        return jsonify({"status": "success"})
        
    if action.startswith("enroll_fail") or action == "enroll_duplicate":
        pending_enrollment = {"student_id": None, "slot": 0}
        emit_status(f"Fingerprint enrollment failed: {status}", 0, "error")
        return jsonify({"status": "failed"})

    if action == "match" and slot > 0:
        student_id = biometric_manager.get_student_id_from_slot(slot)
        if student_id:
            success, message = biometric_manager.mark_attendance(student_id)
            student = next((s for s in data_manager.get_all_students() if str(s.get('id', '')).strip().lstrip('0') == student_id), None)
            
            last_recognition_result = {
                'marked': success,
                'student_id': student_id,
                'student_name': student.get('name') if student else 'Unknown',
                'message': f"Fingerprint: {message}",
            }
            emit_status(last_recognition_result['message'], 100, "success")
            
            return jsonify({
                "status": "success",
                "name": student.get('name') if student else "Access Granted",
                "id": student_id
            })
    
    return jsonify({"status": "received"})

@app.route('/api/biometric/enroll', methods=['POST'])
def trigger_enrollment():
    """Trigger fingerprint enrollment for a student"""
    global pending_enrollment
    if not biometric_manager:
        return jsonify({"status": "error", "message": "Biometric manager not ready"}), 500
        
    data = request.get_json(silent=True) or {}
    student_id = str(data.get('student_id', '')).strip().lstrip('0')
    
    if not student_id:
        return jsonify({"status": "error", "message": "Student ID required"}), 400
        
    # Find an available slot (1-1000 for R307S)
    students = data_manager.get_all_students()
    occupied_slots = {int(s['fp_slot']) for s in students if s.get('fp_slot') and str(s['fp_slot']).isdigit()}
    
    target_slot = 1
    while target_slot in occupied_slots:
        target_slot += 1
        
    if target_slot > 1000:
        return jsonify({"status": "error", "message": "No available slots"}), 500
        
    pending_enrollment = {"student_id": student_id, "slot": target_slot}
    preview_state["active"] = False # Stop live cam during enrollment
    emit_status(f"Please place finger on sensor to enroll for student {student_id}", 0, "running")
    
    return jsonify({"status": "success", "slot": target_slot})

@app.route('/api/camera/poll', methods=['GET'])
def camera_poll():
    """Endpoint for ESP32-CAM to poll and register its IP"""
    if biometric_manager:
        # Capture the remote address as the ESP32-CAM IP
        biometric_manager.esp32_cam_ip = request.remote_addr
    
    return jsonify({"flash": getattr(biometric_manager, "flash", False)})

@app.route('/api/hardware/control', methods=['POST'])
def hardware_control():
    """Trigger hardware events like flash, unlock, or hazard"""
    if not biometric_manager:
        return jsonify({"status": "error"}), 500
        
    data = request.get_json(silent=True) or {}
    
    if 'flash' in data:
        biometric_manager.flash = bool(data['flash'])
    if 'hazard' in data:
        biometric_manager.hazard = bool(data['hazard'])
    if 'unlock' in data:
        biometric_manager.unlock_duration = int(data['unlock'])
        
    return jsonify({"status": "success", "flash": getattr(biometric_manager, "flash", False), "hazard": getattr(biometric_manager, "hazard", False)})

@app.route('/api/controller/custom_oled', methods=['GET', 'POST'])
def custom_oled_endpoint():
    """Receive or send custom OLED byte arrays"""
    if not biometric_manager:
        return Response(b'\x00' * 1024, mimetype='application/octet-stream')
        
    if request.method == 'POST':
        # Accept binary data
        data = request.get_data()
        if len(data) == 1024:
            biometric_manager.custom_oled_image = data
            biometric_manager.custom_oled_trigger = True
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "Invalid length"}), 400
        
    # GET request from hardware
    image = getattr(biometric_manager, "custom_oled_image", None)
    if not image or len(image) != 1024:
        image = b'\x00' * 1024
    return Response(image, mimetype='application/octet-stream')

@app.route('/api/fingerprint/upload_image', methods=['POST'])
def fp_upload_image():
    """Receive fingerprint image from controller"""
    slot = request.args.get('slot', 0)
    # Save image if needed, or just acknowledge
    return jsonify({"status": "success"})

@app.route('/api/fingerprint/upload_template', methods=['POST'])
def fp_upload_template():
    """Receive fingerprint template from controller"""
    slot = request.args.get('slot', 0)
    # Save template if needed
    return jsonify({"status": "success"})

@app.route('/api/controller/live_face', methods=['GET'])
def controller_live_face():
    """Provide a small 128x64 bitmap of the last face detected for the OLED"""
    frame_bytes = preview_state.get("frame")
    if not frame_bytes:
        return Response(b'\x00' * 1024, mimetype='application/octet-stream')

    # Cache to avoid re-processing same frame
    if hasattr(controller_live_face, "last_frame") and controller_live_face.last_frame == frame_bytes:
        return Response(controller_live_face.last_packed, mimetype='application/octet-stream')

    try:
        import numpy as np
        # Decode JPG
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)

        if img is None:
            return Response(b'\x00' * 1024, mimetype='application/octet-stream')

        h, w = img.shape
        target_aspect = 128.0 / 64.0
        current_aspect = w / float(h)
        if current_aspect > target_aspect:
            new_w = int(h * target_aspect)
            x_offset = (w - new_w) // 2
            img = img[:, x_offset:x_offset+new_w]
        else:
            new_h = int(w / target_aspect)
            y_offset = (h - new_h) // 2
            img = img[y_offset:y_offset+new_h, :]

        resized = cv2.resize(img, (128, 64))

        # Simple threshold
        _, bw = cv2.threshold(resized, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        packed = np.zeros((1024,), dtype=np.uint8)
        bw_flat = bw.flatten()
        for i in range(1024):
            byte_val = 0
            for bit in range(8):
                idx = i * 8 + bit
                if bw_flat[idx] > 128:
                    byte_val |= (1 << (7 - bit))
            packed[i] = byte_val

        packed_bytes = packed.tobytes()
        controller_live_face.last_frame = frame_bytes
        controller_live_face.last_packed = packed_bytes

        return Response(packed_bytes, mimetype='application/octet-stream')
    except Exception as e:
        print("Error generating OLED frame:", e)
        return Response(b'\x00' * 1024, mimetype='application/octet-stream')

@app.route('/api/biometric/config', methods=['GET', 'POST'])
def biometric_config():
    """Get or update biometric configuration and mappings"""
    if not biometric_manager:
        return jsonify({"status": "error"}), 500
        
    if request.method == 'GET':
        students = data_manager.get_all_students()
        # Student dicts already contain fp_slot from data_manager.get_all_students()
            
        return jsonify({
            "esp32_cam_ip": biometric_manager.esp32_cam_ip,
            "controller_status": biometric_manager.controller_status,
            "students": students,
            "button_states": getattr(biometric_manager, "button_states", {})
        })
        
    data = request.get_json(silent=True) or {}
    student_id = str(data.get('student_id', '')).strip().lstrip('0')
    slot = data.get('slot', 0)
    
    if student_id and slot > 0:
        biometric_manager.map_slot_to_student(slot, student_id)
        return jsonify({"status": "success"})
        
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    # Initialize system
    if init_system():
        print("System initialized. Starting web server...")
        print("Access the web interface at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Failed to initialize system. Exiting...")
        sys.exit(1)
