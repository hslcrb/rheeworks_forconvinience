#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automaker - Clicker / 오토메이커 - 클리커
프리미엄 오토 클릭커 도구 / Premium Auto-Clicker Tool

Copyright (c) 2008-2026 Rheehose (Rhee Creative)
Licensed under the Apache License, Version 2.0
Website: https://rheehose.com
"""

import time
import threading
import random
import os
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

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
delay = 0.1
button = Button.left
start_stop_key = KeyCode(char='s')
stop_key = KeyCode(char='e')

# Premium Color Palette / 프리미엄 컬러 팔레트
COLORS = {
    "bg": "#121212",
    "card": "#1E1E1E",
    "accent": "#F1C40F",    # Premium Yellow
    "secondary": "#F39C12",
    "success": "#2ECC71",
    "danger": "#E74C3C",
    "text": "#ECf0F1"
}

class ClickMouse(threading.Thread):
    def __init__(self, delay, button):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        mouse = Controller()
        while self.program_running:
            while self.running:
                mouse.click(self.button)
                time.sleep(self.delay)
            time.sleep(0.1)

mouse_clicker = ClickMouse(delay, button)
mouse_clicker.start()

def on_press(key):
    if key == start_stop_key:
        if mouse_clicker.running:
            mouse_clicker.stop_clicking()
            update_ui_state(False)
        else:
            mouse_clicker.start_clicking()
            update_ui_state(True)
    elif key == stop_key:
        mouse_clicker.exit()
        listener.stop()
        root.quit()

# ======================
# UI Functions / UI 기능
# ======================
def update_delay(val):
    global delay
    delay = float(val)
    mouse_clicker.delay = delay
    delay_label.configure(text=f"DELAY: {delay:.2f}s")

def update_ui_state(is_running):
    if is_running:
        status_badge.configure(text="● RUNNING", text_color=COLORS["accent"])
        start_btn.configure(text="STOP (S)", fg_color=COLORS["danger"])
    else:
        status_badge.configure(text="IDLE", text_color=COLORS["success"])
        start_btn.configure(text="START (S)", fg_color=COLORS["accent"])

def toggle_clicking():
    if mouse_clicker.running:
        mouse_clicker.stop_clicking()
        update_ui_state(False)
    else:
        # Update delay before starting
        try:
            d = float(delay_entry.get())
            update_delay(d)
        except:
            pass
        mouse_clicker.start_clicking()
        update_ui_state(True)

# ======================
# GUI Setup / GUI 설정
# ======================
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Automaker Clicker - RheeWorks")
root.geometry("450x450")
root.configure(fg_color=COLORS["bg"])

main_frame = ctk.CTkFrame(root, corner_radius=25, fg_color=COLORS["card"])
main_frame.pack(padx=30, pady=30, fill="both", expand=True)

# Title
ctk.CTkLabel(
    main_frame, 
    text="CLICKER PRO", 
    font=("Inter", 28, "bold"),
    text_color=COLORS["accent"]
).pack(pady=(25, 5))

ctk.CTkLabel(
    main_frame, 
    text="Mouse Automation Tool / 마우스 자동화", 
    font=("Inter", 12),
    text_color="#666666"
).pack()

# Control Card
control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
control_frame.pack(pady=30, padx=40, fill="x")

delay_label = ctk.CTkLabel(control_frame, text="DELAY: 0.10s", font=("JetBrains Mono", 14, "bold"))
delay_label.pack()

delay_slider = ctk.CTkSlider(
    control_frame, 
    from_=0.01, 
    to=1.0, 
    number_of_steps=100,
    button_color=COLORS["accent"],
    button_hover_color=COLORS["secondary"],
    command=update_delay
)
delay_slider.set(0.1)
delay_slider.pack(fill="x", pady=15)

# Status
status_badge = ctk.CTkLabel(
    main_frame, 
    text="IDLE", 
    font=("JetBrains Mono", 16, "bold"),
    text_color=COLORS["success"]
)
status_badge.pack(pady=10)

# Start/Stop Button
start_btn = ctk.CTkButton(
    main_frame, 
    text="START (S)", 
    font=("Inter", 16, "bold"),
    fg_color=COLORS["accent"],
    text_color=COLORS["bg"],
    hover_color=COLORS["secondary"],
    corner_radius=15,
    height=55,
    command=toggle_clicking
)
start_btn.pack(pady=20, padx=50, fill="x")

# Info
info_label = ctk.CTkLabel(
    main_frame, 
    text="Press 'S' to Start/Stop, 'E' to Exit\n'S'는 시작/정지, 'E'는 종료", 
    font=("Inter", 11),
    text_color="#444444"
)
info_label.pack(side="bottom", pady=20)

# Branding
ctk.CTkLabel(
    root, 
    text="© 2008-2026 Rheehose (Rhee Creative)", 
    font=("Inter", 10),
    text_color="#333333"
).pack(side="bottom", pady=5)

# Keyboard Listener
listener = Listener(on_press=on_press)
listener.start()

root.mainloop()
