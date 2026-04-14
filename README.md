# Smart Face Attendance System

Offline face-recognition attendance system built with Python and OpenCV, with a cinematic terminal interface, camera studio tools, student management, and attendance reporting.

## Highlights

- Fully offline workflow (no cloud dependency)
- Stylish terminal UI themes (`neon`, `e2c`, `matrix`, `abyss`, `phantom`)
- Camera Studio with scan, selection, and profile view
- Student management (single add, bulk add, CSV import, delete, view)
- Face capture, model training, and attendance recognition
- Local CSV attendance logs and dashboard stats

## Tech Stack

- Python 3.11+
- OpenCV (`opencv-contrib-python`)
- NumPy
- Standard library CSV-based storage for student lookup and attendance logs

## Project Structure

```text
NIAT_MK/
├── main.py                     # Root launcher (adds Code/ to path)
├── README.md
├── LAUNCHER_STRUCTURE.md
└── Code/
    ├── main.py                 # Main application entry point
    ├── ui_console.py           # Cinematic terminal UI components
    ├── colors.py               # ANSI color helpers
    ├── check_camera.py         # Camera test utility
    ├── camera_utils.py         # Camera scan helpers
    ├── capture_image.py        # Training image capture
    ├── train_image.py          # LBPH model training
    ├── recognize.py            # Attendance recognition
    ├── data_manager.py         # Student and report operations
    ├── settings_manager.py     # Persistent app settings
    ├── storage_manager.py      # Offline storage setup
    └── haarcascade_default.xml # Face detector
```

## Setup

### 1) Create and activate virtual environment (recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install opencv-contrib-python numpy
```

## Run

From project root:

```powershell
python "Code/main.py"
```

Alternative launcher:

```powershell
python "main.py"
```

## Typical Workflow

1. Open `Camera Studio` and select the active camera.
2. Add students via `Data Management`.
3. Capture face images (`Capture Faces`).
4. Train the recognizer (`Train Images`).
5. Start attendance (`Recognize & Attendance`).
6. Review logs in `View Reports`.

## Settings You Can Configure

- Active camera index
- Camera scan range
- Capture sample target
- Recognition pass mark
- UI theme
- Boot animation
- HUD status panel

These are persisted in `app_settings.json`.

## Data Locations

The app creates and uses local folders such as:

- `StudentData` (student CSV database)
- `TrainingImages`
- `TrainedModels`
- `AttendanceRecords`

Exact base location is managed by `storage_manager.py` and displayed during startup.

## Troubleshooting

- Camera not opening:
  - Check camera permissions in Windows settings.
  - Use `Camera Studio -> Scan Available Cameras`.
  - Try another camera index.

- Recognition not working:
  - Ensure you have captured images first.
  - Run `Train Images` to generate `Trainner.yml`.
  - Verify `haarcascade_default.xml` exists in `Code/`.

- Unicode symbols look broken in terminal:
  - Use Windows Terminal or PowerShell with UTF-8 capable font (e.g., Cascadia Mono).

- Corporate policy blocks DLLs:
  - This project avoids `pandas` in recognition flow; if OpenCV DLLs are blocked, use an approved Python/runtime environment.

## Notes

- This project is intended for educational/offline institutional attendance use.
- Store attendance data securely and comply with local privacy policy.

