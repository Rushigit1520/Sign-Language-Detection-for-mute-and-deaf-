@echo off
title Sign Language To Text and Speech Conversion
echo ============================================
echo  Sign Language To Text Conversion
echo  Author: Rushikesh Farakate
echo ============================================
echo.

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment not found.
    echo [*] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [*] Starting application...
echo [*] Please ensure your webcam is connected.
echo.
python final_pred.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with errors.
    echo [*] Make sure all dependencies are installed: pip install -r requirements.txt
    pause
)
