"""
Data manager for student records and attendance operations
"""
import os
import csv
import json
from datetime import datetime
from colors import success, error, warning, info, bold, separator


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
                    if row:
                        students.append({
                            'id': row[0],
                            'name': row[1],
                            'email': row[2] if len(row) > 2 else '',
                            'date_added': row[3] if len(row) > 3 else ''
                        })
        except:
            pass
        return students
    
    def delete_student(self, student_id):
        """Delete a student"""
        try:
            students = self.get_all_students()
            with open(self.student_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Id', 'Name', 'Email', 'DateAdded'])
                for student in students:
                    if student['id'] != str(student_id):
                        writer.writerow([student['id'], student['name'], student['email'], student['date_added']])
            return True
        except:
            return False
    
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
        """Generate attendance report"""
        os.system('cls')
        print("\n")
        print(bold("═" * 80))
        print(bold(f"\n  📈 ATTENDANCE REPORT\n"))
        print(bold("═" * 80))
        
        attendance_path = self.storage_paths['AttendanceRecords']
        attendance_files = [f for f in os.listdir(attendance_path) if f.endswith('.csv')]
        
        if not attendance_files:
            print(warning("⚠ No attendance records found!"))
            return
        
        total_records = 0
        for file in sorted(attendance_files, reverse=True)[:10]:
            try:
                with open(os.path.join(attendance_path, file), 'r') as f:
                    records = len(f.readlines()) - 1
                    total_records += records
                    print(f"\n{info(f'📄 {file}')}: {bold(str(records))} records")
            except:
                pass
        
        print(f"\n{separator('─', 80)}")
        print(f"\n{success(f'✓ Total Attendance Records: {total_records}')}\n")
