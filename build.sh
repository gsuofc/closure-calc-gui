#!/bin/sh
here="`dirname \"$0\"`"
cd "$here" || exit 1
python3 gen_version_number.py
python3 -m PyInstaller --onefile -w closure-calc.py