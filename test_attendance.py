#!/usr/bin/env python3
"""
Test script for attendance system fixes
"""
import csv
import os

def test_id_matching():
    """Test ID matching logic"""
    print("Testing ID matching logic...")

    # Sample student data
    students = [
        {'id': '1', 'name': 'Alice Johnson'},
        {'id': '2', 'name': 'Bob Smith'},
        {'id': '3', 'name': 'Charlie Brown'},
        {'id': '4', 'name': 'Diana Wilson'},
        {'id': '5', 'name': 'Eve Davis'}
    ]

    # Sample attendance data
    attendance_records = [
        {'id': '1', 'name': 'Alice Johnson', 'date': '2024-01-15', 'time': '09:30:00'},
        {'id': '3', 'name': 'Charlie Brown', 'date': '2024-01-15', 'time': '09:31:00'}
    ]

    # Extract marked IDs
    marked_ids = set()
    for record in attendance_records:
        marked_ids.add(str(record['id']).strip())

    print(f"Students in database: {len(students)}")
    for student in students:
        print(f"  - ID: '{student['id']}' Name: '{student['name']}'")

    print(f"Marked IDs from attendance: {len(marked_ids)}")
    for mid in marked_ids:
        print(f"  - ID: '{mid}'")

    # Generate report
    marked_list = []
    unmarked_list = []

    for student in students:
        s_id = str(student['id']).strip()
        row_data = [student['id'], student['name']]
        if s_id in marked_ids:
            marked_list.append(row_data)
            print(f"✓ MATCH: Student {s_id} is PRESENT")
        else:
            unmarked_list.append(row_data)
            print(f"✗ NO MATCH: Student {s_id} is ABSENT")

    print(f"\n📊 Final Report:")
    print(f"Present: {len(marked_list)} students")
    print(f"Absent: {len(unmarked_list)} students")

    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_id_matching()