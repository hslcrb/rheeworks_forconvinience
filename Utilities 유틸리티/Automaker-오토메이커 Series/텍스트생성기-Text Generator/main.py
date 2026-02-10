#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automaker - Text Generator / 오토메이커 - 텍스트생성기
더미 텍스트 생성 도구 / Dummy Text Generation Tool

Copyright (c) 2008-2026 Rheehose (Rhee Creative)
Licensed under the Apache License, Version 2.0
"""

import random
import os
import tkinter as tk
from tkinter import messagebox

try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# ======================
# Data / 데이터
# ======================
LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

KOREAN_DUMMY = "여우비 내리는 날에는 꽃들이 노래를 부르고, 푸른 바다 건너편에는 은하수가 흐릅니다. 가을 바람 소리에 귀를 기울이면 옛이야기가 들려오고, 아침 햇살은 창가에 머무르며 새로운 시작을 알립니다."

# HSL Colors
COLORS = {
    "bg": "#0D1117",
    "card": "#161B22",
    "accent": "#58A6FF",    # GitHub Blue
    "secondary": "#1F6FEB",
    "text": "#C9D1D9",
    "success": "#238636"
}

# ======================
# Logic / 로직
# ======================
def generate_text():
    mode = mode_var.get()
    try:
        count = int(count_entry.get())
    except:
        count = 1
        
    base_text = LOREM_IPSUM if mode == "Latin" else KOREAN_DUMMY
    words = base_text.split()
    
    result = []
    for _ in range(count):
        chunk = random.sample(words, min(len(words), random.randint(5, 15)))
        result.append(" ".join(chunk))
        
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "\n\n".join(result))

def copy_to_clipboard():
    content = output_text.get("1.0", tk.END).strip()
    if content:
        root.clipboard_clear()
        root.clipboard_append(content)
        messagebox.showinfo("복사 / Copy", "클립보드에 복사되었습니다! / Copied to clipboard!")

# ======================
# GUI Setup / GUI 설정
# ======================
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Text Gen Pro - RheeWorks")
root.geometry("600x500")
root.configure(fg_color=COLORS["bg"])

main_frame = ctk.CTkFrame(root, corner_radius=20, fg_color=COLORS["card"])
main_frame.pack(padx=30, pady=30, fill="both", expand=True)

# Title
ctk.CTkLabel(
    main_frame, 
    text="TEXT GENERATOR", 
    font=("Inter", 26, "bold"),
    text_color=COLORS["accent"]
).pack(pady=(20, 5))

ctk.CTkLabel(
    main_frame, 
    text="Universal Dummy Text Tool / 더미 텍스트 도구", 
    font=("Inter", 12),
    text_color="#8b949e"
).pack()

# Input Group
input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
input_frame.pack(pady=20, padx=40, fill="x")

mode_var = ctk.StringVar(value="Korean")
mode_switch = ctk.CTkSegmentedButton(
    input_frame, 
    values=["Korean", "Latin"],
    variable=mode_var,
    selected_color=COLORS["accent"],
    selected_hover_color=COLORS["secondary"],
    unselected_color="#21262d"
)
mode_switch.pack(pady=10)

count_entry = ctk.CTkEntry(
    input_frame, 
    placeholder_text="Paragraph Count (ex: 3)",
    fg_color="#0d1117",
    border_color="#30363d"
)
count_entry.pack(fill="x", pady=5)

# Actions
btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
btn_frame.pack(fill="x", padx=40)

gen_btn = ctk.CTkButton(
    btn_frame, 
    text="GENERATE", 
    command=generate_text,
    fg_color=COLORS["accent"],
    hover_color=COLORS["secondary"],
    text_color="white",
    font=("Inter", 13, "bold")
)
gen_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

copy_btn = ctk.CTkButton(
    btn_frame, 
    text="COPY ALL", 
    command=copy_to_clipboard,
    fg_color="#21262d",
    hover_color="#30363d",
    font=("Inter", 13, "bold")
)
copy_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

# Output
output_text = ctk.CTkTextbox(
    main_frame, 
    fg_color="#0d1117", 
    text_color=COLORS["text"],
    border_color="#30363d",
    border_width=1,
    font=("Inter", 12)
)
output_text.pack(pady=20, padx=40, fill="both", expand=True)

# Branding
ctk.CTkLabel(
    root, 
    text="© 2008-2026 Rheehose (Rhee Creative)", 
    font=("Inter", 10),
    text_color="#484f58"
).pack(side="bottom", pady=10)

root.mainloop()
