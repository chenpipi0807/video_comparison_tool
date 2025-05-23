@echo off
echo Installing required packages...
pip install pyinstaller Pillow

echo Creating icon...
python create_icon.py

echo Creating executable...
pyinstaller --onefile --windowed --icon=logo.ico --name "VideoComparisonTool" video_comparison_tool.py

echo Creating distribution package...
mkdir "VideoComparisonTool" 2>nul
xcopy /Y /E /I "dist\VideoComparisonTool.exe" "VideoComparisonTool\"
copy /Y logo.ico "VideoComparisonTool\"
copy /Y README.md "VideoComparisonTool\"

powershell Compress-Archive -Path VideoComparisonTool -DestinationPath VideoComparisonTool.zip -Force

echo.
echo =============================================
echo 打包完成！
echo 可执行文件在 dist 文件夹中：dist\VideoComparisonTool.exe
echo 完整的发布包已创建为：VideoComparisonTool.zip
echo =============================================
pause
