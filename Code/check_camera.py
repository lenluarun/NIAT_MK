def camer():
    """Test camera connectivity and display"""
    import cv2
    
    print("\n" + "═" * 55)
    print("  📷 CAMERA TEST - Initializing...")
    print("═" * 55)
    print("\n  ✓ Camera is active")
    print("  ✓ Detecting faces...")
    print("  💡 Press 'Q' to close camera\n")

    cascade_face = cv2.CascadeClassifier('haarcascade_default.xml')
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("  ⚠ Error: Cannot open camera!\n")
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
