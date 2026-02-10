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
import locale

def get_system_lang():
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith('ko'):
            return 'ko'
    except:
        pass
    return 'en'
from PIL import Image

# i18n Translations / 번역 정보
TRANSLATIONS = {
    'ko': {
        'backup': '백업 / BACKUP',
        'safeguard': '자동 보호 시스템 / Automatic Safeguard',
        'source_label': '원천 디렉토리 (실습 파일 폴더) / Source Directory',
        'dest_label': '백업 대상 폴더 (USB 등) / Backup Destination',
        'interval': '주기 (분): / Interval (min):',
        'activate': '보호 활성화 / ACTIVATE PROTECT',
        'deactivate': '보호 비활성화 / DEACTIVATE',
        'logs': '실시간 로그 / LIVE LOGS',
        'path_not_selected': '경로가 선택되지 않음... / Path not selected...',
        'browse': '찾아보기 / Browse',
        'warning': '경고 / Warning',
        'select_both': '원천 폴더와 대상 폴더를 모두 선택하세요! / Select both source and destination folders!',
        'error': '오류 / Error',
        'interval_error': '주기는 숫자여야 합니다! / Interval must be a number!',
        'system_ready': '>>> 시스템 준비 완료. 활성화를 기다리는 중...\n',
        'activated': '백업 보호가 활성화되었습니다 / Backup Protection Activated.',
        'deactivated': '백업 보호가 비활성화되었습니다 / Backup Protection Deactivated.',
        'starting_backup': '백업 시작 중 / Starting backup to ',
        'success': '백업 성공 / Backup Successful.',
        'removed_old': '오래된 백업 제거됨 / Removed old backup: '
    },
    'en': {
        'backup': 'BACKUP',
        'safeguard': 'Automatic Safeguard',
        'source_label': 'Source Directory',
        'dest_label': 'Backup Destination',
        'interval': 'Interval (min):',
        'activate': 'ACTIVATE PROTECT',
        'deactivate': 'DEACTIVATE',
        'logs': 'LIVE LOGS',
        'path_not_selected': 'Path not selected...',
        'browse': 'Browse',
        'warning': 'Warning',
        'select_both': 'Select both source and destination folders!',
        'error': 'Error',
        'interval_error': 'Interval must be a number!',
        'system_ready': '>>> System Ready. Waiting for activation...\n',
        'activated': 'Backup Protection Activated.',
        'deactivated': 'Backup Protection Deactivated.',
        'starting_backup': 'Starting backup to ',
        'success': 'Backup Successful.',
        'removed_old': 'Removed old backup: '
    }
}

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
        self.current_lang = get_system_lang()
        
        # UI Setup / UI 구축
        self.setup_ui()

    def setup_ui(self):
        # Sidebar / 사이드바
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.card_color, border_width=1, border_color="#30363d")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="LAVENDAR", font=("Inter", 28, "bold"), text_color=self.accent_color).pack(pady=(30, 5))
        self.backup_label = ctk.CTkLabel(self.sidebar, text=TRANSLATIONS[self.current_lang]['backup'], font=("Inter", 12), text_color=self.dim_text)
        self.backup_label.pack(pady=(0, 30))

        # Language Toggle / 언어 토글
        self.lang_btn = ctk.CTkButton(
            self.sidebar,
            text=self.current_lang.upper(),
            width=60,
            command=self.toggle_lang,
            fg_color="transparent",
            border_width=1,
            border_color=self.accent_color,
            text_color=self.accent_color
        )
        self.lang_btn.pack(side="bottom", pady=(10, 0))

        # Copyright
        ctk.CTkLabel(self.sidebar, text="© 2008-2026\nRheehose (Rhee Creative)", font=("Inter", 10), text_color=self.dim_text).pack(side="bottom", pady=20)

        # Main Content Area / 메인 콘텐츠 영역
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="right", expand=True, fill="both", padx=30, pady=30)
        
        # Header / 헤더
        self.safeguard_label = ctk.CTkLabel(self.content, text=TRANSLATIONS[self.current_lang]['safeguard'], font=("Inter", 24, "bold"), text_color=self.text_color)
        self.safeguard_label.pack(anchor="w", pady=(0, 20))

        # Config Card / 설정 카드
        self.config_card = ctk.CTkFrame(self.content, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        self.config_card.pack(fill="x", pady=10)
        
        # Source Selection
        self.source_selector = self.create_path_selector(self.config_card, TRANSLATIONS[self.current_lang]['source_label'], self.select_source, "source")
        # Destination Selection
        self.dest_selector = self.create_path_selector(self.config_card, TRANSLATIONS[self.current_lang]['dest_label'], self.select_dest, "dest")
        
        # Settings Row
        self.settings_row = ctk.CTkFrame(self.config_card, fg_color="transparent")
        self.settings_row.pack(fill="x", padx=20, pady=20)
        
        self.interval_label = ctk.CTkLabel(self.settings_row, text=TRANSLATIONS[self.current_lang]['interval'], font=("Inter", 13))
        self.interval_label.pack(side="left", padx=(0, 10))
        self.interval_spin = ctk.CTkEntry(self.settings_row, width=60, fg_color=self.secondary_color, border_color="#30363d")
        self.interval_spin.insert(0, "5")
        self.interval_spin.pack(side="left")
        
        self.btn_toggle = ctk.CTkButton(self.settings_row, text=TRANSLATIONS[self.current_lang]['activate'], command=self.toggle_session_proxy, fg_color=self.accent_color, hover_color="#2ea043", font=("Inter", 13, "bold"), height=40)
        self.btn_toggle.pack(side="right")

        # Status Card / 상태 카드
        self.status_card = ctk.CTkFrame(self.content, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        self.status_card.pack(fill="both", expand=True, pady=10)
        
        self.logs_label = ctk.CTkLabel(self.status_card, text=TRANSLATIONS[self.current_lang]['logs'], font=("Inter", 12, "bold"), text_color=self.dim_text)
        self.logs_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.log_view = ctk.CTkTextbox(self.status_card, fg_color="transparent", font=("JetBrains Mono", 11), text_color="#7ee787")
        self.log_view.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_view.insert("end", TRANSLATIONS[self.current_lang]['system_ready'])
        self.log_view.configure(state="disabled")

    def toggle_lang(self):
        self.current_lang = 'en' if self.current_lang == 'ko' else 'ko'
        self.update_ui()

    def update_ui(self):
        lang = TRANSLATIONS[self.current_lang]
        self.backup_label.configure(text=lang['backup'])
        self.safeguard_label.configure(text=lang['safeguard'])
        self.source_selector.title_label.configure(text=lang['source_label'])
        self.dest_selector.title_label.configure(text=lang['dest_label'])
        self.source_entry.configure(placeholder_text=lang['path_not_selected'])
        self.dest_entry.configure(placeholder_text=lang['path_not_selected'])
        self.source_selector.browse_btn.configure(text=lang['browse'])
        self.dest_selector.browse_btn.configure(text=lang['browse'])
        self.interval_label.configure(text=lang['interval'])
        self.btn_toggle.configure(text=lang['deactivate'] if self.is_running else lang['activate'])
        self.logs_label.configure(text=lang['logs'])
        self.lang_btn.configure(text=self.current_lang.upper())

    def toggle_session_proxy(self):
        self.toggle_backup()

    def create_path_selector(self, parent, label_text, command, attr_name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=10)
        
        title_label = ctk.CTkLabel(frame, text=label_text, font=("Inter", 12, "bold"), text_color=self.dim_text)
        title_label.pack(anchor="w")
        
        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill="x", pady=5)
        
        entry = ctk.CTkEntry(inner_frame, placeholder_text=TRANSLATIONS[self.current_lang]['path_not_selected'], fg_color=self.secondary_color, border_color="#30363d")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        setattr(self, f"{attr_name}_entry", entry)
        
        browse_btn = ctk.CTkButton(inner_frame, text=TRANSLATIONS[self.current_lang]['browse'], width=80, command=command, fg_color=self.secondary_color, hover_color="#30363d")
        browse_btn.pack(side="right")

        # Container for access
        class Selector: pass
        sel = Selector()
        sel.title_label = title_label
        sel.browse_btn = browse_btn
        return sel

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
                messagebox.showwarning(TRANSLATIONS[self.current_lang]['warning'], TRANSLATIONS[self.current_lang]['select_both'])
                return
            
            try:
                self.interval_min = int(self.interval_spin.get())
            except ValueError:
                messagebox.showerror(TRANSLATIONS[self.current_lang]['error'], TRANSLATIONS[self.current_lang]['interval_error'])
                return

            self.is_running = True
            self.btn_toggle.configure(text=TRANSLATIONS[self.current_lang]['deactivate'], fg_color="#f85149", hover_color="#da3633")
            self.log(TRANSLATIONS[self.current_lang]['activated'])
            threading.Thread(target=self.backup_loop, daemon=True).start()
        else:
            self.is_running = False
            self.btn_toggle.configure(text=TRANSLATIONS[self.current_lang]['activate'], fg_color=self.accent_color, hover_color="#2ea043")
            self.log(TRANSLATIONS[self.current_lang]['deactivated'])

    def backup_loop(self):
        while self.is_running:
            try:
                # Create timestamped folder / 타임스탬프 폴더 생성
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = os.path.join(self.dest_dir, f"backup_{now}")
                
                self.log(f"{TRANSLATIONS[self.current_lang]['starting_backup']}{os.path.basename(target_path)}...")
                shutil.copytree(self.source_dir, target_path)
                self.log(TRANSLATIONS[self.current_lang]['success'])
                
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
                self.log(f"{TRANSLATIONS[self.current_lang]['removed_old']}{os.path.basename(oldest)}")
        except:
            pass

if __name__ == "__main__":
    app = Lavendar()
    app.mainloop()
