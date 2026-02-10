@echo off
REM RheeWorks ForConvinience - Text Generator GUI Launcher
REM Rheehose (Rhee Creative) 2008-2026

cd /d %~dp0
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

python main.py
