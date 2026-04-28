import datetime
import os
import time
import cv2
import pandas as pd
import numpy as np
from ..utils.colors import Colors
from ..utils import ui as ui_console
import pyfiglet


def get_student_image_path(training_dir, student_id):
    """Find and return path to one image of the matched student"""
    if not os.path.exists(training_dir):
        return None
    
    # Look for files matching pattern *.{student_id}.*.jpg
    for filename in os.listdir(training_dir):
        if filename.endswith('.jpg'):
            parts = filename.split('.')
            if len(parts) >= 3 and parts[-2] == str(student_id):
                return os.path.join(training_dir, filename)
    return None


def recognize_attendence(storage_paths=None, data_manager=None, camera_index=0, pass_mark=80, fast_mode=True):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    trained_dir = storage_paths.get('TrainedModels') if storage_paths else "TrainingImageLabel"
    trainer_path = os.path.join(trained_dir, "Trainner.yml")

    # Check if trained model exists
    if not os.path.exists(trainer_path):
        ui_console.clear_screen()
        print(f"{Colors.BRIGHT_RED}✗ NO TRAINED MODEL FOUND{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'═' * 50}{Colors.RESET}")
        print(f"  {Colors.BRIGHT_WHITE}Error:{Colors.RESET} {Colors.BRIGHT_YELLOW}Trainner.yml not found{Colors.RESET}")
        print(f"  {Colors.BRIGHT_WHITE}Path:{Colors.RESET} {Colors.BRIGHT_YELLOW}{trainer_path}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'═' * 50}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Please train the model first by capturing faces and training images.{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Use options [2] Capture Faces and [3] Train Images from the main menu.{Colors.RESET}")
        return

    recognizer.read(trainer_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    harcascadePath = os.path.join(base_dir, "haarcascade_default.xml")
    if not os.path.exists(harcascadePath):
        harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    student_file = data_manager.student_file if data_manager else "StudentDetails" + os.sep + "StudentDetails.csv"
    training_dir = storage_paths.get('TrainingImages') if storage_paths else "TrainingImage"

    # Read student file forcing Id to be string to ensure consistent comparisons
    try:
        df = pd.read_csv(student_file, dtype={'Id': str})
    except Exception:
        # Fallback: read normally
        df = pd.read_csv(student_file)

    # Create fast lookup dictionary for student details (optimization)
    student_lookup = {}
    for _, row in df.iterrows():
        id_key = str(row['Id']).strip().lstrip('0')  # Remove leading zeros for matching
        student_lookup[id_key] = {
            'name': str(row['Name']).strip() if 'Name' in row else '',
            'email': str(row['Email']).strip() if 'Email' in row else '',
            'date_added': str(row.get('DateAdded', '')).strip()
        }

    # Cache for figlet text to avoid regenerating (optimization)
    figlet_cache = {}

    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Email', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)

    # Track present students for real-time display
    present_students = {}  # id -> {'name': name, 'time': time, 'confidence': conf}
    auto_exit_after_mark = True  # Exit automatically after marking first student
    exit_recognition = False  # Flag to exit the recognition loop

    # start realtime video capture with optimized settings
    cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    # Optimize camera settings for speed
    cam.set(3, 640)  # Width
    cam.set(4, 480)  # Height
    cam.set(cv2.CAP_PROP_FPS, 60)  # Higher frame rate for faster processing
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer

    minW = 0.1 * cam.get(3)  # Reduced min size for faster detection
    minH = 0.1 * cam.get(4)

    # Performance optimization variables
    frame_count = 0
    process_every_n_frames = 1  # Process every frame for immediate recognition
    last_display_update = 0
    display_update_interval = 0.1  # Update display every 0.1 seconds for faster feedback

    # Show recognition status header
    ui_console.clear_screen()
    print(f"{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET}{Colors.BRIGHT_WHITE}                    FACE RECOGNITION IN PROGRESS{Colors.RESET}{Colors.BRIGHT_CYAN}                      ║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}Camera: {camera_index} | Confidence Threshold: {pass_mark} | Fast Mode: {fast_mode} | Immediate Marking | Auto-Exit: {auto_exit_after_mark}{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}Press 'Q' in video window to save & exit{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}{'─' * 80}{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}Recognition started... Looking for faces...{Colors.RESET}\n")

    start_time = time.time()
    faces_detected_count = 0

    try:
        while True:
            ret, im = cam.read()
            if not ret or im is None:
                print("✗ Failed to read frame from camera. Stopping recognition.")
                break

            frame_count += 1

            # Skip frames for better performance (process every Nth frame)
            if frame_count % process_every_n_frames != 0:
                # Still show the video feed but skip heavy processing
                cv2.putText(im, "Fast Mode Active", (10, 30), font, 0.6, (0, 255, 0), 2)
                cv2.imshow('Attendance', im)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print(f"\n✓ Saving attendance for {len(attendance)} students...")
                    break
                continue

            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

            # Optimized face detection with faster parameters
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.4,  # Increased for speed (was 1.3)
                minNeighbors=2,   # Reduced for speed (was 3)
                minSize=(int(minW), int(minH)),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) > 0:
                faces_detected_count += len(faces)

            current_time = time.time()

            for(x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x+w, y+h), (10, 159, 255), 2)
                Id, conf = recognizer.predict(gray[y:y+h, x:x+w])

                # Normalize ID and prepare confidence text
                confidence_score = round(100 - min(conf, 100))
                confstr = f"  {confidence_score}%"
                Id_str = str(Id).strip().lstrip('0')  # Remove leading zeros

                # Fast dictionary lookup instead of pandas query (optimization)
                student_details = student_lookup.get(Id_str, {'name': '', 'email': '', 'date_added': ''})
                name = student_details['name']

                # Set display text based on confidence level
                if conf < pass_mark:
                    tt = f"Roll: {Id_str} Name: {name}"
                elif conf < 100:
                    tt = f"Low confidence: {Id_str}"
                else:
                    tt = "Unknown"

                # Mark attendance only when confidence is below threshold and name exists
                if conf < pass_mark and name and Id_str not in present_students:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    attendance.loc[len(attendance)] = [Id_str, name, student_details['email'], date, timeStamp]

                    present_students[Id_str] = {
                        'name': name,
                        'email': student_details['email'],
                        'time': timeStamp,
                        'confidence': conf
                    }

                    if auto_exit_after_mark:
                        exit_recognition = True
                        print(f"\n{Colors.BRIGHT_GREEN}✓ STUDENT MARKED - EXITING RECOGNITION{Colors.RESET}")
                        break

                    # Show matched student's image (only for new recognitions and not too frequently)
                    if current_time - last_display_update > display_update_interval:
                        student_image_path = get_student_image_path(training_dir, Id_str)
                        if student_image_path:
                            try:
                                student_img = cv2.imread(student_image_path)
                                if student_img is not None:
                                    # Quick resize without complex logic
                                    resized_img = cv2.resize(student_img, (200, 200))
                                    cv2.putText(resized_img, f"Matched: {name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                                    cv2.putText(resized_img, f"ID: {Id_str}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                                    cv2.imshow(f'Matched-{name}', resized_img)
                            except:
                                pass  # Skip if image loading fails

                        # Display student name in cached figlet text (optimization)
                        if name not in figlet_cache:
                            figlet_cache[name] = pyfiglet.figlet_format(name, font="small")  # Use smaller font for speed
                        print(f"\n{Colors.BRIGHT_MAGENTA}{figlet_cache[name]}{Colors.RESET}")

                        print(f"\n{Colors.BRIGHT_GREEN}✓ STUDENT RECOGNIZED & MARKED PRESENT{Colors.RESET}")
                        print(f"{Colors.BRIGHT_CYAN}{'═' * 50}{Colors.RESET}")
                        print(f"  {Colors.BRIGHT_WHITE}ID:{Colors.RESET} {Colors.BRIGHT_YELLOW}{Id_str}{Colors.RESET}")
                        print(f"  {Colors.BRIGHT_WHITE}Name:{Colors.RESET} {Colors.BRIGHT_YELLOW}{name}{Colors.RESET}")
                        if student_details['email']:
                            print(f"  {Colors.BRIGHT_WHITE}Email:{Colors.RESET} {Colors.BRIGHT_YELLOW}{student_details['email']}{Colors.RESET}")
                        print(f"  {Colors.BRIGHT_WHITE}Time:{Colors.RESET} {Colors.BRIGHT_YELLOW}{timeStamp}{Colors.RESET}")
                        print(f"  {Colors.BRIGHT_WHITE}Confidence:{Colors.RESET} {Colors.BRIGHT_YELLOW}{conf:.1f}{Colors.RESET}")
                        print(f"{Colors.BRIGHT_CYAN}{'═' * 50}{Colors.RESET}")
                        print(f"{Colors.BRIGHT_GREEN}Total Present: {len(present_students)} students{Colors.RESET}\n")

                        last_display_update = current_time

                tt = str(tt)
                cv2.putText(im, str(tt), (x+5,y-5), font, 1, (255, 255, 255), 2)

                if conf < 100:  # Only show confidence for recognized faces
                    if conf < pass_mark:  # Lower conf = better match
                        cv2.putText(im, str(confstr), (x + 5, y + h - 5), font,1, (0, 255, 0),1 )
                    elif conf < pass_mark * 2:  # Medium confidence
                        cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 255), 1)
                    else:
                        cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)

            # Deduplicate by string Id
            attendance['Id'] = attendance['Id'].astype(str)
            attendance = attendance.drop_duplicates(subset=['Id'], keep='first')

            # Display present students list in video frame (optimized - show less frequently)
            if frame_count % 10 == 0:  # Update every 10 processed frames
                y_offset = 60  # Start below the instructions
                if present_students:
                    cv2.putText(im, "PRESENT STUDENTS:", (10, y_offset), font, 0.6, (0, 255, 0), 2)
                    y_offset += 25

                    # Show up to 5 students in the video frame (reduced for performance)
                    for i, (student_id, details) in enumerate(list(present_students.items())[:5]):
                        student_text = f"{student_id}: {details['name']}"
                        cv2.putText(im, student_text, (10, y_offset), font, 0.5, (255, 255, 255), 1)
                        y_offset += 20

                    if len(present_students) > 5:
                        cv2.putText(im, f"... and {len(present_students) - 5} more", (10, y_offset), font, 0.5, (255, 255, 255), 1)
                else:
                    cv2.putText(im, "No students present yet", (10, y_offset), font, 0.6, (255, 255, 0), 2)

            # Show attendance count and instructions (optimized - update less frequently)
            if frame_count % 5 == 0:  # Update every 5 processed frames
                attendance_count = len(attendance)
                elapsed_time = int(time.time() - start_time)

                status_text = f"Present: {attendance_count} | Faces: {faces_detected_count} | Elapsed: {elapsed_time}s"
                cv2.putText(im, status_text, (10, 30), font, 0.6, (255, 255, 255), 2)
            cv2.putText(im, "Press 'Q' to save & exit (Auto-exit after mark)", (10, 50), font, 0.5, (255, 255, 255), 1)

            cv2.imshow('Attendance', im)

            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or exit_recognition:
                print(f"\n✓ Saving attendance for {len(attendance)} students...")
                break
    except KeyboardInterrupt:
        print("\n⚠ Recognition interrupted by user (Ctrl+C).")

    cam.release()
    cv2.destroyAllWindows()

    if not attendance.empty:
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        att_dir = storage_paths.get('AttendanceRecords') if storage_paths else "Attendance"
        os.makedirs(att_dir, exist_ok=True)
        fileName = os.path.join(att_dir, f"Attendance_{date}.csv")

        # Check if file exists and append, otherwise create new
        if os.path.exists(fileName):
            # Read existing attendance to avoid duplicates
            existing_df = pd.read_csv(fileName, dtype={'Id': str})
            # Combine and remove duplicates based on Id
            combined_df = pd.concat([existing_df, attendance], ignore_index=True)
            combined_df['Id'] = combined_df['Id'].astype(str)
            combined_df = combined_df.drop_duplicates(subset=['Id'], keep='last')  # Keep latest entry
            combined_df.to_csv(fileName, index=False)
        else:
            attendance.to_csv(fileName, index=False)

        print(f"\n📊 Attendance Summary:")
        print(f"   Total students marked: {len(attendance)}")
        print(f"\n{Colors.BRIGHT_GREEN}✓ PRESENT STUDENTS LIST:{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}")
        for student_id, details in present_students.items():
            email_str = f" ({details['email']})" if details.get('email') else ""
            print(f"   {Colors.BRIGHT_YELLOW}{student_id:<10}{Colors.RESET} {Colors.BRIGHT_WHITE}{details['name']:<20}{Colors.RESET}{Colors.BRIGHT_MAGENTA}{email_str:<25}{Colors.RESET} {Colors.BRIGHT_CYAN}{details['time']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}")
        print(f"   Saved to: {fileName}")

        ui_console.clear_screen()
        print(f"{Colors.BRIGHT_GREEN}")
        print("  ┏" + "━" * 68 + "┓")
        print("  ┃" + " " * 27 + "ATTENDANCE SAVED" + " " * 25 + "┃")
        print("  ┗" + "━" * 68 + "┛\n")
        print(r"""
     __  __    _    ____  _  _______ ____
    |  \/  |  / \  |  _ \| |/ / ____|  _ \
    | |\/| | / _ \ | |_) | ' /|  _| | | | |
    | |  | |/ ___ \|  _ <| . \| |___| |_| |
    |_|  |_/_/   \_\_| \_\_|\_\_____|____/
""")
        print(f"{Colors.RESET}")
        if present_students:
            names = [details['name'] for details in present_students.values()]
            names_str = ", ".join(names)
            print(f"  {Colors.BRIGHT_WHITE}{names_str} - Recognized & Attendance Logged Successfully.{Colors.RESET}")
        else:
            print(f"  {Colors.BRIGHT_WHITE}No user was recognized. Please try again.{Colors.RESET}")
    else:
        ui_console.clear_screen()
        print(f"{Colors.BRIGHT_RED}")
        print("  ┏" + "━" * 68 + "┓")
        print("  ┃" + " " * 26 + "ATTENDANCE FAILED" + " " * 25 + "┃")
        print("  ┗" + "━" * 68 + "┛\n")
        print(r"""
     _   _  ___ _____   __  __    _    ____  _  _______ ____
    | \ | |/ _ \_   _| |  \/  |  / \  |  _ \| |/ / ____|  _ \
    |  \| | | | || |   | |\/| | / _ \ | |_) | ' /|  _| | | | |
    | |\  | |_| || |   | |  | |/ ___ \|  _ <| . \| |___| |_| |
    |_| \_|\___/ |_|   |_|  |_/_/   \_\_| \_\_|\_\_____|____/
""")
        print(f"{Colors.RESET}")
        print(f"  {Colors.BRIGHT_WHITE}No user was recognized. Please try again.{Colors.RESET}")
