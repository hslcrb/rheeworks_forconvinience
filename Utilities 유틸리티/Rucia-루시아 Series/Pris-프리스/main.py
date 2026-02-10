#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Pris - Study/Coding Time Tracker
# Pris - 공부/코딩 시간 관리 대시보드
# Rheehose (Rhee Creative) 2008-2026
# Licensed under Apache-2.0

import os
import sqlite3
import datetime
import time
import threading
from tkinter import messagebox
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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

# i18n Translations / 번역 정보
TRANSLATIONS = {
    'ko': {
        'dashboard': '대시보드 / DASHBOARD',
        'summary': '요약 / Summary',
        'history': '기록 / History',
        'settings': '설정 / Settings',
        'productivity_overview': '생산성 개요 / Productivity Overview',
        'today': '오늘 / TODAY',
        'this_week': '이번 주 / THIS WEEK',
        'streak': '스트릭 / STREAK',
        'weekly_progress': '주간 진행 상황 / Weekly Progress',
        'session_timer': '세션 타이머 / Session Timer',
        'project_placeholder': '프로젝트 이름... / Project Name...',
        'start_session': '세션 시작 / START SESSION',
        'stop_session': '세션 중지 / STOP SESSION',
        'recent_logs': '최근 기록 / Recent Logs',
        'hours': '시간 / Hours',
        'days': '일 / Days',
        'none': '없음'
    },
    'en': {
        'dashboard': 'DASHBOARD',
        'summary': 'Summary',
        'history': 'History',
        'settings': 'Settings',
        'productivity_overview': 'Productivity Overview',
        'today': 'TODAY',
        'this_week': 'THIS WEEK',
        'streak': 'STREAK',
        'weekly_progress': 'Weekly Progress',
        'session_timer': 'Session Timer',
        'project_placeholder': 'Project Name...',
        'start_session': 'START SESSION',
        'stop_session': 'STOP SESSION',
        'recent_logs': 'Recent Logs',
        'hours': 'Hours',
        'days': 'Days',
        'none': 'None'
    }
}

