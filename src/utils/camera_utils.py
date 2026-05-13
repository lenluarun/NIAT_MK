"""
Camera helpers for selection and diagnostics.
"""
import cv2
import threading


def detect_available_cameras(max_index=5):
    """Probe camera indexes and return detected devices."""
    cameras = []
    results = {}
    
    def probe_camera(idx):
        """Probe a single camera in a separate thread with timeout protection."""
        try:
            # Use default backend (remove CAP_DSHOW which causes crashes)
            cap = cv2.VideoCapture(idx)
            # Set buffer size to 1 to avoid stalling
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # Set timeout properties
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                results[idx] = {
                    "index": idx,
                    "resolution": f"{width}x{height}",
                    "fps": round(fps, 1) if fps > 0 else 0
                }
            cap.release()
        except Exception:
            # Silently ignore any exceptions (OpenCV C++ exceptions, hardware errors, etc.)
            pass
    
    # Probe each camera in a thread with 2-second timeout per camera
    threads = []
    for idx in range(max_index + 1):
        thread = threading.Thread(target=probe_camera, args=(idx,), daemon=True)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads with timeout
    for thread in threads:
        thread.join(timeout=2.5)
    
    # Return results in order
    for idx in range(max_index + 1):
        if idx in results:
            cameras.append(results[idx])
    
    return cameras
