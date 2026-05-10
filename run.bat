@echo off
echo ================================================
echo E2C FACE RECOGNITION & ATTENDANCE SYSTEM
echo    Completely Offline ^| Real-time Processing
echo    Powered by E2C TEAM
echo ================================================
echo.
echo [INFO] Initializing E2C Control Center...
echo.
if exist ".venv\Scripts\python.exe" (
	echo [INFO] Using project virtual environment: .venv
	.venv\Scripts\python.exe launcher.py
) else (
	echo [WARN] .venv not found. Using system Python.
	python launcher.py
)
pause