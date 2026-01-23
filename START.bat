@echo off
REM JVPS Desktop Remote - Startup Script

echo ============================================================
echo JVPS Desktop Remote - Starting Server
echo ============================================================

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install/update requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt -q

REM Start the application
echo.
echo Starting JVPS server...
echo Navigate to: http://localhost:5000/
echo.
python app.py

pause
