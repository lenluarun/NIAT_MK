"""
Data manager for student records and attendance operations
"""
import os
import csv
import json
from datetime import datetime
from ..utils.colors import success, error, warning, info, bold, separator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


class DataManager:
    def __init__(self, storage_paths):
        self.storage_paths = storage_paths
        self.student_file = os.path.join(storage_paths['StudentData'], 'StudentDetails.csv')
        self.init_student_file()
    
    def init_student_file(self):
        """Initialize student CSV if it doesn't exist"""
        if not os.path.exists(self.student_file):
            with open(self.student_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Id', 'Name', 'Email', 'DateAdded'])
    
    def add_student(self, student_id, name, email=''):
        """Add a new student"""
        try:
            with open(self.student_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([student_id, name, email, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            return True
        except Exception as e:
            print(error(f"✗ Error adding student: {e}"))
            return False
    
    def student_exists(self, student_id):
        """Check if student exists"""
        try:
            with open(self.student_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if row and row[0] == str(student_id):
                        return True
        except:
            pass
        return False
    
    def get_all_students(self):
        """Get all students"""
        students = []
        try:
            with open(self.student_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if row and len(row) >= 2:
                        students.append({
                            'id': str(row[0]).strip(),
                            'name': row[1].strip(),
                            'email': row[2].strip() if len(row) > 2 else '',
                            'date_added': row[3].strip() if len(row) > 3 else ''
                        })
        except:
            pass
        return students
    
    def delete_student(self, student_id):
        """Delete a student and their training images."""
        try:
            student_id = str(student_id).strip()
            students = self.get_all_students()
            target_student = next((s for s in students if s['id'] == student_id), None)
            if not target_student:
                return False

            with open(self.student_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Id', 'Name', 'Email', 'DateAdded'])
                for student in students:
                    if student['id'] != student_id:
                        writer.writerow([student['id'], student['name'], student['email'], student['date_added']])

            self._delete_student_training_images(student_id, target_student.get('name', ''))
            return True
        except:
            return False

    def _delete_student_training_images(self, student_id, student_name=''):
        """Delete all captured training images for one student."""
        training_path = self.storage_paths.get('TrainingImages')
        if not training_path or not os.path.exists(training_path):
            return 0

        removed = 0
        for file_name in os.listdir(training_path):
            if not file_name.lower().endswith(".jpg"):
                continue
            # Capture format: {name}.{id}.{sample}.jpg
            if f".{student_id}." in file_name:
                try:
                    os.remove(os.path.join(training_path, file_name))
                    removed += 1
                except:
                    pass
            elif student_name and file_name.startswith(f"{student_name}."):
                try:
                    os.remove(os.path.join(training_path, file_name))
                    removed += 1
                except:
                    pass
        return removed

    def reset_database(self, password):
        """
        Reset core student database only.
        Clears student CSV, training images and trained models.
        """
        if password != "E2C":
            return False, "Invalid password."

        try:
            # Reset student database file
            with open(self.student_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Id', 'Name', 'Email', 'DateAdded'])

            # Clear training images
            cleared_images = 0
            training_path = self.storage_paths.get('TrainingImages')
            if training_path and os.path.exists(training_path):
                for file_name in os.listdir(training_path):
                    file_path = os.path.join(training_path, file_name)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            cleared_images += 1
                        except:
                            pass

            # Clear trained models
            cleared_models = 0
            model_path = self.storage_paths.get('TrainedModels')
            if model_path and os.path.exists(model_path):
                for file_name in os.listdir(model_path):
                    file_path = os.path.join(model_path, file_name)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            cleared_models += 1
                        except:
                            pass

            return True, f"Database reset complete. Removed {cleared_images} images and {cleared_models} model files."
        except Exception as e:
            return False, str(e)
    
    def display_all_students(self):
        """Display all students in a formatted table"""
        students = self.get_all_students()
        
        if not students:
            print(warning("⚠ No students found!"))
            return
        
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  📊 STUDENT DATABASE - Total: {len(students)} Students\n"))
        print(bold("═" * 80))
        
        id_header = bold('ID')
        name_header = bold('Name')
        email_header = bold('Email')
        date_header = bold('Added Date')
        print(f"\n{id_header:<10} {name_header:<25} {email_header:<30} {date_header:<15}")
        print(separator("─", 80))
        
        for idx, student in enumerate(students, 1):
            print(f"{student['id']:<10} {student['name']:<25} {student['email']:<30} {student['date_added']:<15}")
        
        print(f"\n{separator('─', 80)}")
        print(f"\n{success(f'✓ Total Students: {len(students)}')}\n")
    
    def add_single_student_interactive(self):
        """Add a single student interactively"""
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  👤 ADD SINGLE STUDENT\n"))
        print(bold("═" * 80 + "\n"))
        
        while True:
            try:
                student_id = input(f"{info('➤')} Enter Student ID (Numeric): ").strip()
                
                if not student_id.isdigit():
                    print(error("✗ ID must be numeric!"))
                    continue
                
                if self.student_exists(student_id):
                    print(error(f"✗ Student ID {student_id} already exists!"))
                    continue
                
                name = input(f"{info('➤')} Enter Student Name (Alphabetic): ").strip()
                
                if not name.isalpha():
                    print(error("✗ Name must contain only alphabetic characters!"))
                    continue
                
                email = input(f"{info('➤')} Enter Email (Optional, press Enter to skip): ").strip()
                
                if self.add_student(student_id, name, email):
                    print(f"\n{success('✓')} Student added successfully!")
                    print(f"{success('✓')} ID: {bold(student_id)}, Name: {bold(name)}\n")
                    return True
                else:
                    print(error("✗ Failed to add student!"))
                    return False
                    
            except Exception as e:
                print(error(f"✗ Error: {e}"))
                return False
    
    def add_bulk_students_interactive(self):
        """Add multiple students interactively"""
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  👥 ADD MULTIPLE STUDENTS - BULK IMPORT\n"))
        print(bold("═" * 80))
        
        print(f"\n{info('Choose method:')}")
        print(f"{info('[1]')} Manual Entry - Enter each student one by one")
        print(f"{info('[2]')} Import from CSV File")
        
        choice = input(f"\n{info('➤')} Select method (1-2): ").strip()
        
        if choice == '1':
            return self._bulk_manual_entry()
        elif choice == '2':
            return self._bulk_csv_import()
        else:
            print(error("✗ Invalid choice!"))
            return False
    
    def _bulk_manual_entry(self):
        """Manual entry for multiple students"""
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  📝 BULK STUDENT ENTRY - Manual\n"))
        print(bold("═" * 80 + "\n"))
        
        print(f"{info('Enter student details. Type END when finished.')}\n")
        
        added_count = 0
        failed_count = 0
        
        while True:
            try:
                student_id = input(f"\n{info('➤')} Student ID (or 'END' to finish): ").strip()
                
                if student_id.upper() == 'END':
                    break
                
                if not student_id.isdigit():
                    print(error("✗ ID must be numeric!"))
                    continue
                
                if self.student_exists(student_id):
                    print(error(f"✗ ID {student_id} already exists, skipping..."))
                    failed_count += 1
                    continue
                
                name = input(f"{info('➤')} Student Name: ").strip()
                
                if not name.isalpha():
                    print(error("✗ Name must contain only alphabetic characters!"))
                    failed_count += 1
                    continue
                
                email = input(f"{info('➤')} Email (Optional): ").strip()
                
                if self.add_student(student_id, name, email):
                    print(success(f"✓ Added: {name} (ID: {student_id})"))
                    added_count += 1
                else:
                    print(error(f"✗ Failed to add {name}"))
                    failed_count += 1
                    
            except Exception as e:
                print(error(f"✗ Error: {e}"))
                failed_count += 1
        
        # Summary
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  ✓ BULK IMPORT SUMMARY\n"))
        print(bold("═" * 80 + "\n"))
        print(f"{success(f'✓ Students Added: {added_count}')}")
        print(f"{error(f'✗ Failed: {failed_count}')}\n")
        return added_count > 0
    
    def _bulk_csv_import(self):
        """Import students from CSV file"""
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  📤 BULK STUDENT IMPORT - From CSV\n"))
        print(bold("═" * 80 + "\n"))
        
        try:
            csv_file = input(f"\n{info('➤')} Enter CSV file path (or 'SAMPLE' to create sample): ").strip()
            
            if csv_file.upper() == 'SAMPLE':
                self._create_sample_csv()
                return False
            
            if not os.path.exists(csv_file):
                print(error(f"✗ File not found: {csv_file}"))
                return False
            
            added_count = 0
            failed_count = 0
            
            print(f"\n{info('⏳')} Reading CSV file...\n")
            
            with open(csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, 1):
                    try:
                        student_id = str(row.get('Id', '')).strip()
                        name = str(row.get('Name', '')).strip()
                        email = str(row.get('Email', '')).strip()
                        
                        if not student_id or not name:
                            print(error(f"✗ Row {row_num}: Missing ID or Name, skipping..."))
                            failed_count += 1
                            continue
                        
                        if not student_id.isdigit():
                            print(error(f"✗ Row {row_num}: Invalid ID format, skipping..."))
                            failed_count += 1
                            continue
                        
                        if not name.replace(' ', '').isalpha():
                            print(error(f"✗ Row {row_num}: Invalid name format, skipping..."))
                            failed_count += 1
                            continue
                        
                        if self.student_exists(student_id):
                            print(warning(f"⚠ Row {row_num}: ID {student_id} already exists, skipping..."))
                            failed_count += 1
                            continue
                        
                        if self.add_student(student_id, name, email):
                            print(success(f"✓ Row {row_num}: Added {name} (ID: {student_id})"))
                            added_count += 1
                        else:
                            print(error(f"✗ Row {row_num}: Failed to add {name}"))
                            failed_count += 1
                            
                    except Exception as e:
                        print(error(f"✗ Row {row_num}: Error - {e}"))
                        failed_count += 1
                        continue
            
            # Summary
            os.system('cls')
            print("\n")
            print(bold("═" * 80))
            print(bold(f"\n  ✓ CSV IMPORT SUMMARY\n"))
            print(bold("═" * 80 + "\n"))
            print(f"{success(f'✓ Students Added: {added_count}')}")
            print(f"{error(f'✗ Failed: {failed_count}')}\n")
            return added_count > 0
            
        except Exception as e:
            print(error(f"✗ Import failed: {e}"))
            return False
    
    def _create_sample_csv(self):
        """Create a sample CSV file for import"""
        sample_file = 'sample_students.csv'
        
        try:
            with open(sample_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Id', 'Name', 'Email'])
                writer.writerow(['101', 'John Smith', 'john@example.com'])
                writer.writerow(['102', 'Sarah Johnson', 'sarah@example.com'])
                writer.writerow(['103', 'Michael Brown', 'michael@example.com'])
            
            print(success(f"✓ Sample CSV created: {bold(sample_file)}"))
            print(f"{info('📝')} Edit this file and use it to import students.\n")
            
        except Exception as e:
            print(error(f"✗ Error creating sample: {e}"))
    
    def generate_attendance_report(self):
        """Generate, Manage and Export Attendance Reports"""
        attendance_path = self.storage_paths['AttendanceRecords']
        
        while True:
            os.system('cls')
            print("\n")
            print(bold("═" * 80))
            print(bold(f"\n  📈 ATTENDANCE REPORTS MANAGER\n"))
            print(bold("═" * 80))
            
            attendance_files = [f for f in os.listdir(attendance_path) if f.endswith('.csv')]
            
            if not attendance_files:
                print(warning("\n⚠ No attendance records found!"))
                return
            
            print(f"\n{info('Available Records (Latest 20):')}")
            print(separator("─", 80))
            
            # Sort files with latest first
            sorted_files = sorted(attendance_files, reverse=True)[:20]
            for idx, file in enumerate(sorted_files, 1):
                try:
                    with open(os.path.join(attendance_path, file), 'r') as f:
                        records = len(f.readlines()) - 1
                        print(f"[{idx}] {file} - {records} records")
                except:
                    print(f"[{idx}] {file} - (Error reading)")
            
            print(separator("─", 80))
            print(f"{info('[V]')} View a record  |  {info('[D]')} Delete a record  |  {info('[E]')} Export to PDF  |  {info('[Q]')} Go Back")
            
            choice = input(f"\n{info('➤')} Enter choice (V/D/E/Q): ").strip().upper()
            
            if choice == 'Q':
                break
                
            elif choice == 'V':
                sel = input(f"{info('➤')} Enter record number to view: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(sorted_files):
                    file_to_view = sorted_files[int(sel) - 1]
                    self._view_attendance_report(file_to_view)
                else:
                    print(error("✗ Invalid selection."))
                input("Press ENTER to continue...")
                
            elif choice == 'D':
                sel = input(f"{info('➤')} Enter record number to delete: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(sorted_files):
                    file_to_del = sorted_files[int(sel) - 1]
                    confirm = input(f"{warning('⚠')} Delete {file_to_del}? (Y/N): ").strip().upper()
                    if confirm == 'Y':
                        try:
                            os.remove(os.path.join(attendance_path, file_to_del))
                            print(success(f"✓ Deleted successfully!"))
                        except Exception as e:
                            print(error(f"✗ Failed to delete: {e}"))
                else:
                    print(error("✗ Invalid selection."))
                input("Press ENTER to continue...")
                
            elif choice == 'E':
                sel = input(f"{info('➤')} Enter record number to export to PDF: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(sorted_files):
                    file_to_exp = sorted_files[int(sel) - 1]
                    self._export_attendance_pdf(file_to_exp)
                else:
                    print(error("✗ Invalid selection."))
                input("Press ENTER to continue...")

    def _show_attendance_preview(self, csv_filename, marked_list, unmarked_list, attendance_records):
        """Show attendance report preview in terminal"""
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  📊 ATTENDANCE REPORT PREVIEW\n"))
        print(bold("═" * 80))
        
        session_name = csv_filename.replace('Attendance_', '').replace('.csv', '').replace('_', ' ')
        print(f"Session: {bold(session_name)}")
        print(f"Total Students: {bold(len(marked_list) + len(unmarked_list))}")
        print(f"Present: {bold(len(marked_list))} | Absent: {bold(len(unmarked_list))}")
        print(separator("─", 80))
        
        # Show attendance records with timestamps
        if attendance_records:
            print(f"\n{info('✓ ATTENDANCE RECORDS (Present Students):')}")
            print(separator("─", 80))
            print(f"{'ID':<10} {'Name':<25} {'Time':<12} {'Date'}")
            print(separator("─", 80))
            for record in attendance_records:
                print(f"{record['id']:<10} {record['name']:<25} {record['time']:<12} {record['date']}")
        
        # Show present students
        if marked_list:
            print(f"\n{info('✓ PRESENT STUDENTS:')}")
            print(separator("─", 80))
            print(f"{'ID':<10} {'Name'}")
            print(separator("─", 80))
            for student in marked_list:
                print(f"{student[0]:<10} {student[1]}")
        else:
            print(f"\n{warning('⚠ No students marked as present.')}")
        
        # Show absent students
        if unmarked_list:
            print(f"\n{error('✗ ABSENT STUDENTS:')}")
            print(separator("─", 80))
            print(f"{'ID':<10} {'Name'}")
            print(separator("─", 80))
            for student in unmarked_list:
                print(f"{student[0]:<10} {student[1]}")
        else:
            print(f"\n{success('🎉 All students are present!')}")
        
        print(separator("═", 80))

    def _view_attendance_report(self, csv_filename):
        """View attendance report in terminal"""
        attendance_path = self.storage_paths['AttendanceRecords']
        file_path = os.path.join(attendance_path, csv_filename)
        
        all_students = self.get_all_students()
        
        marked_ids = set()
        attendance_records = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader) # skip header
                for row in reader:
                    if row and len(row) >= 4:
                        id_val = str(row[0]).strip().lstrip('0')
                        marked_ids.add(id_val)
                        if len(row) >= 5:
                            # New format: Id,Name,Email,Date,Time
                            attendance_records.append({
                                'id': id_val,
                                'name': row[1].strip(),
                                'email': row[2].strip(),
                                'date': row[3].strip(),
                                'time': row[4].strip()
                            })
                        else:
                            # Old format: Id,Name,Date,Time
                            attendance_records.append({
                                'id': id_val,
                                'name': row[1].strip(),
                                'email': '',
                                'date': row[2].strip(),
                                'time': row[3].strip()
                            })
        except Exception as e:
            print(error(f"✗ Failed to read CSV: {e}"))
            return
        
        marked_list = []
        unmarked_list = []
        
        for student in all_students:
            s_id = str(student['id']).strip().lstrip('0')  # Remove leading zeros
            row_data = [student['id'], student['name']]
            if s_id in marked_ids:
                marked_list.append(row_data)
            else:
                unmarked_list.append(row_data)
        
        # Show preview in terminal
        self._show_attendance_preview(csv_filename, marked_list, unmarked_list, attendance_records)

    def _export_attendance_pdf(self, csv_filename):
        """Generates a PDF format with Marked & Unmarked students"""
        print(info(f"⏳ Generating PDF for {csv_filename}..."))
        
        attendance_path = self.storage_paths['AttendanceRecords']
        file_path = os.path.join(attendance_path, csv_filename)
        pdf_filename = csv_filename.replace('.csv', '_Report.pdf')
        pdf_path = os.path.join(attendance_path, pdf_filename)
        
        all_students = self.get_all_students()
        
        marked_ids = set()
        attendance_records = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader) # skip header
                for row in reader:
                    if row and len(row) >= 4:
                        id_val = str(row[0]).strip().lstrip('0')
                        marked_ids.add(id_val)
                        if len(row) >= 5:
                            # New format: Id,Name,Email,Date,Time
                            attendance_records.append({
                                'id': id_val,
                                'name': row[1].strip(),
                                'email': row[2].strip(),
                                'date': row[3].strip(),
                                'time': row[4].strip()
                            })
                        else:
                            # Old format: Id,Name,Date,Time
                            attendance_records.append({
                                'id': id_val,
                                'name': row[1].strip(),
                                'email': '',
                                'date': row[2].strip(),
                                'time': row[3].strip()
                            })
        except Exception as e:
            print(error(f"✗ Failed to read CSV: {e}"))
            return
        
        print(f"\n🔍 Debug Info:")
        print(f"   Students in database: {len(all_students)}")
        for student in all_students:
            print(f"     - ID: '{student['id']}' Name: '{student['name']}'")
        print(f"   Marked IDs from attendance: {len(marked_ids)}")
        for mid in marked_ids:
            print(f"     - ID: '{mid}'")
        print(f"   Attendance records: {len(attendance_records)}")
        for record in attendance_records:
            print(f"     - {record['id']}: {record['name']} at {record['time']}")
            
        marked_list = []
        unmarked_list = []
        
        for student in all_students:
            s_id = str(student['id']).strip().lstrip('0')  # Remove leading zeros
            row_data = [student['id'], student['name']]
            if s_id in marked_ids:
                marked_list.append(row_data)
            else:
                unmarked_list.append(row_data)
        
        # Show preview in terminal
        self._show_attendance_preview(csv_filename, marked_list, unmarked_list, attendance_records)
        
        # Ask for confirmation before generating PDF
        confirm = input(f"\n{info('➤')} Generate PDF report? (Y/N): ").strip().upper()
        if confirm != 'Y':
            print(info("PDF generation cancelled."))
            return
        
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            elements = []
            styles = getSampleStyleSheet()
            
            # --- ELEGANT HEADER ---
            title_style = styles['Heading1']
            title_style.textColor = colors.HexColor("#1A237E") # Dark Indigo
            title_style.alignment = 1 # Center
            title_style.fontSize = 22
            title_style.spaceAfter = 10
            
            sub_style = styles['Normal']
            sub_style.alignment = 1
            sub_style.textColor = colors.HexColor("#546E7A")
            sub_style.fontSize = 12
            
            elements.append(Paragraph("<b>SMART ATTENDANCE REPORT</b>", title_style))
            elements.append(Paragraph(f"Session Log: {csv_filename.replace('.csv', '')} | E2C TEAM", sub_style))
            elements.append(Spacer(1, 20))
            
            # --- SUMMARY METRICS ---
            total = len(marked_list) + len(unmarked_list)
            summary_data = [
                ['Total Enrolled', 'Present (Marked)', 'Absent (Unmarked)'],
                [str(total), str(len(marked_list)), str(len(unmarked_list))]
            ]
            summary_table = Table(summary_data, colWidths=[150, 150, 150])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3F51B5")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E8EAF6")),
                ('FONTSIZE', (0, 1), (-1, -1), 16),
                ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor("#2E7D32")), # Green for present
                ('TEXTCOLOR', (2, 1), (2, 1), colors.HexColor("#C62828")), # Red for absent
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 15),
                ('TOPPADDING', (0, 1), (-1, -1), 15),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#283593")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.white)
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 30))
            
            # Helper to generate alternating row colors
            def get_data_table_style(header_bg, is_empty):
                style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_bg)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor("#212121")),
                ]
                if not is_empty:
                    style.extend([
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.lightgrey),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ])
                return TableStyle(style)

            # --- MARKED TABLE ---
            elements.append(Paragraph("<b>✓ MARKED STUDENTS (PRESENT)</b>", styles['Heading2']))
            elements.append(Spacer(1, 5))
            if marked_list:
                m_data = [['Student ID', 'Student Name']] + marked_list
                m_table = Table(m_data, colWidths=[150, 300])
                m_table.setStyle(get_data_table_style("#4CAF50", False))
                elements.append(m_table)
            else:
                elements.append(Paragraph("<i>No students were recognized in this session.</i>", styles['Normal']))
                
            elements.append(Spacer(1, 25))
            
            # --- UNMARKED TABLE ---
            elements.append(Paragraph("<b>✗ UNMARKED STUDENTS (ABSENT)</b>", styles['Heading2']))
            elements.append(Spacer(1, 5))
            if unmarked_list:
                u_data = [['Student ID', 'Student Name']] + unmarked_list
                u_table = Table(u_data, colWidths=[150, 300])
                u_table.setStyle(get_data_table_style("#F44336", False))
                elements.append(u_table)
            else:
                elements.append(Paragraph("<i>All registered students were present! Outstanding!</i>", styles['Normal']))
                
            # --- FOOTER ---
            elements.append(Spacer(1, 40))
            footer = Paragraph(f"<font color='#9E9E9E' size='9'>Report auto-generated by the E2C Smart Attendance Engine on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.</font>", sub_style)
            elements.append(footer)

            doc.build(elements)
            print(success(f"✓ Beautiful PDF successfully exported to:\n  {pdf_path}"))
            
        except Exception as e:
            print(error(f"✗ Failed to generate beautiful PDF: {e}"))

