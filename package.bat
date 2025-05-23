@echo off
echo Installing required packages...
pip install pyinstaller Pillow

echo Creating logo...
python create_logo.py

echo Creating executable...
pyinstaller --onefile --windowed --icon=logo.ico ^
    --add-data "logo.ico;." ^
    --name "VideoComparisonTool" ^
    video_comparison_tool.py

echo Done! The executable is in the 'dist' folder.
pause
