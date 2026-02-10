#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Typer - Pomodoro Version / 타이퍼 - 포모도로 버전
집중 타이머 프로 + 숨겨진 타이핑 도구 / Focus Timer Pro + Hidden Typing Tool

Copyright (c) 2008-2026 Rheehose (Rhee Creative)
Licensed under the Apache License, Version 2.0
Website: https://rheehose.com
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import time
import threading
import random
import os

from pynput import keyboard
from tzlocal import get_localzone
from datetime import datetime


# =========================================
# Global State / 전역 상태
# =========================================
source_path = ""  # 원천 텍스트 경로 / Source text path
target_path = ""  # 대상 텍스트 경로 / Target text path
buffer_text = ""  # 버퍼 텍스트 / Buffer text content
cursor = 0        # 현재 커서 위치 / Current cursor position
recording = False # 녹화 상태 / Recording status
listener = None   # 키보드 리스너 / Keyboard listener

work_seconds = 25 * 60  # 포모도로 작업 시간 / Pomodoro work duration (seconds)
running = False         # 타이머 실행 상태 / Timer running status


# =========================================
# Fake Typing Engine / 가짜 타이핑 엔진
# =========================================

def on_press(key):
    global cursor

    if not recording:
        return

    try:
        if not key.char:
            return
    except:
        return

    if cursor >= len(buffer_text):
        return

    count = random.randint(1, 5)
    chunk = buffer_text[cursor:cursor+count]
    cursor += count

    with open(target_path, "a", encoding="utf-8") as f:
        f.write(chunk)


def start_fake_typing():
    global buffer_text, cursor, recording, listener

    if not source_path or not target_path:
        messagebox.showerror("오류", "파일 먼저 선택하세요")
        return

    with open(source_path, "r", encoding="utf-8") as f:
        buffer_text = f.read()

    cursor = 0
    recording = True

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    rec_label.config(text="🔴 REC", fg="red")


def stop_fake_typing():
    global recording, listener
    recording = False
    rec_label.config(text="STOPPED", fg="black")
    if listener:
        listener.stop()


# =========================================
# Pomodoro Timer UI / 포모도로 타이머 UI
# =========================================

def format_time(s):
    m = s // 60
    s %= 60
    return f"{m:02}:{s:02}"


def timer_loop():
    global work_seconds, running

    while running and work_seconds >= 0:
        timer_label.config(text=format_time(work_seconds))
        time.sleep(1)
        work_seconds -= 1


def start_timer():
    global running, work_seconds
    if running:
        return

    running = True
    work_seconds = 25 * 60

    threading.Thread(target=timer_loop, daemon=True).start()


def stop_timer():
    global running
    running = False


# =========================================
# Timezone Clock / 타임존 시계
# =========================================

def update_clock():
    tz = get_localzone()
    now = datetime.now(tz)
    clock_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
    root.after(1000, update_clock)


# =========================================
# Secret Room / 비밀 방
# =========================================

def open_secret():
    main_frame.pack_forget()
    secret_frame.pack(fill="both", expand=True)


def back_main():
    secret_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)


def select_source():
    global source_path
    source_path = filedialog.askopenfilename()
    src_label.config(text=os.path.basename(source_path))


def select_target():
    global target_path
    path = filedialog.asksaveasfilename()

    if os.path.exists(path) and os.path.getsize(path) > 0:
        messagebox.showerror("오류", "빈 파일만 가능")
        return

    open(path, "w").close()
    target_path = path
    tgt_label.config(text=os.path.basename(target_path))


# =========================================
# GUI Setup / GUI 설정
# =========================================

root = tk.Tk()
root.title("Focus Timer Pro")
root.geometry("420x500")


# ---------- MAIN (Fake Pomodoro) ----------
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

tk.Label(main_frame, text="🍅 Focus Timer", font=("Arial", 20)).pack(pady=10)

clock_label = tk.Label(main_frame, font=("Consolas", 12))
clock_label.pack()

timer_label = tk.Label(main_frame, text="25:00", font=("Arial", 48))
timer_label.pack(pady=20)

tk.Button(main_frame, text="START", width=15, command=start_timer).pack(pady=5)
tk.Button(main_frame, text="STOP", width=15, command=stop_timer).pack(pady=5)

# 👇 일부러 누르고 싶게 만드는 버튼
tk.Button(
    main_frame,
    text="🚫 누르지 마세요 🚫",
    fg="red",
    command=open_secret
).pack(pady=40)



# ---------- SECRET ----------
secret_frame = tk.Frame(root)

tk.Label(secret_frame, text="🕵 Secret Console", font=("Arial", 18)).pack(pady=10)

tk.Button(secret_frame, text="원천텍스트 선택", command=select_source).pack()
src_label = tk.Label(secret_frame, text="None")
src_label.pack()

tk.Button(secret_frame, text="대상텍스트 선택", command=select_target).pack()
tgt_label = tk.Label(secret_frame, text="None")
tgt_label.pack()

tk.Button(secret_frame, text="Start Fake Typing", command=start_fake_typing).pack(pady=5)
tk.Button(secret_frame, text="Stop", command=stop_fake_typing).pack()

rec_label = tk.Label(secret_frame, text="READY")
rec_label.pack(pady=10)

tk.Button(secret_frame, text="← 돌아가기", command=back_main).pack(pady=20)


update_clock()
root.mainloop()
