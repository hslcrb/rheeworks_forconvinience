#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Lavendar - Laboratory File Auto-Backup Tool
# Lavendar - 실습실 파일 자동 백업 도구
# Rheehose (Rhee Creative) 2008-2026
# Licensed under Apache-2.0

import os
import shutil
import time
import threading
import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

class Lavendar(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration / 설정 ---
        self.title("LAVENDAR")
        self.geometry("900x650")
        ctk.set_appearance_mode("dark")
        
        # Colors / 색상
        self.bg_color = "#0d1117"
        self.card_color = "#161b22"
        self.accent_color = "#238636" # Success Green
        self.secondary_color = "#21262d"
        self.text_color = "#c9d1d9"
        self.dim_text = "#8b949e"
        
        self.configure(fg_color=self.bg_color)
        
        # State / 상태
        self.source_dir = ""
        self.dest_dir = ""
        self.is_running = False
        self.interval_min = 5
        self.last_backup = "None"
        
        # UI Setup / UI 구축
        self.setup_ui()

    def setup_ui(self):
        # Sidebar / 사이드바
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.card_color, border_width=1, border_color="#30363d")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="LAVENDAR", font=("Inter", 28, "bold"), text_color=self.accent_color).pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="BACKUP", font=("Inter", 12), text_color=self.dim_text).pack(pady=(0, 30))

        # Copyright
        ctk.CTkLabel(self.sidebar, text="© 2008-2026\nRheehose (Rhee Creative)", font=("Inter", 10), text_color=self.dim_text).pack(side="bottom", pady=20)

        # Main Content Area / 메인 콘텐츠 영역
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="right", expand=True, fill="both", padx=30, pady=30)
        
        # Header / 헤더
        ctk.CTkLabel(self.content, text="Automatic Safeguard", font=("Inter", 24, "bold"), text_color=self.text_color).pack(anchor="w", pady=(0, 20))

        # Config Card / 설정 카드
        self.config_card = ctk.CTkFrame(self.content, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        self.config_card.pack(fill="x", pady=10)
        
        # Source Selection
        self.create_path_selector(self.config_card, "Source Directory (실습 파일 폴더)", self.select_source, "source")
        # Destination Selection
        self.create_path_selector(self.config_card, "Backup Destination (백업 대상 폴더/USB)", self.select_dest, "dest")
        
        # Settings Row
        self.settings_row = ctk.CTkFrame(self.config_card, fg_color="transparent")
        self.settings_row.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.settings_row, text="Interval (분):", font=("Inter", 13)).pack(side="left", padx=(0, 10))
        self.interval_spin = ctk.CTkEntry(self.settings_row, width=60, fg_color=self.secondary_color, border_color="#30363d")
        self.interval_spin.insert(0, "5")
        self.interval_spin.pack(side="left")
        
        self.btn_toggle = ctk.CTkButton(self.settings_row, text="ACTIVATE PROTECT", command=self.toggle_backup, fg_color=self.accent_color, hover_color="#2ea043", font=("Inter", 13, "bold"), height=40)
        self.btn_toggle.pack(side="right")

        # Status Card / 상태 카드
        self.status_card = ctk.CTkFrame(self.content, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        self.status_card.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(self.status_card, text="LIVE LOGS", font=("Inter", 12, "bold"), text_color=self.dim_text).pack(anchor="w", padx=20, pady=(15, 5))
        
        self.log_view = ctk.CTkTextbox(self.status_card, fg_color="transparent", font=("JetBrains Mono", 11), text_color="#7ee787")
        self.log_view.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_view.insert("end", ">>> System Ready. Waiting for activation...\n")
        self.log_view.configure(state="disabled")

    def create_path_selector(self, parent, label_text, command, attr_name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(frame, text=label_text, font=("Inter", 12, "bold"), text_color=self.dim_text).pack(anchor="w")
        
        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill="x", pady=5)
        
        entry = ctk.CTkEntry(inner_frame, placeholder_text="Path not selected...", fg_color=self.secondary_color, border_color="#30363d")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        setattr(self, f"{attr_name}_entry", entry)
        
        ctk.CTkButton(inner_frame, text="Browse", width=80, command=command, fg_color=self.secondary_color, hover_color="#30363d").pack(side="right")

    def select_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_dir = path
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, path)

    def select_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_dir = path
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, path)

    def log(self, message):
        self.log_view.configure(state="normal")
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        self.log_view.insert("end", f"{timestamp} {message}\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def toggle_backup(self):
        if not self.is_running:
            if not self.source_dir or not self.dest_dir:
                messagebox.showwarning("Warning", "Select both source and destination folders!")
                return
            
            try:
                self.interval_min = int(self.interval_spin.get())
            except ValueError:
                messagebox.showerror("Error", "Interval must be a number!")
                return

            self.is_running = True
            self.btn_toggle.configure(text="DEACTIVATE", fg_color="#f85149", hover_color="#da3633")
            self.log("Backup Protection Activated.")
            threading.Thread(target=self.backup_loop, daemon=True).start()
        else:
            self.is_running = False
            self.btn_toggle.configure(text="ACTIVATE PROTECT", fg_color=self.accent_color, hover_color="#2ea043")
            self.log("Backup Protection Deactivated.")

    def backup_loop(self):
        while self.is_running:
            try:
                # Create timestamped folder / 타임스탬프 폴더 생성
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = os.path.join(self.dest_dir, f"backup_{now}")
                
                self.log(f"Starting backup to {os.path.basename(target_path)}...")
                shutil.copytree(self.source_dir, target_path)
                self.log("Backup Successful.")
                
                # Cleanup old backups (keep last 10) / 오래된 백업 정리 (최근 10개 유지)
                self.cleanup_old_backups()
                
            except Exception as e:
                self.log(f"ERROR: {str(e)}")
            
            # Wait for interval / 주기 대기
            for _ in range(self.interval_min * 60):
                if not self.is_running: break
                time.sleep(1)

    def cleanup_old_backups(self):
        try:
            backups = [os.path.join(self.dest_dir, d) for d in os.listdir(self.dest_dir) if d.startswith("backup_")]
            backups.sort(key=os.path.getmtime)
            
            while len(backups) > 10:
                oldest = backups.pop(0)
                shutil.rmtree(oldest)
                self.log(f"Removed old backup: {os.path.basename(oldest)}")
        except:
            pass

if __name__ == "__main__":
    app = Lavendar()
    app.mainloop()
