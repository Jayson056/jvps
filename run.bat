@echo off
REM JVPS Desktop Remote - Setup Script
echo.
echo ====================================
echo   JVPS Desktop Remote - Setup & Run
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Clear screen
cls

echo.
echo ====================================
echo   JVPS Desktop Remote - READY TO START
echo =====================================
echo.
echo Server starting on http://localhost:58247
echo.
echo Quick Links:
echo  - Home:        http://localhost:58247/
echo  - New Broadcast: http://localhost:58247/broadcast/new
echo  - Browse Sessions: http://localhost:58247/view_list
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run app
python app.py

pause
