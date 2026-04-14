import csv
import cv2
import os
from colors import success, error, info, bold, separator, highlight
from ui_console import print_card


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


def print_section(title):
    """Print a stylish section header"""
    print_card(
        title,
        [
            "Collect high-quality face images for model training.",
            "Face should be centered and clearly visible.",
            "Press Q in camera window for manual stop.",
        ],
    )


def takeImages(storage_paths, data_manager, camera_index=0, max_samples=100):
    print_section("📸 CAPTURE FACES - Training Image Collection")
    Id = input(f"\n  {info('➤')} Enter Student ID (Numeric): ")
    name = input(f"  {info('➤')} Enter Student Name (Alphabetic): ")
    email = input(f"  {info('➤')} Enter Email (Optional, press Enter to skip): ")

    if(is_number(Id) and name.isalpha()):
        print(f"\n  {success('✓')} Starting capture for: {bold(name)} (ID: {bold(Id)})")
        print(f"  {info('📷')} Camera Index: {bold(camera_index)}")
        print(f"  {info('🎯')} Target Samples: {bold(max_samples)}")
        print("  Press 'Q' to stop early\n")
        
        cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cam.isOpened():
            print(f"  {error('✗')} Cannot open camera index {camera_index}!")
            return
        
        # Get absolute path to cascade classifier
        cascade_dir = os.path.dirname(os.path.abspath(__file__))
        cascade_path = os.path.join(cascade_dir, "haarcascade_default.xml")
        
        if not os.path.exists(cascade_path):
            print(f"  {error('✗')} Cascade classifier not found at: {cascade_path})")
            return
        
        detector = cv2.CascadeClassifier(cascade_path)
        
        if detector.empty():
            print(f"  {error('✗')} Failed to load cascade classifier!")
            return
        
        sampleNum = 0
        training_path = storage_paths['TrainingImages']

        while(True):
            ret, img = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Optimize cascade parameters for better detection during capture
            faces = detector.detectMultiScale(gray, 1.1, 4, minSize=(30,30), maxSize=(200,200), flags=cv2.CASCADE_SCALE_IMAGE)
            
            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                sampleNum = sampleNum+1
                
                # Extract and equalize face region for better training data quality
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.equalizeHist(face_roi)
                
                cv2.putText(img, f"Samples: {sampleNum}", (x+5, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Save equalized image for better training
                cv2.imwrite(os.path.join(training_path, f"{name}.{Id}.{sampleNum}.jpg"), face_roi)
                cv2.imshow('Face Capture - E2C TEAM', img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum >= max_samples:
                break
        cam.release()
        cv2.destroyAllWindows()
        
        data_manager.add_student(Id, name, email)
        
        print(f"\n  {success('✓')} Images Saved Successfully!")
        print(f"  {success('✓')} Student: {bold(name)} (ID: {bold(Id)})")
        print(f"  {success('✓')} Total Images Captured: {bold(sampleNum)}")
        print(f"  {separator('═', 50)}")
    else:
        print(f"\n  {error('✗')} Validation Error:")
        if(not is_number(Id)):
            print(f"    {error('•')} ID must be numeric")
        if(not name.isalpha()):
            print(f"    {error('•')} Name must contain only alphabetic characters")