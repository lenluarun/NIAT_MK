import os
import csv
import time
import datetime
import pandas as pd
from src.core.data import DataManager
from src.core.email_service import send_attendance_email

class BiometricManager:
    def __init__(self, storage_paths, data_manager):
        self.storage_paths = storage_paths
        self.data_manager = data_manager
        self.esp32_cam_ip = "0.0.0.0"
        self.controller_status = "offline"
        self.last_fp_event = {"slot": 0, "action": "none", "timestamp": 0}
        self.button_states = {
            "1": {"name": "Toggle Cam Preview", "last_pressed": "Never", "pin": 13},
            "2": {"name": "OLED Stats Display", "last_pressed": "Never", "pin": 27},
            "3": {"name": "Website PDF Download", "last_pressed": "Never", "pin": 32},
            "4": {"name": "Start Face Recognition", "last_pressed": "Never", "pin": 12}
        }
        self.stats_display_until = 0
        self.stats_lines = ["", "", ""]
        self.slot_mapping_file = os.path.join(
            os.path.dirname(self.data_manager.student_file), 
            "FingerprintSlots.csv"
        )
        self._init_slot_mapping()

    def _init_slot_mapping(self):
        if not os.path.exists(self.slot_mapping_file):
            with open(self.slot_mapping_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Slot', 'StudentId'])

    def get_student_id_from_slot(self, slot):
        try:
            students = self.data_manager.get_all_students()
            for student in students:
                if str(student.get('fp_slot', '')).strip() == str(slot).strip():
                    return str(student.get('id', '')).strip().lstrip('0')
        except Exception:
            pass
        return None

    def sync_hardware_database(self):
        """Sync student mapping to ESP32-CAM SD Card for OLED name lookup"""
        if not self.esp32_cam_ip or self.esp32_cam_ip == "0.0.0.0":
            return False, "ESP32-CAM IP not registered"
            
        try:
            students = self.data_manager.get_all_students()
            sd_data = []
            for s in students:
                if s.get('fp_slot'):
                    sd_data.append({
                        "slot": int(s['fp_slot']),
                        "name": s['name'],
                        "id": s['id']
                    })
            
            import requests
            url = f"http://{self.esp32_cam_ip}:81/sd/save?path=/students.json"
            response = requests.post(url, json=sd_data, timeout=5)
            return response.status_code == 200, "Sync successful" if response.status_code == 200 else f"Sync failed: {response.status_code}"
        except Exception as e:
            return False, f"Sync error: {str(e)}"

    def map_slot_to_student(self, slot, student_id):
        try:
            student_id = str(student_id).strip().lstrip('0')
            students = self.data_manager.get_all_students()
            target_student = next((s for s in students if str(s.get('id', '')).strip().lstrip('0') == student_id), None)
            
            if target_student:
                return self.data_manager.update_student(
                    target_student['id'], 
                    target_student['name'], 
                    target_student['email'], 
                    fp_slot=str(slot)
                )
            return False
        except Exception:
            return False

    def mark_attendance(self, student_id):
        """Mark attendance for a student (Fingerprint or Face)"""
        students = self.data_manager.get_all_students()
        student = next((s for s in students if str(s.get('id', '')).strip().lstrip('0') == student_id), None)
        
        if not student:
            return False, "Student not found in database"

        name = student.get('name', 'Unknown')
        email = student.get('email', '')
        
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        
        att_dir = self.storage_paths.get('Attendance') or self.storage_paths.get('AttendanceRecords')
        if not att_dir:
            return False, "Attendance directory not found"
            
        os.makedirs(att_dir, exist_ok=True)
        fileName = os.path.join(att_dir, f"Attendance_{date}.csv")
        
        new_record = pd.DataFrame([[student_id, name, email, date, timeStamp]], 
                                 columns=['Id', 'Name', 'Email', 'Date', 'Time'])
        
        if os.path.exists(fileName):
            existing_df = pd.read_csv(fileName, dtype={'Id': str})
            # Check if already marked today
            if student_id in existing_df['Id'].values:
                return True, f"Attendance already marked for {name}"
            
            combined_df = pd.concat([existing_df, new_record], ignore_index=True)
            combined_df.to_csv(fileName, index=False)
        else:
            new_record.to_csv(fileName, index=False)
            
        # Send Email Notification
        import threading
        email_thread = threading.Thread(target=send_attendance_email, args=(name, email, timeStamp))
        email_thread.daemon = True
        email_thread.start()
            
        return True, f"Attendance marked for {name}"
