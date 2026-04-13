import os
import time
import cv2
import numpy as np
from PIL import Image
from colors import success, error, info, bold, separator, highlight


def print_header(title):
    """Print stylish header"""
    print("\n" + separator("═", 55))
    print(f"  {title}")
    print(separator("═", 55))


def getImagesAndLabels(path):
    """Extract images and labels from training directory"""
    if not os.path.exists(path) or not os.listdir(path):
        return [], []
    
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')
            Id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces.append(imageNp)
            Ids.append(Id)
        except:
            continue
    return faces, Ids


def TrainImages(storage_paths):
    print_header("🤖 TRAINING MODEL - Face Recognition")
    print(f"\n  {info('⏳')} Loading training images...")
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    harcascadePath = "haarcascade_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    training_path = storage_paths['TrainingImages']
    faces, Id = getImagesAndLabels(training_path)
    
    if len(faces) == 0:
        print(f"\n  {error('✗')} No training images found!")
        print(f"  {error('✗')} Please capture faces first.\n")
        return
    
    print(f"  {success('✓')} Found {bold(len(faces))} images to train\n")
    print(f"  {info('⏳')} Training in progress...")
    recognizer.train(faces, np.array(Id))
    counter_img(training_path)
    
    model_path = os.path.join(storage_paths['TrainedModels'], 'Trainner.yml')
    recognizer.save(model_path)
    print(f"\n  {success('✓')} Model trained and saved successfully!")
    print(f"  {success('✓')} Model Path: {bold(model_path)}")
    print(separator("═", 55) + "\n")


def counter_img(path):
    """Display training progress"""
    imgcounter = 1
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    for imagePath in imagePaths:
        print(f"  ⏳ Processed: {imgcounter}/{len(imagePaths)} images", end="\r")
        time.sleep(0.008)
        imgcounter += 1