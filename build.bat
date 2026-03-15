@echo off
echo Installing dependencies...
pip install openpyxl pyinstaller

echo Building File Shift...
pyinstaller --onefile --windowed --name "FileShift" app.py

echo.
echo Done! Your exe is in the "dist" folder.
pause
