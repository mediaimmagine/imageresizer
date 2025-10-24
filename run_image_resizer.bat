@echo off
echo ====================================
echo    IMAGE RESIZER - Starting...
echo ====================================
echo.

REM Check if Pillow is installed, install if not
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo Installing required package: Pillow...
    python -m pip install Pillow
    echo.
)

echo Starting Image Resizer...
python image_resizer.py

if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)

