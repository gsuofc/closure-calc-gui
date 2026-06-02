@echo off
cd /d "%~dp0"
python gen_version_number.py "build.bat"
python -m PyInstaller --onefile -w closure-calc.py --icon=icon.ico --add-data "icon.ico;." --add-data "icon.png;."
pause