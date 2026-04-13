import datetime
import os
import time
import cv2
import pandas as pd
from colors import success, error, info, bold, separator


def print_header(title):
    """Print stylish header"""
    print("\n" + separator("═", 60))
    print(f"  {title}")
    print(separator("═", 60))


def recognize_attendence(storage_paths, data_manager):
    print_header("✓ ATTENDANCE RECOGNITION - Starting")
    print(f"\n  {info('⏳')} Loading model and student data...\n")
    
    model_path = os.path.join(storage_paths['TrainedModels'], 'Trainner.yml')
    
    if not os.path.exists(model_path):
        print(error("✗ Trained model not found!"))
        print(error("✗ Please train the model first.\n"))
        return
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()  
    recognizer.read(model_path)
    harcascadePath = "haarcascade_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    df = pd.read_csv(data_manager.student_file)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)

    print(f"  {success('✓')} Model loaded successfully")
    print(f"  {success('✓')} Student database loaded")
    print(f"  {info('💡')} Press 'Q' to stop and save attendance\n")
    
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640) 
    cam.set(4, 480) 
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    while True:
        ret, im = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5,
                minSize = (int(minW), int(minH)),flags = cv2.CASCADE_SCALE_IMAGE)
        for(x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (0, 255, 0), 2)
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            if conf < 100:
                try:
                    aa = df.loc[df['Id'] == Id]['Name'].values
                    confstr = "  {0}%".format(round(100 - conf))
                    tt = str(Id)+"-"+str(aa[0]) if len(aa) > 0 else "Unknown"
                except:
                    tt = "Unknown"
                    confstr = "  {0}%".format(round(100 - conf))
            else:
                Id = '  Unknown  '
                tt = str(Id)
                confstr = "  {0}%".format(round(100 - conf))

            if (100-conf) > 67:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                try:
                    aa = str(aa[0]) if len(aa) > 0 else "Unknown"
                except:
                    aa = "Unknown"
                attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]

            tt = str(tt)[2:-2] if str(tt) != "Unknown" else tt
            if(100-conf) > 67:
                tt = tt + " [Pass]"
                cv2.putText(im, str(tt), (x+5,y-5), font, 1, (0, 255, 0), 2)
            else:
                cv2.putText(im, str(tt), (x + 5, y - 5), font, 1, (255, 255, 255), 2)

            if (100-conf) > 67:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 0), 1)
            elif (100-conf) > 50:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 255), 1)
            else:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)


        attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
        cv2.putText(im, "E2C TEAM - Attendance System (Offline Mode)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(im, f"Students Marked: {len(attendance)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.imshow('Attendance System - Press Q to Exit', im)
        if (cv2.waitKey(1) == ord('q')):
            break
    
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    attendance_file = f"Attendance_{date}_{Hour}-{Minute}-{Second}.csv"
    file_path = os.path.join(storage_paths['AttendanceRecords'], attendance_file)
    attendance.to_csv(file_path, index=False)
    
    print("\n" + separator("═", 60))
    print(f"  {success('✓')} ATTENDANCE SAVED SUCCESSFULLY")
    print(separator("═", 60))
    print(f"\n  {success('✓')} Total Students Marked: {bold(len(attendance))}")
    print(f"  {success('✓')} File: {bold(attendance_file)}")
    print(f"  {success('✓')} Date: {bold(date)}")
    print(f"  {success('✓')} Time: {bold(timeStamp)}")
    print(f"  {info('📁')} Path: {bold(file_path)}")
    print(f"  {separator('═', 60)}\n")
    
    cam.release()
    cv2.destroyAllWindows()