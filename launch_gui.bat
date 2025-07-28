@echo off
echo Bengali License Plate Recognition GUI Launcher
echo ===============================================

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo Error: Could not activate virtual environment.
    echo Please ensure the virtual environment is set up correctly.
    pause
    exit /b 1
)

echo Virtual environment activated.
echo.

echo Launching GUI application...
python license_plate_gui.py

if errorlevel 1 (
    echo.
    echo Error occurred while running the application.
    echo You can also try running the test script first:
    echo python test_gui.py
)

echo.
echo Press any key to exit...
pause > nul
