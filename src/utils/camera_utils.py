"""
Camera helpers for selection and diagnostics.
"""
import cv2


def detect_available_cameras(max_index=5):
    """Probe camera indexes and return detected devices."""
    cameras = []
    for idx in range(max_index + 1):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cameras.append({
                "index": idx,
                "resolution": f"{width}x{height}",
                "fps": round(fps, 1) if fps > 0 else 0
            })
        cap.release()
    return cameras
