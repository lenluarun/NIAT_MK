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
last_recognition_result = {"marked": False, "student_id": None, "student_name": None, "message": ""}
preview_state = {"active": False, "frame": None, "label": ""}
camera_check_stop_event = threading.Event()


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
        "latest_attendance": latest_report['file_name'],
        "camera_count": 1,
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
                )

                if quick_pipeline:
                    emit_status("Training model from captured images...", 70)
                    train_image.TrainImages(storage_paths)

                    if RECOGNITION_AVAILABLE:
                        emit_status("Running attendance recognition...", 85)
                        before_snapshot = _recognition_snapshot()
                        recognize.recognize_attendence(
                            storage_paths,
                            data_manager,
                            camera_index=app_settings['camera_index'],
                            pass_mark=app_settings['recognition_pass_mark'],
                            fast_mode=(app_settings.get("recognition_mode", "fast") == "fast")
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

@app.route('/api/recognize/attendance', methods=['POST'])
def recognize_attendance():
    """Start attendance recognition"""
    if not RECOGNITION_AVAILABLE:
        return jsonify({"status": "error", "message": "Recognition module not available"}), 500

    try:
        emit_status("Starting attendance recognition...", 0)
        before_snapshot = _recognition_snapshot()

        def run_recognition():
            global last_recognition_result
            try:
                preview_state["active"] = True
                recognize.recognize_attendence(
                    storage_paths,
                    data_manager,
                    camera_index=app_settings['camera_index'],
                    pass_mark=app_settings['recognition_pass_mark'],
                    fast_mode=(app_settings.get("recognition_mode", "fast") == "fast"),
                    frame_callback=lambda frame: update_preview_frame(frame, "recognition"),
                    show_window=False,
                    max_runtime_seconds=45,
                )
                last_recognition_result = _build_recognition_result(before_snapshot)
                emit_status(last_recognition_result['message'], 100, "success")
            except Exception as e:
                emit_status(f"Recognition failed: {str(e)}", 0, "error")
            finally:
                preview_state["active"] = False
                clear_preview_frame()

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

        if confirmation != 'RESET':
            return jsonify({"status": "error", "message": "Type RESET to confirm the reset"}), 400

        if not data_manager:
            return jsonify({"status": "error", "message": "Student database is not available"}), 500

        ok, message = data_manager.reset_database(password)
        if not ok:
            return jsonify({"status": "error", "message": message}), 400

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


@app.route('/api/reports/download-csv/<path:report_name>')
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
        return jsonify(result)
    except Exception:
        return jsonify(current_operation)


@app.route('/api/camera/preview')
def camera_preview():
    """Stream the current camera preview into the web UI."""
    return Response(stream_with_context(preview_stream()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Initialize system
    if init_system():
        print("System initialized. Starting web server...")
        print("Access the web interface at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Failed to initialize system. Exiting...")
        sys.exit(1)