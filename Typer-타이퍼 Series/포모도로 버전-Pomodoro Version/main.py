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

try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

from pynput import keyboard
from tzlocal import get_localzone
from datetime import datetime

# =========================================
# Global State / 전역 상태
# =========================================
source_path = ""
target_path = ""
buffer_text = ""
cursor = 0
recording = False
listener = None

work_seconds = 25 * 60
running = False

# Premium Color Palette / 프리미엄 컬러 팔레트
COLORS = {
    "bg": "#0F0F0F",
    "card": "#1A1A1A",
    "accent": "#FF4757",    # Tomato Red
    "accent_soft": "#FF6B81",
    "secret": "#2F3542",    # Dark Grey
    "text": "#FFFFFF",
    "success": "#2ED573"
}

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
        messagebox.showerror("오류 / Error", "파일 먼저 선택하세요 / Select files first")
        return
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            buffer_text = f.read()
    except Exception as e:
        messagebox.showerror("오류 / Error", str(e))
        return
    cursor = 0
    recording = True
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    rec_label.configure(text="● RECORDING", text_color=COLORS["accent"])
    ft_start_btn.configure(text="STOP ENGINE", fg_color=COLORS["accent"])

def stop_fake_typing():
    global recording, listener
    recording = False
    rec_label.configure(text="ENGINE STANDBY", text_color="#888888")
    ft_start_btn.configure(text="START ENGINE", fg_color=COLORS["secret"])
    if listener:
        listener.stop()

# =========================================
# Pomodoro Timer Logic / 포모도로 타이머 로직
# =========================================

def format_time(s):
    m = s // 60
    s %= 60
    return f"{m:02}:{s:02}"

def timer_loop():
    global work_seconds, running
    while running and work_seconds > 0:
        timer_label.configure(text=format_time(work_seconds))
        time.sleep(1)
        work_seconds -= 1
    if work_seconds <= 0:
        running = False
        timer_label.configure(text="00:00")
        messagebox.showinfo("Focus / 집중", "Time to rest! / 휴식 시간입니다!")

def start_timer():
    global running, work_seconds
    if running:
        return
    running = True
    work_seconds = 25 * 60
    threading.Thread(target=timer_loop, daemon=True).start()
    timer_start_btn.configure(text="STOP", fg_color=COLORS["accent"])

def stop_timer():
    global running
    running = False
    timer_start_btn.configure(text="START", fg_color=COLORS["accent"])

# =========================================
# UI Controllers / UI 컨트롤러
# =========================================

def update_clock():
    try:
        tz = get_localzone()
        now = datetime.now(tz)
        clock_label.configure(text=now.strftime("%Y-%m-%d %H:%M:%S"))
    except:
        pass
    root.after(1000, update_clock)

def open_secret():
    main_frame.pack_forget()
    secret_frame.pack(fill="both", expand=True)

def back_main():
    secret_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

def select_source():
    global source_path
    path = filedialog.askopenfilename()
    if path:
        source_path = path
        src_label.configure(text=os.path.basename(source_path))

def select_target():
    global target_path
    path = filedialog.asksaveasfilename()
    if path:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            messagebox.showerror("오류", "빈 파일만 가능")
            return
        open(path, "w").close()
        target_path = path
        tgt_label.configure(text=os.path.basename(target_path))

# =========================================
# GUI Setup / GUI 설정
# =========================================

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Focus Timer Pro - RheeWorks")
root.geometry("450x600")
root.configure(fg_color=COLORS["bg"])

# ---------- MAIN FRAME ----------
main_frame = ctk.CTkFrame(root, fg_color="transparent")
main_frame.pack(fill="both", expand=True, padx=30, pady=30)

tk_title = ctk.CTkLabel(main_frame, text="TOMATO FOCUS", font=("Inter", 28, "bold"), text_color=COLORS["accent"])
tk_title.pack(pady=(20, 5))

clock_label = ctk.CTkLabel(main_frame, text="0000-00-00 00:00:00", font=("JetBrains Mono", 14), text_color="#555555")
clock_label.pack()

timer_container = ctk.CTkFrame(main_frame, corner_radius=100, fg_color=COLORS["card"], width=250, height=250)
timer_container.pack_propagate(False)
timer_container.pack(pady=40)

timer_label = ctk.CTkLabel(timer_container, text="25:00", font=("Inter", 64, "bold"), text_color=COLORS["text"])
timer_label.place(relx=0.5, rely=0.5, anchor="center")

timer_start_btn = ctk.CTkButton(
    main_frame, 
    text="START", 
    font=("Inter", 16, "bold"),
    fg_color=COLORS["accent"],
    hover_color=COLORS["accent_soft"],
    corner_radius=20,
    height=50,
    command=lambda: start_timer() if not running else stop_timer()
)
timer_start_btn.pack(fill="x", padx=40)

secret_entry_btn = ctk.CTkButton(
    main_frame,
    text="🚫 DO NOT ENTER / 진입 금지",
    font=("Inter", 12),
    fg_color="transparent",
    text_color="#333333",
    hover=False,
    command=open_secret
)
secret_entry_btn.pack(side="bottom", pady=20)

# ---------- SECRET FRAME ----------
secret_frame = ctk.CTkFrame(root, fg_color=COLORS["bg"])

ctk.CTkLabel(secret_frame, text="ENGINE CONSOLE", font=("JetBrains Mono", 20, "bold"), text_color=COLORS["success"]).pack(pady=(30, 20))

sc_card = ctk.CTkFrame(secret_frame, fg_color=COLORS["card"], corner_radius=15)
sc_card.pack(fill="both", expand=True, padx=30, pady=10)

# File Buttons
ctk.CTkButton(sc_card, text="SOURCE FILE", fg_color=COLORS["secret"], corner_radius=10, command=select_source).pack(pady=(20, 5), padx=20, fill="x")
src_label = ctk.CTkLabel(sc_card, text="None Selected", font=("Inter", 11), text_color="#666666")
src_label.pack()

ctk.CTkButton(sc_card, text="TARGET FILE", fg_color=COLORS["secret"], corner_radius=10, command=select_target).pack(pady=(15, 5), padx=20, fill="x")
tgt_label = ctk.CTkLabel(sc_card, text="None Selected", font=("Inter", 11), text_color="#666666")
tgt_label.pack()

rec_label = ctk.CTkLabel(sc_card, text="ENGINE STANDBY", font=("JetBrains Mono", 12), text_color="#888888")
rec_label.pack(pady=20)

ft_start_btn = ctk.CTkButton(
    sc_card, 
    text="START ENGINE", 
    fg_color=COLORS["secret"], 
    hover_color=COLORS["success"],
    font=("Inter", 14, "bold"),
    command=lambda: start_fake_typing() if not recording else stop_fake_typing()
)
ft_start_btn.pack(pady=10, padx=20, fill="x")

ctk.CTkButton(secret_frame, text="← BACK TO FOCUS", fg_color="transparent", text_color="#555555", command=back_main).pack(pady=20)

update_clock()
root.mainloop()
