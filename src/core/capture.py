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
    training_dir = None
    student_csv_dir = None
    if isinstance(storage_paths, dict):
        training_dir = storage_paths.get('TrainingImages') or storage_paths.get('TrainingImage')
        student_csv_dir = storage_paths.get('StudentDetails') or storage_paths.get('StudentData')

    if not training_dir:
        raise ValueError("storage_paths must contain 'TrainingImages' path")

    # Ask for user inputs
    Id = input("Enter Your Id: ").strip()
    name = input("Enter Your Name: ").strip()

    valid_name = all(part.isalpha() for part in name.split())
    if not (is_number(Id) and valid_name):
        if not is_number(Id):
            print("Enter Numeric ID")
        if not valid_name:
            print("Enter Alphabetical Name")
        return

    # Check if student exists in database
    student_exists = False
    if data_manager is not None:
        student_exists = data_manager.student_exists(str(Id))
    else:
        # Check CSV directly
        student_csv_file = os.path.join(student_csv_dir or base_dir, "StudentDetails.csv")
        if os.path.exists(student_csv_file):
            try:
                with open(student_csv_file, 'r') as csvFile:
                    reader = csv.reader(csvFile)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if row and str(row[0]).strip() == str(Id):
                            student_exists = True
                            break
            except Exception:
                pass

    if not student_exists:
        print(f"✗ Student with ID {Id} does not exist in the database.")
        print("Please add the student first using the Data Management menu.")
        return

    print(f"✓ Student found: {name} (ID: {Id})")
    print("Starting face capture...")

    cam = cv2.VideoCapture(int(camera_index))
    if not cam.isOpened():
        print(f"✗ Failed to open camera at index {camera_index}")
        return

    # Haarcascade path: prefer the one bundled in project folder
    base_dir = os.path.dirname(__file__)
    cascade_path = os.path.join(base_dir, "..", "models", "haarcascade_default.xml")
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
            cv2.putText(img, f"Samples: {sampleNum}/{max_samples}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('frame', img)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (10, 159, 255), 2)
                sampleNum += 1
                filename = f"{name}.{Id}.{sampleNum}.jpg"
                filepath = os.path.join(training_dir, filename)
                cv2.imwrite(filepath, gray[y:y + h, x:x + w])
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

    # Save student details (only if not already exists)
    try:
        if data_manager is not None:
            # Check if student already exists before adding
            if not data_manager.student_exists(str(Id)):
                data_manager.add_student(str(Id), name)
        else:
            # Check CSV before appending
            exists_in_csv = False
            if os.path.exists(student_csv_file):
                try:
                    with open(student_csv_file, 'r') as csvFile:
                        reader = csv.reader(csvFile)
                        next(reader, None)  # Skip header
                        for row in reader:
                            if row and str(row[0]).strip() == str(Id):
                                exists_in_csv = True
                                break
                except Exception:
                    pass
            if not exists_in_csv:
                with open(student_csv_file, 'a+', newline='') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow([Id, name])
    except Exception as e:
        print(f"⚠ Failed to record student details: {e}")

    print(f"Images Saved for ID : {Id} Name : {name}")
