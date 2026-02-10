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

# ======================
# Global State / 전역 상태
# ======================
source_path = ""  # 원천 텍스트 경로 / Source text path
target_path = ""  # 대상 텍스트 경로 / Target text path

buffer_text = ""  # 버퍼 텍스트 / Buffer text content
cursor = 0        # 현재 커서 위치 / Current cursor position
recording = False # 녹화 상태 / Recording status
listener = None   # 키보드 리스너 / Keyboard listener


# ======================
# File Selection / 파일 선택
# ======================
def select_source():
    global source_path
    source_path = filedialog.askopenfilename(title="원천 텍스트 선택")
    source_label.config(text=os.path.basename(source_path))
    check_ready()


def select_target():
    global target_path

    path = filedialog.asksaveasfilename(title="대상 텍스트 선택")

    if not path:
        return

    # 비어있는지 검사
    if os.path.exists(path) and os.path.getsize(path) > 0:
        messagebox.showerror("오류", "대상 텍스트는 비어 있어야 합니다!")
        return

    open(path, "w", encoding="utf-8").close()

    target_path = path
    target_label.config(text=os.path.basename(target_path))
    check_ready()


def check_ready():
    if source_path and target_path:
        start_btn.config(state=tk.NORMAL)


# ======================
# Keyboard Input Handler / 키 입력 처리
# ======================
def on_press(key):
    global cursor

    if not recording:
        return

    # 단축키 제외 (ctrl, alt 등 무시)
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
        with open(source_path, "r", encoding="utf-8") as f:
            buffer_text = f.read()

        cursor = 0
        recording = True

        status_label.config(text="🔴 REC", fg="red")
        start_btn.config(text="STOP")

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    else:
        recording = False
        status_label.config(text="STOPPED", fg="black")
        start_btn.config(text="START")

        if listener:
            listener.stop()


# ======================
# GUI Setup / GUI 설정
# ======================
root = tk.Tk()
root.title("Fake Typing Copier")
root.geometry("400x200")

tk.Button(root, text="원천텍스트 선택", command=select_source).pack(pady=5)
source_label = tk.Label(root, text="선택 안됨")
source_label.pack()

tk.Button(root, text="대상텍스트 선택 (빈 파일)", command=select_target).pack(pady=5)
target_label = tk.Label(root, text="선택 안됨")
target_label.pack()

start_btn = tk.Button(root, text="START", state=tk.DISABLED, command=start_record)
start_btn.pack(pady=10)

status_label = tk.Label(root, text="READY")
status_label.pack()

root.mainloop()
