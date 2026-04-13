# 🚀 Launcher & Directory Structure

## Complete Project Layout

```
NIAT_MK/
│
├── .qodo/                          (Qodo Configuration)
│   └── [Configuration files]
│
├── .venv/                          (Python Virtual Environment)
│   ├── Scripts/
│   │   └── python.exe             (Python Interpreter)
│   │   └── pip.exe                (Package Manager)
│   │   └── Activate.ps1           (Environment Activation Script)
│   ├── Lib/
│   │   └── site-packages/         (Installed Dependencies)
│   └── pyvenv.cfg                 (Virtual Env Config)
│
└── Smart-Attendance-System/        (Main Project)
    │
    ├── .git/                       (Git Repository)
    ├── .qodo/                      (Project Config)
    ├── README.md                   (Original Documentation)
    │
    └── Code/                       (Application Source)
        ├── main.py                 ⭐ Main Application Entry
        ├── colors.py               (Terminal Styling)
        ├── storage_manager.py      (Offline Storage)
        ├── data_manager.py         (Student Management)
        ├── capture_image.py        (Face Capture)
        ├── train_image.py          (Model Training)
        ├── recognize.py            (Attendance Recognition)
        ├── check_camera.py         (Camera Test)
        ├── automail.py             (Email Reports)
        ├── test_system.py          (Component Testing)
        ├── haarcascade_default.xml (Face Detector)
        ├── PROJECT_STATUS.md       (Completion Report)
        │
        ├── StudentDetails/         (CSV Database)
        ├── TrainingImages/         (Captured Faces)
        ├── TrainedModels/          (ML Models)
        ├── AttendanceRecords/      (Attendance Logs)
        ├── Reports/                (Generated Reports)
        └── Backups/                (Data Backups)
```

---

## 📂 Launcher Directory (Smart-Attendance-System Root)

### Files:
| File | Purpose |
|------|---------|
| `README.md` | Original project documentation |
| `.git/` | Git version control |
| `.qodo/` | Project configuration |

### To Run Application:

#### Option 1: Direct from Smart-Attendance-System folder
```powershell
cd Smart-Attendance-System\Code
python main.py
```

#### Option 2: From NIAT_MK (parent) folder
```powershell
cd Smart-Attendance-System\Code
python main.py
```

#### Option 3: Using Virtual Environment
```powershell
# From NIAT_MK root
.\.venv\Scripts\Activate.ps1
cd Smart-Attendance-System\Code
python main.py
```

---

## 🔧 Virtual Environment Location

**Path:** `C:\Users\arune\OneDrive\Documents\github files\NIAT_MK\.venv\`

### What's Inside:
- **Scripts/** - Executables (python.exe, pip.exe, Activate.ps1)
- **Lib/site-packages/** - Installed Python packages
- **pyvenv.cfg** - Environment configuration

### Installed Packages:
- ✓ OpenCV
- ✓ NumPy
- ✓ Pandas
- ✓ Pillow
- ✓ YagMail

---

## 🎯 Quick Start Commands

### From Command Line:
```powershell
# Navigate to project
cd "C:\Users\arune\OneDrive\Documents\github files\NIAT_MK\Smart-Attendance-System\Code"

# Run application
python main.py
```

### From PowerShell with Virtual Env:
```powershell
# Activate virtual environment
cd "C:\Users\arune\OneDrive\Documents\github files\NIAT_MK"
.\.venv\Scripts\Activate.ps1

# Navigate to code and run
cd Smart-Attendance-System\Code
python main.py
```

---

## 📊 Directory Permissions & Access

| Path | Type | Access |
|------|------|--------|
| `.venv/` | Virtual Environment | Read/Execute |
| `.git/` | Version Control | Read |
| `Code/` | Application Source | Read/Write |
| `StudentDetails/` | Data Storage | Read/Write |
| `TrainingImages/` | Image Storage | Read/Write |
| `TrainedModels/` | Model Storage | Read/Write |
| `AttendanceRecords/` | Log Storage | Read/Write |

---

## ✅ Launcher Checklist

- ✅ Virtual environment created at `.venv/`
- ✅ All dependencies installed
- ✅ Python 3.11.9 available
- ✅ Application code in `Code/` subdirectory
- ✅ Launcher script: `Code/main.py`
- ✅ Test script: `Code/test_system.py`
- ✅ Documentation: `README.md` & `PROJECT_STATUS.md`

---

**Status:** 🟢 READY TO LAUNCH  
**Entry Point:** `Smart-Attendance-System/Code/main.py`  
**Environment:** Python 3.11.9 @ `.venv/`
