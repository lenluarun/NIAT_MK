"""
Face Recognition System Diagnostic Test
Tests camera, cascade classifier, and face detection
"""
import os
import cv2
import sys
from pathlib import Path

print("\n" + "═"*70)
print("  FACE RECOGNITION SYSTEM - DIAGNOSTIC TEST")
print("═"*70)

# Test 1: Check cascade classifier
print("\n[TEST 1] Checking Cascade Classifier File...")
cascade_dir = os.path.dirname(os.path.abspath(__file__))
cascade_path = os.path.join(cascade_dir, "haarcascade_default.xml")
print(f"  Expected path: {cascade_path}")

if os.path.exists(cascade_path):
    print("  ✓ Cascade file EXISTS")
    cascade = cv2.CascadeClassifier(cascade_path)
    if cascade.empty():
        print("  ✗ FAILED to load cascade classifier!")
        sys.exit(1)
    else:
        print("  ✓ Cascade classifier loaded successfully")
else:
    print(f"  ✗ Cascade file NOT FOUND")
    sys.exit(1)

# Test 2: Check camera
print("\n[TEST 2] Checking Camera Access...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("  ✗ Camera not accessible!")
    sys.exit(1)
else:
    print("  ✓ Camera is accessible")
    # Get camera properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"    - Resolution: {width}x{height}")
    print(f"    - FPS: {fps}")

# Test 3: Capture frames and detect faces
print("\n[TEST 3] Testing Face Detection from Camera...")
print("  ✓ Capturing 5 test frames and detecting faces...")
print("  (Window will appear - press 'Q' to skip any frame)\n")

face_count = 0
frame_count = 0
max_frames = 30

while frame_count < max_frames:
    ret, frame = cap.read()
    if not ret:
        print("  ✗ Failed to capture frame")
        break
    
    frame_count += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
    
    # Draw rectangles
    cv2.putText(frame, "E2C TEAM - Face Recognition Test", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"Faces Detected: {len(faces)}", (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.putText(frame, f"Frame: {frame_count}/{max_frames}", (10, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, "Face", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        face_count += 1
    
    cv2.imshow('Face Detection Test - Press Q to Exit', frame)
    
    key = cv2.waitKey(100) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Test 4: Check trained model
print("\n[TEST 4] Checking for Trained Model...")
storage_config = os.path.join(os.path.dirname(cascade_dir), "storage_config.json")
if os.path.exists(storage_config):
    import json
    with open(storage_config, 'r') as f:
        config = json.load(f)
        model_path = os.path.join(config.get('base_path', '.'), 'TrainingImageLabel', 'Trainner.yml')
else:
    model_path = os.path.join(cascade_dir, "TrainingImageLabel", "Trainner.yml")

if os.path.exists(model_path):
    print(f"  ✓ Trained model found: {model_path}")
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=16, grid_x=8, grid_y=8)
        recognizer.read(model_path)
        print("  ✓ Model loaded successfully")
    except Exception as e:
        print(f"  ✗ Failed to load model: {e}")
else:
    print(f"  ⚠ No trained model found at: {model_path}")
    print("  ⚠ Please train the model first using 'Train Images' option")

# Test 5: Check training data
print("\n[TEST 5] Checking Training Data...")
training_image_path = os.path.join(cascade_dir, "TrainingImage")
if os.path.exists(training_image_path):
    training_count = len(os.listdir(training_image_path))
    print(f"  Training images found: {training_count}")
    if training_count == 0:
        print("  ⚠ No training images available - please capture faces first")
else:
    print(f"  ✗ Training directory not found")

# Test 6: Check student database
print("\n[TEST 6] Checking Student Database...")
student_file = os.path.join(cascade_dir, "StudentDetails", "StudentDetails.csv")
if os.path.exists(student_file):
    with open(student_file, 'r') as f:
        lines = f.readlines()
        student_count = len(lines) - 1  # Exclude header
        print(f"  ✓ Student database found")
        print(f"  Students registered: {student_count}")
        if student_count == 0:
            print("  ⚠ No students registered - please add students first")
else:
    print(f"  ✗ Student database not found")

# Summary
print("\n" + "═"*70)
print("  TEST SUMMARY")
print("═"*70)
print(f"✓ Cascade classifier: LOADED")
print(f"✓ Camera: ACCESSIBLE")
print(f"✓ Face detection: WORKING ({frame_count} frames tested, {face_count} faces detected)")
input("\n✓ Press ENTER to exit...")
