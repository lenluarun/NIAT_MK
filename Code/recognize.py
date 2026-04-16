import datetime
import os
import time
import cv2
import pandas as pd
import numpy as np
from colors import Colors
import ui_console


def recognize_attendence(storage_paths=None, data_manager=None, camera_index=0, pass_mark=45, fast_mode=True):
    recognizer = cv2.face.LBPHFaceRecognizer_create()  
    trained_dir = storage_paths.get('TrainedModels') if storage_paths else "TrainingImageLabel"
    recognizer.read(os.path.join(trained_dir, "Trainner.yml"))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    harcascadePath = os.path.join(base_dir, "haarcascade_default.xml")
    if not os.path.exists(harcascadePath):
        harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    student_file = data_manager.student_file if data_manager else "StudentDetails" + os.sep + "StudentDetails.csv"

    # Read student file forcing Id to be string to ensure consistent comparisons
    try:
        df = pd.read_csv(student_file, dtype={'Id': str})
    except Exception:
        # Fallback: read normally
        df = pd.read_csv(student_file)

    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)

    # start realtime video capture
    cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    cam.set(3, 640) 
    cam.set(4, 480) 
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    try:
        while True:
            ret, im = cam.read()
            if not ret or im is None:
                print("✗ Failed to read frame from camera. Stopping recognition.")
                break
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5,
                    minSize = (int(minW), int(minH)),flags = cv2.CASCADE_SCALE_IMAGE)
            for(x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x+w, y+h), (10, 159, 255), 2)
                Id, conf = recognizer.predict(gray[y:y+h, x:x+w])

                # Normalize ID and prepare confidence text
                confstr = "  {0}%".format(round(100 - conf))
                Id_str = str(Id).strip()

                # Lookup name safely
                name_vals = df.loc[df['Id'] == Id_str]['Name'].values
                name = name_vals[0] if len(name_vals) > 0 else ''

                if conf < 100:
                    tt = f"{Id_str}-{name}" if name else Id_str
                else:
                    Id_str = 'Unknown'
                    name = ''
                    tt = Id_str

                # Mark attendance only when pass threshold is met
                if (100-conf) >= pass_mark:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    # Ensure we write string ID (matching StudentDetails format)
                    attendance.loc[len(attendance)] = [Id_str, name, date, timeStamp]

                tt = str(tt)
                if(100-conf) >= pass_mark:
                    tt = tt + " [Pass]"
                    cv2.putText(im, str(tt), (x+5,y-5), font, 1, (255, 255, 255), 2)
                else:
                    cv2.putText(im, str(tt), (x + 5, y - 5), font, 1, (255, 255, 255), 2)

                if (100-conf) >= pass_mark:
                    cv2.putText(im, str(confstr), (x + 5, y + h - 5), font,1, (0, 255, 0),1 )
                elif (100-conf) > 50:
                    cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 255), 1)
                else:
                    cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)


            # Deduplicate by string Id
            attendance['Id'] = attendance['Id'].astype(str)
            attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
            cv2.imshow('Attendance', im)
            
            if not attendance.empty:
                break

            if (cv2.waitKey(1) == ord('q')):
                break
    except KeyboardInterrupt:
        print("\n⚠ Recognition interrupted by user (Ctrl+C).")
        
    cam.release()
    cv2.destroyAllWindows()

    if not attendance.empty:
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        att_dir = storage_paths.get('AttendanceRecords') if storage_paths else "Attendance"
        os.makedirs(att_dir, exist_ok=True)
        fileName = os.path.join(att_dir, "Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv")
        attendance.to_csv(fileName, index=False)
        
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
        print(f"  {Colors.BRIGHT_WHITE}User ID Recognized & Logged Successfully.{Colors.RESET}")
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
