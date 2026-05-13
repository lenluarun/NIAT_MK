def camer(camera_index=0, frame_callback=None, show_window=True, max_frames=None, stop_event=None):
    import cv2
    import os

    # Haarcascade path resolution
    base_dir = os.path.dirname(__file__)
    cascade_path = os.path.join(base_dir, '..', 'models', 'haarcascade_default.xml')
    if not os.path.exists(cascade_path):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

    # Load the cascade
    cascade_face = cv2.CascadeClassifier(cascade_path)

    # Handle both USB cameras (index) and network cameras (URL)
    try:
        if isinstance(camera_index, str) and (camera_index.startswith('http') or camera_index.startswith('rtsp')):
            # Network camera (URL/IP stream)
            cap = cv2.VideoCapture(camera_index)
            camera_label = camera_index
        else:
            # USB camera (numeric index)
            cap = cv2.VideoCapture(int(camera_index))
            camera_label = f"USB Index {camera_index}"
    except Exception:
        cap = cv2.VideoCapture(int(camera_index))
        camera_label = f"USB Index {camera_index}"
    
    if not cap.isOpened():
        print(f"✗ Failed to open camera: {camera_label}")
        return

    frame_count = 0

    try:
        while True:
            # Check if stop event is set
            if stop_event and stop_event.is_set():
                print("✓ Camera check stopped by user.")
                break
            
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

            if frame_callback:
                try:
                    frame_callback(img)
                except Exception:
                    pass

            if show_window:
                cv2.imshow('Webcam Check', img)

            frame_count += 1
            if show_window:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            if max_frames is not None and frame_count >= max_frames:
                break
    except KeyboardInterrupt:
        print("\n⚠ Camera check interrupted by user (Ctrl+C).")
    finally:
        # Release the captureVideo object
        cap.release()
        if show_window:
            cv2.destroyAllWindows()
