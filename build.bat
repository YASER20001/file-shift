@echo off
echo Installing dependencies...
pip install openpyxl pyinstaller

echo Building Videos Works...
pyinstaller --onefile --windowed --name "VideosWorks" app.py

echo.
echo Done! Your exe is in the "dist" folder.
pause
