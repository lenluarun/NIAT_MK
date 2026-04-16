import csv
import cv2
import os
import time


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def takeImages(storage_paths, data_manager=None, camera_index=0, max_samples=100):
    """
    Capture face images from a camera and save into storage_paths['TrainingImages'].
    Parameters:
      storage_paths: dict with folder paths (expects keys 'TrainingImages' and 'StudentDetails')
      data_manager: optional DataManager instance to register student (if provided)
      camera_index: integer camera index to open with OpenCV
      max_samples: maximum number of face samples to capture
    """
    # Validate storage_paths
    training_dir = storage_paths.get('TrainingImages') if isinstance(storage_paths, dict) else None
    student_csv_dir = storage_paths.get('StudentDetails') if isinstance(storage_paths, dict) else None

    if not training_dir:
        raise ValueError("storage_paths must contain 'TrainingImages' path")

    # Ask for user inputs
    Id = input("Enter Your Id: ").strip()
    name = input("Enter Your Name: ").strip()

    if not (is_number(Id) and name.isalpha()):
        if not is_number(Id):
            print("Enter Numeric ID")
        if not name.isalpha():
            print("Enter Alphabetical Name")
        return

    cam = cv2.VideoCapture(int(camera_index))
    if not cam.isOpened():
        print(f"✗ Failed to open camera at index {camera_index}")
        return

    # Haarcascade path: prefer the one bundled in project folder
    base_dir = os.path.dirname(__file__)
    cascade_path = os.path.join(base_dir, "haarcascade_default.xml")
    if not os.path.exists(cascade_path):
        # fallback to OpenCV default cascade location (if available)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

    detector = cv2.CascadeClassifier(cascade_path)
    sampleNum = 0

    # Ensure training directory exists
    os.makedirs(training_dir, exist_ok=True)
    # Ensure student details dir exists and CSV file available
    if student_csv_dir:
        os.makedirs(student_csv_dir, exist_ok=True)
    student_csv_file = os.path.join(student_csv_dir or base_dir, "StudentDetails.csv")

    try:
        while True:
            ret, img = cam.read()
            if not ret or img is None:
                print("✗ Failed to read frame from camera. Stopping capture.")
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (10, 159, 255), 2)
                sampleNum += 1
                filename = f"{name}.{Id}.{sampleNum}.jpg"
                filepath = os.path.join(training_dir, filename)
                cv2.imwrite(filepath, gray[y:y + h, x:x + w])
                cv2.imshow('frame', img)
            # Break conditions
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            if sampleNum >= int(max_samples):
                break
    except KeyboardInterrupt:
        print("\n⚠ Face capture interrupted by user (Ctrl+C).")
    finally:
        # release resources
        cam.release()
        cv2.destroyAllWindows()

    # Save student details
    try:
        if data_manager is not None:
            # Attempt to use data_manager API if available
            try:
                data_manager.add_student(str(Id), name)
            except Exception:
                # fallback to CSV append
                with open(student_csv_file, 'a+', newline='') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow([Id, name])
        else:
            with open(student_csv_file, 'a+', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow([Id, name])
    except Exception as e:
        print(f"⚠ Failed to record student details: {e}")

    print(f"Images Saved for ID : {Id} Name : {name}")
