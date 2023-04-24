@echo off
git fetch --all
git reset --hard origin/main
pip install -r requirements.txt
start "" /B pythonw "main.py"
exit