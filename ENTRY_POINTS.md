# E2C System - Entry Points Documentation

## Primary Entry Point

### **`launcher.py`** ⭐ (USE THIS)
The single unified entry point for the E2C Attendance System.

**How to run:**
```bash
python launcher.py
```

**Features:**
- ✓ Terminal Interface (Professional E2C UI)
- ✓ Web Interface (Browser-based)
- ✓ System Updates from GitHub
- ✓ Clean menu-driven navigation

---

## Secondary Entry Points (Specialized)

### **`web_app.py`**
Direct web interface launcher (alternative to using launcher.py option 2).

```bash
python web_app.py
```
- Starts Flask development server on http://localhost:5000
- Use if you want to skip the launcher menu

### **`test_attendance.py`**
Test utility for attendance system functions.

```bash
python test_attendance.py
```
- For development/testing purposes
- Not part of main workflow

---

## Module Structure

### **`main.py`** (DO NOT RUN DIRECTLY)
Core module containing all business logic and menu functions.
- Imported by `launcher.py` → `interactive_ui.py`
- Contains: camera, capture, training, recognition, reports, settings
- Should NEVER be run directly - use launcher.py instead

### **`src/utils/interactive_ui.py`**
Professional E2C terminal UI with styling.
- Called by launcher.py for terminal interface
- Renders beautiful ASCII art and colored menus
- Handles user interaction with main.py functions

---

## Workflow

```
launcher.py
    ├─→ [1] Terminal Interface
    │       └─→ src/utils/interactive_ui.py
    │           └─→ main.py (functions)
    │
    ├─→ [2] Web Interface
    │       └─→ web_app.py (Flask)
    │
    └─→ [3] Update System
            └─→ src/core/updater.py
```

---

## Removed Files

The following old/redundant files have been deleted:
- ❌ `demo_ui.py` (Old demo)
- ❌ `src/main_interface.py` (Duplicate of main.py)

---

## Quick Start

1. **Open Terminal in project directory**
2. **Run:** `python launcher.py`
3. **Select option 1 for Terminal UI** (or 2 for Web UI)
4. **Enjoy the professional E2C interface!**

---

## For Developers

If you need to:
- **Test a specific function**: Import from `main.py`
- **Modify the terminal UI**: Edit `src/utils/interactive_ui.py`
- **Add a new menu option**: Add function to `main.py` and menu button to `launcher.py`
- **Run tests**: Use `test_attendance.py`