class Pris(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration / 설정 ---
        self.title("PRIS")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        # Colors / 색상
        self.bg_color = "#0d1117"
        self.card_color = "#161b22"
        self.accent_color = "#58a6ff"
        self.secondary_color = "#21262d"
        self.text_color = "#c9d1d9"
        self.dim_text = "#8b949e"
        
        self.configure(fg_color=self.bg_color)
        
        # State / 상태
        self.is_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.current_project = "General"
        self.current_lang = get_system_lang()
        
        # Database / 데이터베이스
        self.init_db()
        
        # UI Setup / UI 구축
        self.setup_ui()
        
        # Update Loop / 업데이트 루프
        self.update_timer()

    def init_db(self):
        """Initialize SQLite database / SQLite 데이터베이스 초기화"""
        self.conn = sqlite3.connect("rucia_stats.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_sec INTEGER,
                date DATE
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        # Sidebar / 사이드바
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.card_color, border_width=1, border_color="#30363d")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="PRIS", font=("Inter", 28, "bold"), text_color=self.accent_color).pack(pady=(30, 5))
        self.dash_label = ctk.CTkLabel(self.sidebar, text=TRANSLATIONS[self.current_lang]['dashboard'], font=("Inter", 12), text_color=self.dim_text)
        self.dash_label.pack(pady=(0, 30))

        # Nav Buttons
        self.create_nav_btn(TRANSLATIONS[self.current_lang]['summary'], True)
        self.create_nav_btn(TRANSLATIONS[self.current_lang]['history'], False)
        self.create_nav_btn(TRANSLATIONS[self.current_lang]['settings'], False)

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
        
        self.header = ctk.CTkFrame(self.content, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 20))
        self.header_label = ctk.CTkLabel(self.header, text=TRANSLATIONS[self.current_lang]['productivity_overview'], font=("Inter", 24, "bold"), text_color=self.text_color)
        self.header_label.pack(side="left")
        
        # Top Stats / 상단 통계 카드
        self.stats_row = ctk.CTkFrame(self.content, fg_color="transparent")
        self.stats_row.pack(fill="x", pady=10)
        
        self.card_today, self.title_today = self.create_stat_card(self.stats_row, TRANSLATIONS[self.current_lang]['today'], "00:00:00", "#7ee787")
        self.card_week, self.title_week = self.create_stat_card(self.stats_row, TRANSLATIONS[self.current_lang]['this_week'], "0.0 hrs", "#d2a8ff")
        self.card_streak, self.title_streak = self.create_stat_card(self.stats_row, TRANSLATIONS[self.current_lang]['streak'], "0 Days", "#ffa657")

        # Layout Column / 레이아웃 컬럼
        self.main_row = ctk.CTkFrame(self.content, fg_color="transparent")
        self.main_row.pack(expand=True, fill="both", pady=10)
        
        # Chart Section / 차트 섹션
        self.chart_container = ctk.CTkFrame(self.main_row, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        self.chart_container.pack(side="left", expand=True, fill="both", padx=(0, 10))
        self.chart_label = ctk.CTkLabel(self.chart_container, text=TRANSLATIONS[self.current_lang]['weekly_progress'], font=("Inter", 14, "bold"))
        self.chart_label.pack(pady=15)
        self.canvas_frame = ctk.CTkFrame(self.chart_container, fg_color="transparent")
        self.canvas_frame.pack(expand=True, fill="both", padx=10, pady=(0, 15))
        self.render_chart()

        # Control Section / 제어 섹션
        self.control_panel = ctk.CTkFrame(self.main_row, fg_color=self.card_color, corner_radius=15, width=300, border_width=1, border_color="#30363d")
        self.control_panel.pack(side="right", fill="y", padx=(10, 0))
        
        self.timer_title = ctk.CTkLabel(self.control_panel, text=TRANSLATIONS[self.current_lang]['session_timer'], font=("Inter", 16, "bold"))
        self.timer_title.pack(pady=20)
        
        self.timer_label = ctk.CTkLabel(self.control_panel, text="00:00:00", font=("JetBrains Mono", 42, "bold"), text_color=self.accent_color)
        self.timer_label.pack(pady=10)
        
        self.proj_entry = ctk.CTkEntry(self.control_panel, placeholder_text=TRANSLATIONS[self.current_lang]['project_placeholder'], fg_color=self.secondary_color, border_color="#30363d", width=220)
        self.proj_entry.pack(pady=10)
        
        self.btn_toggle = ctk.CTkButton(self.control_panel, text=TRANSLATIONS[self.current_lang]['start_session'], command=self.toggle_session, fg_color=self.accent_color, hover_color="#1f6feb", height=45, font=("Inter", 13, "bold"))
        self.btn_toggle.pack(pady=20, padx=40, fill="x")
        
        # Quick Logs / 최근 기록
        self.recent_logs_label = ctk.CTkLabel(self.control_panel, text=TRANSLATIONS[self.current_lang]['recent_logs'], font=("Inter", 12, "bold"), text_color=self.dim_text)
        self.recent_logs_label.pack(pady=(10, 5))
        self.log_list = ctk.CTkTextbox(self.control_panel, fg_color="transparent", font=("Inter", 11), text_color=self.dim_text, height=200)
        self.log_list.pack(fill="both", padx=10, pady=5)
        self.update_log_view()
        self.update_top_stats()
        self.update_ui()

    def toggle_lang(self):
        self.current_lang = 'en' if self.current_lang == 'ko' else 'ko'
        self.update_ui()

    def update_ui(self):
        lang = TRANSLATIONS[self.current_lang]
        self.header_label.configure(text=lang['productivity_overview'])
        self.btn_toggle.configure(text=lang['stop_session'] if self.is_running else lang['start_session'])
        self.proj_entry.configure(placeholder_text=lang['project_placeholder'])
        self.recent_logs_label.configure(text=lang['recent_logs'])
        self.chart_label.configure(text=lang['weekly_progress'])
        self.timer_title.configure(text=lang['session_timer'])
        self.dash_label.configure(text=lang['dashboard'])
        self.title_today.configure(text=lang['today'])
        self.title_week.configure(text=lang['this_week'])
        self.title_streak.configure(text=lang['streak'])
        self.lang_btn.configure(text=self.current_lang.upper())
        self.update_top_stats()
        self.render_chart()

    def create_nav_btn(self, text, active):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color=self.secondary_color if active else "transparent", hover_color=self.secondary_color, anchor="w", font=("Inter", 13), height=40)
        btn.pack(fill="x", padx=10, pady=5)

    def create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=self.card_color, corner_radius=12, border_width=1, border_color="#30363d")
        card.pack(side="left", expand=True, fill="both", padx=5)
        title_label = ctk.CTkLabel(card, text=title, font=("Inter", 11, "bold"), text_color=self.dim_text)
        title_label.pack(pady=(15, 0))
        val_label = ctk.CTkLabel(card, text=value, font=("Inter", 20, "bold"), text_color=color)
        val_label.pack(pady=(5, 15))
        return (val_label, title_label)

    def toggle_session(self):
        if not self.is_running:
            self.start_session()
        else:
            self.stop_session()

    def start_session(self):
        self.is_running = True
        self.start_time = datetime.datetime.now()
        self.current_project = self.proj_entry.get().strip() or "General"
        self.btn_toggle.configure(text=TRANSLATIONS[self.current_lang]['stop_session'], fg_color="#f85149", hover_color="#da3633")
        self.proj_entry.configure(state="disabled")

    def stop_session(self):
        self.is_running = False
        end_time = datetime.datetime.now()
        duration = int((end_time - self.start_time).total_seconds())
        
        if duration > 10: # Min 10 seconds to save / 최소 10초 이상일 때 저장
            self.save_session(self.current_project, self.start_time, end_time, duration)
            self.update_top_stats()
            self.update_log_view()
            self.render_chart()
            
        self.btn_toggle.configure(text=TRANSLATIONS[self.current_lang]['start_session'], fg_color=self.accent_color, hover_color="#1f6feb")
        self.proj_entry.configure(state="normal")
        self.timer_label.configure(text="00:00:00")
        self.elapsed_time = 0

    def save_session(self, proj, start, end, duration):
        self.cursor.execute('''
            INSERT INTO sessions (project, start_time, end_time, duration_sec, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (proj, start.isoformat(), end.isoformat(), duration, start.date().isoformat()))
        self.conn.commit()

    def update_timer(self):
        if self.is_running:
            delta = datetime.datetime.now() - self.start_time
            self.timer_label.configure(text=str(delta).split(".")[0])
        self.after(1000, self.update_timer)

    def update_top_stats(self):
        today = datetime.date.today().isoformat()
        self.cursor.execute("SELECT SUM(duration_sec) FROM sessions WHERE date = ?", (today,))
        total_today = self.cursor.fetchone()[0] or 0
        self.card_today.configure(text=time.strftime('%H:%M:%S', time.gmtime(total_today)))
        
        # Last 7 days
        week_start = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        self.cursor.execute("SELECT SUM(duration_sec) FROM sessions WHERE date >= ?", (week_start,))
        total_week = self.cursor.fetchone()[0] or 0
        self.card_week.configure(text=f"{total_week/3600:.1f} hrs")

    def update_log_view(self):
        self.log_list.configure(state="normal")
        self.log_list.delete("1.0", "end")
        self.cursor.execute("SELECT project, duration_sec, date FROM sessions ORDER BY id DESC LIMIT 10")
        for row in self.cursor.fetchall():
            m, s = divmod(row[1], 60)
            h, m = divmod(m, 60)
            self.log_list.insert("end", f"• {row[2]} | {row[0]}\n  {h:02}:{m:02}:{s:02}\n\n")
        self.log_list.configure(state="disabled")

    def render_chart(self):
        # Clear previous chart / 기존 차트 초기화
        for child in self.canvas_frame.winfo_children():
            child.destroy()
            
        # Data preparation / 데이터 준비
        dates = []
        durations = []
        for i in range(6, -1, -1):
            d = (datetime.date.today() - datetime.timedelta(days=i))
            dates.append(d.strftime("%a"))
            self.cursor.execute("SELECT SUM(duration_sec) FROM sessions WHERE date = ?", (d.isoformat(),))
            durations.append((self.cursor.fetchone()[0] or 0) / 3600)

        # Plotting / 그래프 그리기
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
        fig.patch.set_facecolor(self.card_color)
        ax.set_facecolor(self.card_color)
        
        bars = ax.bar(dates, durations, color=self.accent_color, alpha=0.8, edgecolor=self.accent_color, linewidth=1)
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#30363d')
        ax.spines['bottom'].set_color('#30363d')
        ax.tick_params(axis='both', colors=self.dim_text, labelsize=9)
        ax.set_ylabel(TRANSLATIONS[self.current_lang]['hours'], color=self.dim_text, fontsize=9)
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")
        plt.close(fig)

if __name__ == "__main__":
    app = Pris()
    app.mainloop()
