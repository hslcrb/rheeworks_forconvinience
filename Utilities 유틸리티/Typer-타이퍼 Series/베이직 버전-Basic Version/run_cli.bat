@echo off
REM RheeWorks ForConvinience - Typer Basic CLI Launcher
REM Rheehose (Rhee Creative) 2008-2026

cd /d %~dp0
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

python cli.py %*
