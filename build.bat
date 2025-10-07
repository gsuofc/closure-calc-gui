@echo off
cd /d "%~dp0"
python gen_version_number.py
python -m PyInstaller --onefile -w closure-calc.py
pause