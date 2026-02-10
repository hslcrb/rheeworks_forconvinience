#!/ reentry/env python3
# -*- coding: utf-8 -*-
# Pris CLI - Study/Coding Time Tracker
# Rheehose (Rhee Creative) 2008-2026

import os
import sqlite3
import datetime
import time
import sys

def init_db():
    conn = sqlite3.connect("rucia_stats.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_sec INTEGER,
            date DATE
        )
    ''')
    conn.commit()
    return conn

def show_stats():
    conn = init_db()
    cursor = conn.cursor()
    
    print("\n" + "="*40)
    print("      PRIS CLI - PRODUCTIVITY STATS")
    print("="*40)
    
    # Today
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT SUM(duration_sec) FROM sessions WHERE date = ?", (today,))
    total_today = cursor.fetchone()[0] or 0
    print(f"TODAY: {time.strftime('%H:%M:%S', time.gmtime(total_today))}")
    
    # Week
    week_start = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    cursor.execute("SELECT SUM(duration_sec) FROM sessions WHERE date >= ?", (week_start,))
    total_week = cursor.fetchone()[0] or 0
    print(f"THIS WEEK: {total_week/3600:.1f} hrs")
    
    # Logs
    print("\n--- RECENT LOGS ---")
    cursor.execute("SELECT project, duration_sec, date FROM sessions ORDER BY id DESC LIMIT 5")
    for row in cursor.fetchall():
        m, s = divmod(row[1], 60)
        h, m = divmod(m, 60)
        print(f"[{row[2]}] {row[0]:<15} | {h:02}:{m:02}:{s:02}")
    print("="*40 + "\n")
    conn.close()

def start_timer(project):
    conn = init_db()
    cursor = conn.cursor()
    
    start_time = datetime.datetime.now()
    print(f"\n>>> Timer STARTS for [{project}] at {start_time.strftime('%H:%M:%S')}")
    print("Press Ctrl+C to STOP session.")
    
    try:
        while True:
            delta = datetime.datetime.now() - start_time
            sys.stdout.write(f"\rElapsed Time: {str(delta).split('.')[0]}")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        end_time = datetime.datetime.now()
        duration = int((end_time - start_time).total_seconds())
        print(f"\n\n>>> Timer STOPPED. Duration: {duration} seconds.")
        
        if duration > 10:
            cursor.execute('''
                INSERT INTO sessions (project, start_time, end_time, duration_sec, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (project, start_time.isoformat(), end_time.isoformat(), duration, start_time.date().isoformat()))
            conn.commit()
            print("Session saved successfully.")
        else:
            print("Session too short, not saved.")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_stats()
        print("Usage: python3 cli.py [stats|start <project_name>]")
    elif sys.argv[1] == "stats":
        show_stats()
    elif sys.argv[1] == "start":
        name = sys.argv[2] if len(sys.argv) > 2 else "General"
        start_timer(name)
    else:
        print("Unknown command.")
