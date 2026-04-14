def camer(camera_index=0):
    """Test camera connectivity and display"""
    import cv2
    import os
    from ui_console import print_card
    
    print_card(
        "CAMERA TEST / LIVE PREVIEW",
        [
            f"Target Camera Index: {camera_index}",
            "Face detector: Haar Cascade",
            "Press Q to stop camera preview",
        ],
    )

    # Get absolute path to cascade classifier
    cascade_dir = os.path.dirname(os.path.abspath(__file__))
    cascade_path = os.path.join(cascade_dir, 'haarcascade_default.xml')
    
    if not os.path.exists(cascade_path):
        print(f"  ⚠ Error: Cascade classifier not found at {cascade_path}!\n")
        return
    
    cascade_face = cv2.CascadeClassifier(cascade_path)
    
    if cascade_face.empty():
        print(f"  ⚠ Error: Failed to load cascade classifier!\n")
        return
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"  ⚠ Error: Cannot open camera index {camera_index}!\n")
        return

    while True:
        ret, img = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade_face.detectMultiScale(gray, 1.3, 5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        
        cv2.putText(img, "E2C TEAM - Camera Check", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"Faces Detected: {len(faces)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        for (a, b, c, d) in faces:
            cv2.rectangle(img, (a, b), (a + c, b + d), (0, 255, 0), 2)
            cv2.putText(img, "Face", (a, b-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow('Camera Test - Press Q to Exit', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("  ✓ Camera closed successfully")
    print("  ═ Powered by E2C TEAM ═\n")
    cap.release()
    cv2.destroyAllWindows()
