#!/ reentry/env python3
# -*- coding: utf-8 -*-
# Pris CLI - Study/Coding Time Tracker
# Rheehose (Rhee Creative) 2008-2026

import os
import sqlite3
import datetime
import time
import sys
import locale

def get_msg(ko_msg, en_msg):
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith('ko'):
            return f"{ko_msg} / {en_msg}"
    except:
        pass
    return en_msg

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
    print(f"      {get_msg('PRIS CLI - 생산성 통계', 'PRIS CLI - PRODUCTIVITY STATS')}")
    print("="*40)
    
    # Today
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT SUM(duration_sec) FROM sessions WHERE date = ?", (today,))
    total_today = cursor.fetchone()[0] or 0
    print(f"{get_msg('오늘', 'TODAY')}: {time.strftime('%H:%M:%S', time.gmtime(total_today))}")
    
    # Week
    week_start = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    cursor.execute("SELECT SUM(duration_sec) FROM sessions WHERE date >= ?", (week_start,))
    total_week = cursor.fetchone()[0] or 0
    print(f"{get_msg('이번 주', 'THIS WEEK')}: {total_week/3600:.1f} hrs")
    
    # Logs
    print(f"\n--- {get_msg('최근 기록', 'RECENT LOGS')} ---")
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
    print(f"\n>>> {get_msg('타이머 시작', 'Timer STARTS')} [{project}] at {start_time.strftime('%H:%M:%S')}")
    print(get_msg("세션을 중지하려면 Ctrl+C를 누르세요.", "Press Ctrl+C to STOP session."))
    
    try:
        while True:
            delta = datetime.datetime.now() - start_time
            sys.stdout.write(f"\r{get_msg('경과 시간', 'Elapsed Time')}: {str(delta).split('.')[0]}")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        end_time = datetime.datetime.now()
        duration = int((end_time - start_time).total_seconds())
        print(f"\n\n>>> {get_msg('타이머 중지', 'Timer STOPPED')}. {get_msg('지속 시간', 'Duration')}: {duration} seconds.")
        
        if duration > 10:
            cursor.execute('''
                INSERT INTO sessions (project, start_time, end_time, duration_sec, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (project, start_time.isoformat(), end_time.isoformat(), duration, start_time.date().isoformat()))
            conn.commit()
            print(get_msg("세션이 성공적으로 저장되었습니다.", "Session saved successfully."))
        else:
            print(get_msg("세션이 너무 짧아 저장되지 않았습니다.", "Session too short, not saved."))
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_stats()
        print(f"{get_msg('사용법', 'Usage')}: python3 cli.py [stats|start <project_name>]")
    elif sys.argv[1] == "stats":
        show_stats()
    elif sys.argv[1] == "start":
        name = sys.argv[2] if len(sys.argv) > 2 else "General"
        start_timer(name)
    else:
        print(get_msg("알 수 없는 명령입니다.", "Unknown command."))
