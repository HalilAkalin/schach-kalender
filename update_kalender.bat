@echo off
cd /d "%~dp0"

echo Hole Aenderungen von GitHub...
git pull

echo Fuehre Python-Skript aus...
python kalender.py

echo Lade Aenderungen zu GitHub hoch...
git add .
git commit -m "Automatisches Update"
git push

echo Fertig!