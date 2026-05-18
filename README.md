# NIAT MK Smart Face Recognition Attendance System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Contrib-green.svg)](https://opencv.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-red.svg)](https://flask.palletsprojects.com/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Reports-orange.svg)](https://www.reportlab.com/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

Offline face recognition attendance with a keyboard-first terminal experience, editable settings, local reports, and a browser dashboard.

[Download](#download-and-setup) • [How to Use](#how-to-use) • [Settings](#settings) • [Project Structure](#project-structure) • [Troubleshooting](#troubleshooting)

</div>

## Preview

![Terminal UI preview](IMGS/IMG%201.png)

[Watch the web UI preview video](IMGS/WEB%20UI%20VIDEO.mp4)

---

## Overview

NIAT MK is a fully offline attendance system built for local classrooms, labs, and small organizations. It uses webcam-based face capture and recognition to mark attendance, stores everything on the machine, and generates attendance reports without depending on cloud services.

The current version includes:

- A launcher-driven workflow through `launcher.py`
- A stylish keyboard-only terminal interface
- A normal terminal menu for quick local workflows
- Editable system settings instead of a read-only settings page
- Student detail management from the settings console
- Local CSV attendance logs and PDF report generation
- A Flask web dashboard for browser-based use

---

## What Is New

This release updates the original project into a cleaner and more usable system.

- The launcher now prefers the project `.venv` so the app uses the correct dependencies.
- The enhanced terminal interface now runs in keyboard-only mode.
- The settings screen now lets you change real values such as camera index, pass mark, sample count, theme, and HUD options.
- Report generation now includes richer attendance details and a daily text report.
- Student records can be added from the enhanced settings console.

---

## Core Features

### Attendance and Recognition

- Real-time face detection and recognition
- Student attendance marking during live camera sessions
- Capture workflow for collecting training images
- Model training from stored face samples
- Attendance CSV output plus PDF and text report generation

### Interface Modes

- Keyboard-first enhanced terminal interface
- Normal stylish terminal mode for keyboard users
- Web dashboard access for browser-based control

### Administration

- Add and manage student details
- Update pass mark and capture limits
- Change camera index and camera scan range
- Toggle HUD display and boot animation
- View current settings before applying changes

### Storage and Reports

- Local storage under the project workspace
- Student CSV database
- Attendance history by date
- Human-readable daily reports
- PDF attendance reports

---

## Download And Setup

### 1. Get the project

Clone the repository to your machine:

```bash
git clone https://github.com/lenluarun/NIAT_MK.git
cd NIAT_MK
```

### 2. Create the virtual environment

Use the project environment the launcher expects:

```bash
python -m venv .venv
```

### 3. Activate it on Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

The important packages include:

- `opencv-contrib-python`
- `numpy`
- `pandas`
- `Pillow`
- `scikit-learn`
- `Flask`
- `Flask-CORS`
- `reportlab`

### 5. Start the app

On Windows, the simplest option is:

```powershell
.\run.bat
```

You can also launch directly:

```bash
python launcher.py
```

---

## How To Use

### Recommended startup flow

1. Run `run.bat` or `python launcher.py`.
2. Choose the terminal interface or the web interface.
3. Check the camera first.
4. Add student details and capture face samples.
5. Train the recognizer.
6. Start attendance recognition.
7. Review the generated attendance reports.

### Normal Stylish Terminal

Use this if you prefer keyboard input and a simple command-style flow.

The terminal UI uses numbered menus and plain text prompts only.

### Web Interface

If you want browser-based control, run:

```bash
python web_app.py
```

Then open:

```text
http://localhost:5000
```

---

## Settings

The enhanced settings console is now editable.

You can change:

- Camera index
- Camera scan range
- Capture sample limit
- Recognition pass mark
- Recognition mode
- UI theme
- Boot animation
- HUD display
- Student details

Settings are stored locally in the configuration files under `config/` and loaded on startup.

---

## Reports And Data

The system stores and generates data locally.

- Student list: `src/data/StudentDetails/StudentDetails.csv`
- Attendance logs: `src/data/Attendance/`
- Daily text summary: `Daily_Report_YYYY-MM-DD.txt`
- PDF report: `Attendance_YYYY-MM-DD_Report.pdf`

The reports include marked students, timestamps, and summary details.

---

## Project Structure

```text
NIAT_MK/
├── launcher.py
├── main.py
├── web_app.py
├── run.bat
├── requirements.txt
├── config/
├── docs/
├── src/
│   ├── core/
│   ├── data/
│   ├── models/
│   ├── reports/
│   └── utils/
└── templates/
```

Key files:

- `launcher.py` is the main entry point.
- `main.py` contains the core business actions.
- `src/utils/interactive_ui.py` contains the enhanced interface.
- `src/core/data.py` manages students and reports.
- `src/core/recognition.py` handles recognition and attendance.
- `src/utils/settings_manager.py` stores editable settings.

---

## Requirements

- Python 3.11 or newer is recommended
- Webcam or camera device
- Windows PowerShell or Command Prompt for the main launcher flow
- OpenCV contrib build for face recognition support

If face recognition fails to import, make sure `opencv-contrib-python` is installed instead of only the base OpenCV package.

---

## Troubleshooting

### Camera does not open

- Check Windows camera permissions.
- Try a different camera index in Settings.
- Close other apps that may already be using the webcam.

### Recognition does not work

- Capture new face samples first.
- Train the model before starting recognition.
- Confirm the trained model file exists in the models folder.

### Terminal text looks broken

- Use Windows Terminal or modern PowerShell.
- Keep the project launcher and terminal on UTF-8 capable settings.

---

## Notes For Developers

- `launcher.py` is the preferred entry point.
- Do not run `main.py` directly unless you are debugging internals.
- Keep changes aligned with the enhanced interface flow.
- Update the README whenever you add a new mode, action, or report format.

---

## License

This project is provided under the MIT License.

---

## Acknowledgments

- OpenCV for the face detection and recognition tooling
- Flask for the web dashboard
- ReportLab for PDF generation
- The contributors and maintainers of this project

---

<div align="center">

If you want the next update, I can also rewrite the docs in `docs/` so they match this README exactly.

</div>
