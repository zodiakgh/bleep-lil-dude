@echo off
pip install pyinstaller
pyinstaller --onefile --noconsole --name Bleep bleep.py
echo.
echo Done: dist\Bleep.exe
pause
