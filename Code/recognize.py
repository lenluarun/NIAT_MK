import datetime
import os
import time
import cv2
import pandas as pd
import signal
import sys
from colors import success, error, info, bold, separator, warning

# Global flag for graceful shutdown
should_exit = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global should_exit
    should_exit = True
    print(f"\n\n{info('⏳')} Shutting down gracefully...")

signal.signal(signal.SIGINT, signal_handler)


def print_header(title):
    """Print stylish header"""
    print("\n" + separator("═", 60))
    print(f"  {title}")
    print(separator("═", 60))


def recognize_attendence(storage_paths, data_manager, camera_index=0, pass_mark=67):
    global should_exit
    should_exit = False
    
    print_header("✓ ATTENDANCE RECOGNITION - Starting")
    print(f"\n  {info('⏳')} Loading model and student data...\n")
    
    model_path = os.path.join(storage_paths['TrainedModels'], 'Trainner.yml')
    
    if not os.path.exists(model_path):
        print(error("✗ Trained model not found!"))
        print(error("✗ Please train the model first.\n"))
        return
    
    # Use tuned LBPH parameters for better accuracy and consistency
    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=16, grid_x=8, grid_y=8)
    recognizer.read(model_path)
    
    # Get absolute path to cascade classifier
    cascade_dir = os.path.dirname(os.path.abspath(__file__))
    harcascadePath = os.path.join(cascade_dir, "haarcascade_default.xml")
    
    if not os.path.exists(harcascadePath):
        print(error(f"✗ Cascade classifier not found at: {harcascadePath}"))
        return
    
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    
    # Verify cascade classifier loaded successfully
    if faceCascade.empty():
        print(error("✗ Failed to load cascade classifier!"))
        print(error(f"✗ Check file exists: {harcascadePath}"))
        return
    
    df = pd.read_csv(data_manager.student_file)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)

    print(f"  {success('✓')} Model loaded successfully")
    print(f"  {success('✓')} Student database loaded")
    print(f"  {info('💡')} Press 'Q' to stop and save attendance\n")
    
    cam = None
    try:
        cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cam.isOpened():
            print(error(f"✗ Cannot open camera index {camera_index}!"))
            return
            
        cam.set(3, 640) 
        cam.set(4, 480) 
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)
        frame_count = 0
        last_frame_time = time.time()
        frame_timeout = 5  # Reset timeout every 5 seconds
        
        print(f"{info('▶')} Starting face recognition... (Ctrl+C or press Q to stop)\n")

        while True:
            # Check for graceful shutdown signal
            if should_exit:
                print(f"{info('⏳')} Exit signal received...")
                break
            
            # Timeout protection - if no frames for 5 seconds, something's wrong
            if time.time() - last_frame_time > frame_timeout:
                print(warning("⚠ Camera timeout - no frames received. Restarting..."))
                cam.release()
                time.sleep(1)
                cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
                if not cam.isOpened():
                    print(error("✗ Cannot reconnect to camera!"))
                    break
                last_frame_time = time.time()
                continue
            
            ret, im = cam.read()
            if not ret:
                print(warning("⚠ Failed to read frame from camera"))
                break
            
            last_frame_time = time.time()
            
            # Resize for faster processing
            im = cv2.resize(im, (640, 480))
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization for consistent lighting
            gray = cv2.equalizeHist(gray)
            
            # Optimized cascade parameters (1.1 scale factor, 4 neighbors for better accuracy)
            faces = faceCascade.detectMultiScale(gray, 1.1, 4,
                    minSize = (int(minW), int(minH)), maxSize=(int(minW*5), int(minH*5)), flags = cv2.CASCADE_SCALE_IMAGE)
            for(x, y, w, h) in faces:
                # Extract and equalize face region for better recognition
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.equalizeHist(face_roi)
                
                cv2.rectangle(im, (x, y), (x+w, y+h), (0, 255, 0), 2)
                Id, conf = recognizer.predict(face_roi)
                
                # Lowered threshold from 100 to 85 for LBPH (better for varying lighting)
                if conf < 85:
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

                if (100-conf) > 60:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    try:
                        aa = str(aa[0]) if len(aa) > 0 else "Unknown"
                    except:
                        aa = "Unknown"
                    attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]

                tt = str(tt)[2:-2] if str(tt) != "Unknown" else tt
                if(100-conf) > pass_mark:
                    tt = tt + " [Pass]"
                    cv2.putText(im, str(tt), (x+5,y-5), font, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(im, str(tt), (x + 5, y - 5), font, 1, (255, 255, 255), 2)

                if (100-conf) > pass_mark:
                    cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 0), 1)
                elif (100-conf) > 50:
                    cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 255), 1)
                else:
                    cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)


            # Skip duplicate check every other frame for better performance
            frame_count += 1
            if frame_count % 2 == 0:
                attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
            
            cv2.putText(im, "E2C TEAM - Attendance System (Optimized)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(im, f"Students Marked: {len(attendance)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            cv2.imshow('Attendance System - Press Q to Exit', im)
            
            # Non-blocking keyboard input with timeout
            try:
                key = cv2.waitKey(100) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    break
            except Exception as e:
                print(warning(f"⚠ Keyboard input error: {e}"))
                break
        
        # Save attendance data
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        attendance_file = f"Attendance_{date}_{Hour}-{Minute}-{Second}.csv"
        file_path = os.path.join(storage_paths['AttendanceRecords'], attendance_file)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
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
        
    except KeyboardInterrupt:
        print(f"\n\n{warning('⚠')} Recognition interrupted by user")
        print(f"{info('💾')} Saving attendance records...")
        
        if len(attendance) > 0:
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            Hour, Minute, Second = timeStamp.split(":")
            attendance_file = f"Attendance_{date}_{Hour}-{Minute}-{Second}_interrupted.csv"
            file_path = os.path.join(storage_paths['AttendanceRecords'], attendance_file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            attendance.to_csv(file_path, index=False)
            print(f"{success('✓')} Partial attendance saved: {attendance_file}\n")
        else:
            print(f"{info('ℹ')} No attendance records to save\n")
    
    except Exception as e:
        print(f"\n{error(f'✗ Error during recognition: {str(e)}')}") 
        import traceback
        traceback.print_exc()
    
    finally:
        # Ensure resources are always cleaned up
        if cam is not None:
            try:
                cam.release()
            except:
                pass
        
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        print(f"{success('✓')} Camera and resources released\n")