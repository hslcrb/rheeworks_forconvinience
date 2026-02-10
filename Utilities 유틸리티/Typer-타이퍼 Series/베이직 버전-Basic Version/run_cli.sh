#!/bin/bash
# RheeWorks ForConvinience - Typer Basic CLI Launcher
# Rheehose (Rhee Creative) 2008-2026

BASEDIR=$(dirname "$0")
cd "$BASEDIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 cli.py "$@"
