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
import locale

def get_system_lang():
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith('ko'):
            return 'ko'
    except:
        pass
    return 'en'

try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# i18n Translations / 번역 정보
TRANSLATIONS = {
    'ko': {
        'subtitle': '가짜 타이핑 복사 / Fake Typing Copier',
        'select_source_btn': '원천 선택 / SELECT SOURCE',
        'select_target_btn': '대상 선택 / SELECT TARGET',
        'not_selected': '선택 안됨 / Not Selected',
        'ready': '준비 완료 / READY',
        'rec': '● 녹화 중 / REC',
        'start_rec': '녹화 시작 / START RECORDING',
        'stop_rec': '녹화 중지 / STOP RECORDING',
        'error': '오류 / Error',
        'target_empty_error': '대상 텍스트는 비어 있어야 합니다! / Target must be empty!',
        'source_select_title': '원천 텍스트 선택',
        'target_select_title': '대상 텍스트 선택'
    },
    'en': {
        'subtitle': 'Fake Typing Copier',
        'select_source_btn': 'SELECT SOURCE',
        'select_target_btn': 'SELECT TARGET',
        'not_selected': 'Not Selected',
        'ready': 'READY',
        'rec': '● REC',
        'start_rec': 'START RECORDING',
        'stop_rec': 'STOP RECORDING',
        'error': 'Error',
        'target_empty_error': 'Target must be empty!',
        'source_select_title': 'Select Source Text',
        'target_select_title': 'Select Target Text'
    }
}

current_lang = get_system_lang()

# ======================
# File Selection / 파일 선택
# ======================
def select_source():
    global source_path
    path = filedialog.askopenfilename(title=TRANSLATIONS[current_lang]['source_select_title'])
    if path:
        source_path = path
        source_label.configure(text=os.path.basename(source_path))
        check_ready()

def select_target():
    global target_path
    path = filedialog.asksaveasfilename(title=TRANSLATIONS[current_lang]['target_select_title'])

    if not path:
        return

    # Check if empty / 비어있는지 검사
    if os.path.exists(path) and os.path.getsize(path) > 0:
        messagebox.showerror(TRANSLATIONS[current_lang]['error'], TRANSLATIONS[current_lang]['target_empty_error'])
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

        status_badge.configure(text=TRANSLATIONS[current_lang]['rec'], text_color=COLORS["danger"])
        start_btn.configure(text=TRANSLATIONS[current_lang]['stop_rec'], fg_color=COLORS["danger"])

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    else:
        recording = False
        status_badge.configure(text=TRANSLATIONS[current_lang]['ready'], text_color=COLORS["success"])
        start_btn.configure(text=TRANSLATIONS[current_lang]['start_rec'], fg_color=COLORS["accent"])

        if listener:
            listener.stop()

def toggle_lang():
    global current_lang
    current_lang = 'en' if current_lang == 'ko' else 'ko'
    update_ui()

def update_ui():
    lang = TRANSLATIONS[current_lang]
    subtitle_label.configure(text=lang['subtitle'])
    source_btn.configure(text=lang['select_source_btn'])
    target_btn.configure(text=lang['select_target_btn'])
    if not source_path:
        source_label.configure(text=lang['not_selected'])
    if not target_path:
        target_label.configure(text=lang['not_selected'])
    
    if recording:
        status_badge.configure(text=lang['rec'])
        start_btn.configure(text=lang['stop_rec'])
    else:
        status_badge.configure(text=lang['ready'])
        start_btn.configure(text=lang['start_rec'])
    
    lang_btn.configure(text=current_lang.upper())

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
title_label.pack(pady=(15, 5))

# Language Toggle / 언어 토글
lang_btn = ctk.CTkButton(
    main_frame,
    text=current_lang.upper(),
    width=40,
    height=25,
    command=toggle_lang,
    fg_color="transparent",
    border_width=1,
    border_color=COLORS["accent"],
    text_color=COLORS["accent"]
)
lang_btn.place(relx=0.95, rely=0.05, anchor="ne")

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
    text=TRANSLATIONS[current_lang]['start_rec'], 
    state="disabled",
    command=start_record,
    fg_color="#444444",
    hover_color=COLORS["secondary"],
    corner_radius=15,
    height=45,
    font=("Inter", 14, "bold")
)
start_btn.pack(pady=20, padx=40, fill="x")

update_ui()

# Branding / 브랜딩
branding_label = ctk.CTkLabel(
    root, 
    text="© 2008-2026 Rheehose (Rhee Creative)", 
    font=("Inter", 10),
    text_color="#555555"
)
branding_label.pack(side="bottom", pady=10)

root.mainloop()
