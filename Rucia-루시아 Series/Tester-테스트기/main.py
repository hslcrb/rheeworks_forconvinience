#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Tester-기 - Algorithm Problem Auto-Tester
# 테스트기 - 알고리즘 문제풀이 자동 테스트기
# Rheehose (Rhee Creative) 2008-2026
# Licensed under Apache-2.0

import os
import subprocess
import time
import difflib
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

class RuciaTester(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration / 설정 ---
        self.title("RUCIA TESTER")
        self.geometry("1100x800")
        ctk.set_appearance_mode("dark")
        
        # Colors / 색상
        self.bg_color = "#0d1117"
        self.card_color = "#161b22"
        self.accent_color = "#d2a8ff" # Tech Purple
        self.secondary_color = "#21262d"
        self.text_color = "#c9d1d9"
        self.dim_text = "#8b949e"
        self.pass_color = "#3fb950"
        self.fail_color = "#f85149"
        
        self.configure(fg_color=self.bg_color)
        
        # State / 상태
        self.target_script = ""
        self.test_cases = [] # List of (input, expected_output)
        
        # UI Setup / UI 구축
        self.setup_ui()

    def setup_ui(self):
        # Sidebar / 사이드바
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.card_color, border_width=1, border_color="#30363d")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="RUCIA", font=("Inter", 28, "bold"), text_color=self.accent_color).pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="TESTER", font=("Inter", 12), text_color=self.dim_text).pack(pady=(0, 30))

        # Copyright
        ctk.CTkLabel(self.sidebar, text="© 2008-2026\nRheehose (Rhee Creative)", font=("Inter", 10), text_color=self.dim_text).pack(side="bottom", pady=20)

        # Main Content Area / 메인 콘텐츠 영역
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="right", expand=True, fill="both", padx=30, pady=30)
        
        # Header / 헤더
        ctk.CTkLabel(self.content, text="Logic Evaluation Environment", font=("Inter", 24, "bold"), text_color=self.text_color).pack(anchor="w", pady=(0, 20))

        # Config Panel / 설정 패널
        self.config_panel = ctk.CTkFrame(self.content, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        self.config_panel.pack(fill="x", pady=10)
        
        # Script Selection
        script_row = ctk.CTkFrame(self.config_panel, fg_color="transparent")
        script_row.pack(fill="x", padx=20, pady=20)
        
        self.script_entry = ctk.CTkEntry(script_row, placeholder_text="Target script (main.py, solution.py...)", fg_color=self.secondary_color, border_color="#30363d")
        self.script_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(script_row, text="Select Script", width=120, command=self.select_script, fg_color=self.secondary_color, hover_color="#30363d").pack(side="right")

        # Test Case Input Section / 테스트 케이스 입력 섹션
        self.input_section = ctk.CTkFrame(self.content, fg_color="transparent")
        self.input_section.pack(fill="x", pady=10)
        
        # Input Box
        input_box_frame = ctk.CTkFrame(self.input_section, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        input_box_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
        ctk.CTkLabel(input_box_frame, text="INPUT", font=("Inter", 11, "bold"), text_color=self.dim_text).pack(pady=5)
        self.input_text = ctk.CTkTextbox(input_box_frame, fg_color="transparent", height=150, font=("JetBrains Mono", 11))
        self.input_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Expected Box
        expected_box_frame = ctk.CTkFrame(self.input_section, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        expected_box_frame.pack(side="left", expand=True, fill="both", padx=(5, 5))
        ctk.CTkLabel(expected_box_frame, text="EXPECTED OUTPUT", font=("Inter", 11, "bold"), text_color=self.dim_text).pack(pady=5)
        self.expected_text = ctk.CTkTextbox(expected_box_frame, fg_color="transparent", height=150, font=("JetBrains Mono", 11))
        self.expected_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Actions
        actions_frame = ctk.CTkFrame(self.input_section, fg_color="transparent", width=150)
        actions_frame.pack(side="right", fill="y")
        ctk.CTkButton(actions_frame, text="ADD CASE", command=self.add_test_case, fg_color=self.secondary_color, hover_color="#30363d", height=45).pack(pady=(25, 10), fill="x", padx=10)
        ctk.CTkButton(actions_frame, text="RUN ALL", command=self.run_all_tests, fg_color=self.accent_color, hover_color="#af8cf7", text_color="#161b22", font=("Inter", 13, "bold"), height=80).pack(pady=5, fill="x", padx=10)

        # Results Display / 결과 표시 영역
        self.results_card = ctk.CTkScrollableFrame(self.content, fg_color=self.card_color, corner_radius=15, border_width=1, border_color="#30363d")
        self.results_card.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(self.results_card, text="VERIFICATION REPORT", font=("Inter", 12, "bold"), text_color=self.dim_text).pack(anchor="w", padx=10, pady=10)
        
        self.result_container = ctk.CTkFrame(self.results_card, fg_color="transparent")
        self.result_container.pack(fill="both", expand=True)

    def select_script(self):
        file = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if file:
            self.target_script = file
            self.script_entry.delete(0, "end")
            self.script_entry.insert(0, file)

    def add_test_case(self):
        in_data = self.input_text.get("1.0", "end-1c").strip()
        out_data = self.expected_text.get("1.0", "end-1c").strip()
        
        if not in_data or not out_data:
            messagebox.showwarning("Warning", "Fill both input and expected output!")
            return
            
        self.test_cases.append((in_data, out_data))
        self.input_text.delete("1.0", "end")
        self.expected_text.delete("1.0", "end")
        self.log_case_added(len(self.test_cases), in_data)

    def log_case_added(self, num, in_data):
        label = ctk.CTkLabel(self.result_container, text=f"Case #{num} Added: {in_data[:20]}...", font=("Inter", 11), text_color=self.dim_text)
        label.pack(anchor="w", padx=20, pady=2)

    def run_all_tests(self):
        if not self.target_script:
            messagebox.showwarning("Warning", "Select a target script first!")
            return
        if not self.test_cases:
            messagebox.showwarning("Warning", "Add at least one test case!")
            return
            
        # Clear previous results
        for child in self.result_container.winfo_children():
            child.destroy()
            
        results = []
        for i, (in_data, expected) in enumerate(self.test_cases):
            res = self.run_test(in_data, expected, i+1)
            results.append(res)

    def run_test(self, in_data, expected, case_num):
        start_time = time.time()
        try:
            # Use subprocess to run the target script / 자식 프로세스로 대상 스크립트 실행
            process = subprocess.Popen(
                ["python3", self.target_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=in_data, timeout=5)
            elapsed = (time.time() - start_time) * 1000 # ms
            
            actual = stdout.strip()
            passed = actual == expected.strip()
            
            self.display_result(case_num, in_data, expected, actual, passed, elapsed, stderr)
            return passed
        except subprocess.TimeoutExpired:
            self.display_result(case_num, in_data, expected, "TIMEOUT", False, 5000, "Operation timed out after 5 seconds")
            return False
        except Exception as e:
            self.display_result(case_num, in_data, expected, "ERROR", False, 0, str(e))
            return False

    def display_result(self, case_num, in_data, expected, actual, passed, elapsed, error):
        card = ctk.CTkFrame(self.result_container, fg_color=self.secondary_color, corner_radius=10, border_width=1, border_color="#30363d")
        card.pack(fill="x", padx=10, pady=5)
        
        status_text = "PASS" if passed else "FAIL"
        status_color = self.pass_color if passed else self.fail_color
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text=f"Case #{case_num}", font=("Inter", 12, "bold")).pack(side="left")
        ctk.CTkLabel(header, text=status_text, font=("Inter", 12, "bold"), text_color=status_color).pack(side="left", padx=10)
        ctk.CTkLabel(header, text=f"{elapsed:.2f}ms", font=("JetBrains Mono", 11), text_color=self.dim_text).pack(side="right")
        
        if not passed:
            diff_frame = ctk.CTkFrame(card, fg_color=self.bg_color, corner_radius=5)
            diff_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            ctk.CTkLabel(diff_frame, text=f"Expected: {expected}", font=("JetBrains Mono", 11), text_color=self.dim_text, anchor="w").pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(diff_frame, text=f"Actual:   {actual}", font=("JetBrains Mono", 11), text_color=self.fail_color, anchor="w").pack(fill="x", padx=10, pady=2)
            
            if error:
                ctk.CTkLabel(diff_frame, text=f"Error: {error}", font=("JetBrains Mono", 10), text_color="#f85149", wraplenght=600).pack(fill="x", padx=10, pady=2)

if __name__ == "__main__":
    app = RuciaTester()
    app.mainloop()
