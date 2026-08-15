@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   SkyTrail Desktop Launcher
echo ============================================

if not exist "venv\Scripts\python.exe" (
    echo [Setup] No virtual environment found. Creating one with Python 3.12...
    py -3.12 -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERROR] Could not create venv using Python 3.12.
        echo Make sure Python 3.12 is installed from python.org
        pause
        exit /b 1
    )
    echo [Setup] Virtual environment created.
)

call venv\Scripts\activate.bat

python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo [Setup] Installing dependencies, this may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Dependency install failed. Check the error above.
        pause
        exit /b 1
    )
)

where ollama >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Ollama not found on PATH. Make sure it's installed from ollama.com
)

echo [Launch] Starting SkyTrail...
echo.
python src\main.py

if errorlevel 1 (
    echo.
    echo [ERROR] SkyTrail closed with an error. See above for details.
    pause
)
