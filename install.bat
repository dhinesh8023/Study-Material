@echo off
cd /d "%~dp0"
echo Installing StudyShare dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Installation failed.
    pause
    exit /b 1
)
echo.
echo Installation complete!
echo Start the app with: python app.py
pause
