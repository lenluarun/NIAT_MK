def camer(camera_index=0):
    import cv2
    import os

    # Haarcascade path resolution
    base_dir = os.path.dirname(__file__)
    cascade_path = os.path.join(base_dir, 'haarcascade_default.xml')
    if not os.path.exists(cascade_path):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

    # Load the cascade
    cascade_face = cv2.CascadeClassifier(cascade_path)

    # To capture video from webcam.
    cap = cv2.VideoCapture(int(camera_index))
    if not cap.isOpened():
        print(f"✗ Failed to open camera at index {camera_index}")
        return

    try:
        while True:
            # Read the frame
            ret, img = cap.read()
            if not ret or img is None:
                print("✗ Failed to read frame from camera. Exiting check.")
                break

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect the faces
            faces = cascade_face.detectMultiScale(gray, 1.3, 5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

            # Draw the rectangle around each face
            for (a, b, c, d) in faces:
                cv2.rectangle(img, (a, b), (a + c, b + d), (10,159,255), 2)

            # Display
            cv2.imshow('Webcam Check', img)

            # Stop if 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("\n⚠ Camera check interrupted by user (Ctrl+C).")
    finally:
        # Release the captureVideo object
        cap.release()
        cv2.destroyAllWindows()
