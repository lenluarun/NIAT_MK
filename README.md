# 🛡️ NIAT MK: Smart Biometric Attendance System

<div align="center">

![Project Banner](IMGS/IMG%201.png)

**A Privacy-First, Multi-Modal Attendance & Access Control Solution**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/en/products/socs/esp32)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

[Features](#-key-features) • [Hardware](#-hardware-integration) • [Setup](#-quick-start) • [Usage](#-how-to-use) • [Structure](#-project-structure)

</div>

---

## 🌟 Overview

**NIAT MK** is an advanced, fully offline attendance system designed for high-privacy environments like classrooms, laboratories, and small offices. By combining **Face Recognition** (OpenCV LBPH) and **Biometric Fingerprint Matching** (R307 Sensor), it provides a robust, fail-safe solution for attendance tracking and physical access control.

> **Privacy-First:** All data processing, model training, and biometric storage happen locally. No cloud, no internet dependencies, no data leaks.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **Dual-Biometric** | Support for Face Recognition (Webcam/ESP32-CAM) and Fingerprint matching. |
| **Offline AI** | Uses LBPH algorithms for high-speed, local face recognition and training. |
| **Smart Reports** | Automated generation of Daily Text summaries and Professional PDF reports. |
| **Dual Interface** | Choose between a **Power-User Terminal** or a **Modern Web Dashboard**. |
| **Access Control** | Integrated relay control for electronic door locks via ESP32. |
| **Live Monitoring** | Real-time MJPEG streaming from remote ESP32-CAM nodes. |

---

## 🔌 Hardware Integration

The system supports a distributed architecture with dedicated hardware nodes:

### 📹 ESP32-CAM (Vision Node)
- **Wireless Streaming**: MJPEG live feed over WiFi.
- **Remote Capture**: High-res image capture for dataset training.
- **Local Logging**: SD Card support for standalone backups.

### ☝️ ESP32 Controller (Biometric Node)
- **R307 Fingerprint**: Sub-second matching with 1000+ slot capacity.
- **OLED Display**: SSD1306 display for status, names, and "Live Cam" thumbnails.
- **Physical Feedback**: Buzzer, Dual-LED status, and Relay for door control.

---

## 🛠️ Tech Stack

### Software
- **Core**: Python 3.11+
- **Vision**: OpenCV (contrib-python), Pillow
- **Data**: Pandas, NumPy, Scikit-learn
- **Web**: Flask, Bootstrap 5, Jinja2
- **Reporting**: ReportLab

### Hardware
- **Controllers**: ESP32 DevKit V1, ESP32-CAM (AI-Thinker)
- **Sensors**: R307 Optical Fingerprint Module
- **Displays**: 0.96" I2C OLED (SSD1306)
- **Actuators**: 5V Relay Module, Active Buzzer

---

## 📦 Quick Start

### 1. Clone & Prep
```bash
git clone https://github.com/lenluarun/NIAT_MK.git
cd NIAT_MK
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Hardware
- Open `FP/ESP32_CONTROLLER/ESP32_CONTROLLER.ino` or `FP/ESP32_CAM_SOLO/ESP32_CAM_SOLO.ino`.
- Update `STASSID`, `STAPSK`, and `SERVER_IP` to match your local network.
- Flash the firmware using Arduino IDE.

### 3. Launch System
```bash
# Start the main launcher
python launcher.py

# OR start the web dashboard directly
python web_app.py
```

---

## 🖥️ How To Use

1. **Registration**: Add student details via the Terminal or Web UI.
2. **Capture**: Collect 100+ face samples or enroll fingerprints via the ESP32 node.
3. **Train**: Run the training module to update the local `.yml` model.
4. **Attendance**: 
   - **Face Mode**: Start the recognizer. Once a face is matched, attendance is logged.
   - **Finger Mode**: Place finger on sensor. The node identifies the student and notifies the server.
5. **Report**: Check the `src/data/Attendance/` folder for PDF and Text reports.

---

## 📂 Project Structure

```text
NIAT_MK/
├── launcher.py            # Unified interface selector
├── web_app.py             # Flask Web Dashboard
├── config/                # JSON System Settings
├── src/
│   ├── core/              # Recognition, Biometric, & Data logic
│   ├── models/            # Trained Models & Haar Cascades
│   ├── data/              # Student Database & Reports
│   └── utils/             # UI Engines & Settings Managers
├── FP/                    # ESP32 Firmware (C++/Arduino)
└── templates/             # Web UI HTML Assets
```

---

## 🤝 Contributing & License

This project is maintained by **E2C TEAM**.
Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">

**Developed with ❤️ for secure and efficient attendance management.**

</div>
