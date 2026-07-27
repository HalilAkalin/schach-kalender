@echo off
cd /d "%~dp0"

echo Fuehre Python-Skript aus...
python kalender.py

echo Lade Aenderungen zu GitHub hoch...
git add .
git commit -m "Automatisches Update"
git push

echo Fertig!
pause