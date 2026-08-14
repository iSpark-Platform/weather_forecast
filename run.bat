@echo off
title WeatherSense AI — Launcher
color 0B
echo.
echo  ██╗    ██╗███████╗ █████╗ ████████╗██╗  ██╗███████╗██████╗ ███████╗███████╗███╗   ██╗███████╗███████╗
echo  ██║    ██║██╔════╝██╔══██╗╚══██╔══╝██║  ██║██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║██╔════╝██╔════╝
echo  ██║ █╗ ██║█████╗  ███████║   ██║   ███████║█████╗  ██████╔╝███████╗█████╗  ██╔██╗ ██║███████╗█████╗
echo  ██║███╗██║██╔══╝  ██╔══██║   ██║   ██╔══██║██╔══╝  ██╔══██╗╚════██║██╔══╝  ██║╚██╗██║╚════██║██╔══╝
echo  ╚███╔███╔╝███████╗██║  ██║   ██║   ██║  ██║███████╗██║  ██║███████║███████╗██║ ╚████║███████║███████╗
echo   ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝
echo.
echo                                  🌍 Advanced Weather Intelligence System
echo                            15-Day Forecast • Coastal Alerts • Risk Maps • AI Tutor
echo.
echo ══════════════════════════════════════════════════════════════════════════════════════════
echo.

REM Check if Python is installed
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)


echo [1/3] Checking Python environment...
py --version

REM Install requirements if needed
echo.
echo [2/3] Installing dependencies (first run may take a minute)...
py -m pip install -r requirements.txt --quiet --no-warn-script-location
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed. Trying to continue...
)

echo.
echo [3/3] Starting WeatherSense AI Server...
echo.
echo ══════════════════════════════════════════════════════════════════════════════════════════
echo  🟢 Server Starting on: http://localhost:5000
echo.
echo  Pages:
echo    🏠 Dashboard        →  http://localhost:5000/
echo    📅 15-Day Forecast  →  http://localhost:5000/forecast
echo    🌊 Coastal Alerts   →  http://localhost:5000/coastal
echo    🗺️  Risk Map         →  http://localhost:5000/map
echo    🤖 AI Weather Tutor →  http://localhost:5000/tutor
echo.
echo  🆘 Emergency Numbers:
echo    National Emergency: 112
echo    NDRF Flood Rescue:  1800-180-4188
echo    Coast Guard:        1554
echo.
echo  Press Ctrl+C to stop the server
echo ══════════════════════════════════════════════════════════════════════════════════════════
echo.

REM Open browser after 2 seconds
start "" timeout /t 2 /nobreak >nul && start "" "http://localhost:5000"

REM Start Flask app
py app.py

pause
