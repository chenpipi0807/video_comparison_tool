@echo off
echo Installing required packages...
pip install pyinstaller Pillow

echo Creating icon...
python create_icon.py

echo Creating executable...
python -m PyInstaller --onefile --windowed --icon=logo.ico --name "VideoComparisonTool" video_comparison_tool.py

echo Creating distribution package...
mkdir "VideoComparisonTool" 2>nul
xcopy /Y /E /I "dist\VideoComparisonTool.exe" "VideoComparisonTool\"
copy /Y logo.ico "VideoComparisonTool\"
copy /Y README.md "VideoComparisonTool\"

powershell Compress-Archive -Path VideoComparisonTool -DestinationPath VideoComparisonTool.zip -Force

echo.
echo =============================================
echo Packaging complete!
echo Executable is in the 'dist' folder: dist\VideoComparisonTool.exe
echo Complete distribution package created as: VideoComparisonTool.zip
echo =============================================
pause
