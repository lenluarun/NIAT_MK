# NIAT MK Smart Face Recognition & Biometric Attendance System

## 1. Project Overview
NIAT MK is an advanced, fully offline attendance system designed for local environments like classrooms, laboratories, and small offices. It combines **Face Recognition** (via local webcam or remote ESP32-CAM) and **Fingerprint Recognition** (via R307 sensor) into a unified attendance and access control solution.

The system is built with a "Privacy-First" approach, meaning all data processing, face training, and report generation happen locally on your machine without requiring any cloud or internet connection.

---

## 2. Core Architecture
The system follows a **Centralized Server - Remote Node** architecture.

### A. Central Python Server
The heart of the system is the Python backend which orchestrates everything:
- **Face Processing**: Uses OpenCV's LBPH (Local Binary Patterns Histograms) algorithm for high-speed offline face recognition.
- **Data Management**: Manages student databases, fingerprint slot mappings, and attendance records.
- **Reporting Engine**: Automatically generates daily text summaries and professional PDF attendance reports using ReportLab.
- **Communication Hub**: Provides a REST API for the ESP32 hardware nodes to poll for commands and report recognition events.

### B. Interface Layers
- **Launcher (`launcher.py`)**: A central entry point for setting up dependencies, updating the system, and choosing the interface mode.
- **Terminal UI**: A stylish, keyboard-first console interface for power users who prefer high-speed local operations.
- **Web UI (`web_app.py`)**: A modern Bootstrap 5 dashboard accessible via any browser on the local network, featuring real-time statistics and touch-friendly controls.

---

## 3. Hardware Integration
The project features custom firmware for two types of ESP32-based hardware nodes:

### I. ESP32-CAM (Vision Node)
- **Role**: Dedicated wireless camera and storage node.
- **Features**:
    - **Live Streaming**: MJPEG video stream for remote monitoring.
    - **Capture**: High-resolution image capture for training and verification.
    - **Local Storage**: Integrated SD Card support for logging and storing student data backups.
    - **Remote Control**: Flash LED can be toggled remotely from the dashboard.

### II. ESP32 Controller (Biometric & Access Node)
- **Role**: Handles fingerprint identification and physical access control.
- **Features**:
    - **Biometric Sensor**: Integrated R307 fingerprint module for sub-second matching.
    - **Visual Feedback**: 0.96" OLED Display (SSD1306) shows system status, student names, and "Live Cam" thumbnails.
    - **Access Control**: Onboard Relay for controlling electronic door locks.
    - **Alerts**: Buzzer and Dual-LED (Red/Green) system for success/denial feedback.
    - **Hazard Mode**: A remote-triggered emergency strobe mode for the controller LEDs.

---

## 4. How It Works (Workflow)

### 1. Registration
1. Student details are added via the Terminal or Web UI.
2. **Face Capture**: 100+ samples are captured via a webcam or the ESP32-CAM.
3. **Biometric Enrollment**: The ESP32 Controller is put into "Enroll Mode" via the server, and the student's fingerprint is mapped to their unique ID.

### 2. Training
The system uses the captured face samples to train a local `.yml` model. This process is fully offline and usually takes only a few seconds.

### 3. Attendance & Recognition
- **Mode A (Face)**: The system monitors the video stream. When a face matches the trained model, attendance is marked.
- **Mode B (Fingerprint)**: When a student places their finger on the sensor, the controller identifies the slot, sends the "Match" event to the server, and the server logs the attendance.
- **Access Control**: Upon a successful match (Face or Finger), the server can send an "Unlock" command to the ESP32 Controller to trigger the relay.

### 4. Reporting & Notification
- Every attendance marking triggers a background email notification (optional) to the student.
- At the end of the day (or on-demand), the system compiles all logs into a CSV and generates a beautiful PDF report.

---

## 5. Project Structure
```text
NIAT_MK/
├── launcher.py            # Main entry point (Interface selector)
├── web_app.py             # Flask Web Server
├── config/                # JSON application settings
├── src/
│   ├── core/              # Business Logic (Recognition, Biometric, Data)
│   ├── models/            # Trained AI models & Haar Cascades
│   ├── data/              # Student CSVs and Attendance Reports
│   └── utils/             # UI rendering and Settings management
├── FP/                    # Hardware Firmware
│   ├── ESP32_CAM_SOLO/    # ESP32-CAM Source Code
│   └── ESP32_CONTROLLER/  # ESP32 Fingerprint Node Source Code
└── templates/             # Web UI HTML templates
```

---

## 6. Connection & Setup
1. **Host Computer**: Runs the Python server (`launcher.py`).
2. **Network**: All devices (Server, ESP32-CAM, ESP32 Controller) must be on the same WiFi network.
3. **Configuration**:
    - Update `SERVER_IP` in the `.ino` files to match your computer's local IPv4.
    - Set the camera index or ESP32-CAM IP in the application settings.
4. **Hardware Hookup**:
    - **Fingerprint**: TX/RX to ESP32 pins 25/26.
    - **OLED**: I2C to pins 21/22.
    - **Relay**: Pin 4.

---

## 7. Key Features
- ✅ **Multi-Modal Biometrics**: Face + Fingerprint support.
- ✅ **Offline Operation**: No internet required for core functionality.
- ✅ **Automated Reporting**: Instant PDF and CSV generation.
- ✅ **Dual UI**: Choice between Terminal efficiency and Web aesthetics.
- ✅ **Remote Camera**: Use ESP32-CAM as a wireless vision node.
- ✅ **Email Alerts**: Automatic attendance confirmation emails.
- ✅ **Responsive Dashboard**: Manage everything from your phone browser.

---
**Powered by E2C TEAM**
