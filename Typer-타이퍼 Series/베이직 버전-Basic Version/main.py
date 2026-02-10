#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Typer - Basic Version / 타이퍼 - 베이직 버전
가짜 타이핑 복사 도구 / Fake Typing Copier

Copyright (c) 2008-2026 Rheehose (Rhee Creative)
Licensed under the Apache License, Version 2.0
Website: https://rheehose.com
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import random
from pynput import keyboard
import threading
import os

try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# ======================
# Global State / 전역 상태
# ======================
source_path = ""  # 원천 텍스트 경로 / Source text path
target_path = ""  # 대상 텍스트 경로 / Target text path

buffer_text = ""  # 버퍼 텍스트 / Buffer text content
cursor = 0        # 현재 커서 위치 / Current cursor position
recording = False # 녹화 상태 / Recording status
listener = None   # 키보드 리스너 / Keyboard listener

# HSL-inspired Color Palette / HSL 기반 컬러 팔레트
COLORS = {
    "bg": "#121212",        # Deep dark
    "card": "#1E1E1E",      # Soft dark card
    "accent": "#6C5CE7",    # Premium Purple
    "secondary": "#A29BFE", # Light Purple
    "success": "#00B894",   # Mint Green
    "danger": "#D63031",    # Soft Red
    "text": "#F5F5F5"       # Off-white
}

# ======================
# File Selection / 파일 선택
# ======================
def select_source():
    global source_path
    path = filedialog.askopenfilename(title="원천 텍스트 선택")
    if path:
        source_path = path
        source_label.configure(text=os.path.basename(source_path))
        check_ready()

def select_target():
    global target_path
    path = filedialog.asksaveasfilename(title="대상 텍스트 선택")

    if not path:
        return

    # Check if empty / 비어있는지 검사
    if os.path.exists(path) and os.path.getsize(path) > 0:
        messagebox.showerror("오류 / Error", "대상 텍스트는 비어 있어야 합니다! / Target must be empty!")
        return

    open(path, "w", encoding="utf-8").close()

    target_path = path
    target_label.configure(text=os.path.basename(target_path))
    check_ready()

def check_ready():
    if source_path and target_path:
        start_btn.configure(state="normal", fg_color=COLORS["accent"])

# ======================
# Keyboard Input Handler / 키 입력 처리
# ======================
def on_press(key):
    global cursor

    if not recording:
        return

    # Ignore shortcuts / 단축키 제외 (ctrl, alt 등 무시)
    try:
        if hasattr(key, 'char') and key.char:
            pass
        else:
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

# ======================
# Start/Stop Functions / 시작/정지
# ======================
def start_record():
    global recording, buffer_text, cursor, listener

    if not recording:
        if not source_path or not target_path:
            return

        with open(source_path, "r", encoding="utf-8") as f:
            buffer_text = f.read()

        cursor = 0
        recording = True

        status_badge.configure(text="● REC", text_color=COLORS["danger"])
        start_btn.configure(text="STOP RECORDING", fg_color=COLORS["danger"])

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    else:
        recording = False
        status_badge.configure(text="READY", text_color=COLORS["success"])
        start_btn.configure(text="START RECORDING", fg_color=COLORS["accent"])

        if listener:
            listener.stop()

# ======================
# GUI Setup / GUI 설정
# ======================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Typer Basic - RheeWorks")
root.geometry("500x350")
root.configure(fg_color=COLORS["bg"])

# Main Container / 메인 컨테이너
main_frame = ctk.CTkFrame(root, corner_radius=20, fg_color=COLORS["card"])
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Title / 제목
title_label = ctk.CTkLabel(
    main_frame, 
    text="TYPER BASIC", 
    font=("Inter", 24, "bold"),
    text_color=COLORS["accent"]
)
title_label.pack(pady=(20, 10))

# Subtitle / 부제목
subtitle_label = ctk.CTkLabel(
    main_frame, 
    text="Fake Typing Copier / 가짜 타이핑 복사", 
    font=("Inter", 12),
    text_color="#888888"
)
subtitle_label.pack(pady=(0, 20))

# File Section / 파일 섹션
file_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
file_frame.pack(fill="x", padx=30)

# Source File Button / 원천 파일 버튼
source_btn = ctk.CTkButton(
    file_frame, 
    text="SELECT SOURCE / 원천 선택", 
    command=select_source,
    fg_color="#333333",
    hover_color="#444444",
    corner_radius=10
)
source_btn.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

source_label = ctk.CTkLabel(file_frame, text="Not Selected / 선택 안됨", font=("Inter", 11))
source_label.grid(row=0, column=1, pady=5, sticky="w")

# Target File Button / 대상 파일 버튼
target_btn = ctk.CTkButton(
    file_frame, 
    text="SELECT TARGET / 대상 선택", 
    command=select_target,
    fg_color="#333333",
    hover_color="#444444",
    corner_radius=10
)
target_btn.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="ew")

target_label = ctk.CTkLabel(file_frame, text="Not Selected / 선택 안됨", font=("Inter", 11))
target_label.grid(row=1, column=1, pady=5, sticky="w")

file_frame.columnconfigure(0, weight=1)
file_frame.columnconfigure(1, weight=1)

# Status Badge / 상태 배지
status_badge = ctk.CTkLabel(
    main_frame, 
    text="READY", 
    font=("Inter", 14, "bold"),
    text_color=COLORS["success"]
)
status_badge.pack(pady=(20, 0))

# Start/Stop Button / 시작/정지 버튼
start_btn = ctk.CTkButton(
    main_frame, 
    text="START RECORDING", 
    state="disabled",
    command=start_record,
    fg_color="#444444",
    hover_color=COLORS["secondary"],
    corner_radius=15,
    height=45,
    font=("Inter", 14, "bold")
)
start_btn.pack(pady=20, padx=40, fill="x")

# Branding / 브랜딩
branding_label = ctk.CTkLabel(
    root, 
    text="© 2008-2026 Rheehose (Rhee Creative)", 
    font=("Inter", 10),
    text_color="#555555"
)
branding_label.pack(side="bottom", pady=10)

root.mainloop()
