@echo off
echo "Building"
python -m PyInstaller --onefile --name Speedtest_GUI --windowed --add-data "bin;bin" gui.py
echo "Build terminata"
PAUSE