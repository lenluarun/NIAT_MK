import csv
import cv2
import os
from colors import success, error, info, bold, separator, highlight


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
    print("\n" + separator("═", 50))
    print(f"  {title}")
    print(separator("═", 50))


def takeImages(storage_paths, data_manager):
    print_section("📸 CAPTURE FACES - Training Image Collection")
    Id = input(f"\n  {info('➤')} Enter Student ID (Numeric): ")
    name = input(f"  {info('➤')} Enter Student Name (Alphabetic): ")
    email = input(f"  {info('➤')} Enter Email (Optional, press Enter to skip): ")

    if(is_number(Id) and name.isalpha()):
        print(f"\n  {success('✓')} Starting capture for: {bold(name)} (ID: {bold(Id)})")
        print("  Press 'Q' to stop or capture 100+ images\n")
        
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0
        training_path = storage_paths['TrainingImages']

        while(True):
            ret, img = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30,30), flags=cv2.CASCADE_SCALE_IMAGE)
            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                sampleNum = sampleNum+1
                cv2.putText(img, f"Samples: {sampleNum}", (x+5, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imwrite(os.path.join(training_path, f"{name}.{Id}.{sampleNum}.jpg"), gray[y:y+h, x:x+w])
                cv2.imshow('Face Capture - E2C TEAM', img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum > 100:
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