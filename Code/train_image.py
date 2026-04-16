import os
import time
import cv2
import numpy as np
from PIL import Image
from threading import Thread


def getImagesAndLabels(path):
    # path of all the files in the folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    faces = []
    # empty ID list
    Ids = []
    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')
            Id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces.append(imageNp)
            Ids.append(Id)
        except Exception:
            # skip unreadable files or unexpected filename formats
            continue
    return faces, Ids


def TrainImages(storage_paths):
    """
    Train the LBPH face recognizer using images from storage_paths['TrainingImages']
    and write the trained model to storage_paths['TrainedModels'] or TrainingImageLabel.
    """
    # Resolve directories
    training_dir = storage_paths.get('TrainingImages') if isinstance(storage_paths, dict) else 'TrainingImage'
    trained_dir = storage_paths.get('TrainedModels') or storage_paths.get('TrainingImageLabel') or 'TrainingImageLabel'
    os.makedirs(training_dir, exist_ok=True)
    os.makedirs(trained_dir, exist_ok=True)

    recognizer = None
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except Exception as e:
        # If cv2.face is not available, try the alternative import path
        if hasattr(cv2, 'face'):
            recognizer = cv2.face.LBPHFaceRecognizer_create()
        else:
            raise

    faces, Ids = getImagesAndLabels(training_dir)
    if not faces or not Ids:
        print("✗ No training images found. Please capture images first.")
        return

    def train_and_save():
        recognizer.train(faces, np.array(Ids))
        model_path = os.path.join(trained_dir, "Trainner.yml")
        recognizer.save(model_path)
        print(f"✓ Training complete. Model saved to: {model_path}")

    # Start counter thread for UI feedback
    Thread(target=counter_img, args=(training_dir,), daemon=True).start()
    # Run training in main thread (training may block; run in background thread if desired)
    train_thread = Thread(target=train_and_save)
    train_thread.start()
    try:
        train_thread.join()
    except KeyboardInterrupt:
        print("\n⚠ Training interrupted by user (Ctrl+C).")


def counter_img(path):
    imgcounter = 1
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for imagePath in imagePaths:
        print(str(imgcounter) + " Images Trained", end="\r")
        time.sleep(0.008)
        imgcounter += 1
    print()  # newline after counter
