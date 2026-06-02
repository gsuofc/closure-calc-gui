#!/bin/sh
here="`dirname \"$0\"`"
cd "$here" || exit 1
python3 gen_version_number.py "build.sh"
python3 -m PyInstaller --onefile -w closure-calc.py --add-data "icon.ico:." --icon=icon.icns --add-data "icon.png:."