#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automaker - Project Template Generator / 오토메이커 - 프로젝트 템플릿 생성기
Multi-language Scaffolding Tool / 다국어 프로젝트 스캐폴딩 도구

Copyright (c) 2008-2026 Rheehose (Rhee Creative)
Licensed under the Apache License, Version 2.0
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import json
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

# ======================
# Templates / 템플릿
# ======================

# JSP Templates
WEB_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee https://jakarta.ee/xml/ns/jakartaee/web-app_5_0.xsd"
  version="5.0">
  <display-name>{project_name}</display-name>
  <welcome-file-list><welcome-file>index.jsp</welcome-file></welcome-file-list>
</web-app>"""

INDEX_JSP_TEMPLATE = """<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head><title>{project_name}</title></head>
<body style="background:#0d1117;color:#c9d1d9;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
    <div style="background:#161b22;padding:40px;border-radius:20px;border:1px solid #30363d;text-align:center;">
        <h1 style="color:#58a6ff;">{project_name}</h1>
        <p>JSP Project initialized successfully!</p>
    </div>
</body>
</html>"""

# Python Templates
PYTHON_MAIN_TEMPLATE = """def main():
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
"""

# C Templates
C_MAIN_TEMPLATE = """#include <stdio.h>

int main() {
    printf("Hello from {project_name}!\\n");
    return 0;
}
"""
C_MAKEFILE_TEMPLATE = """all:
\tgcc main.c -o {project_name}
clean:
\trm -f {project_name}
"""

# Node.js Templates
NODE_PACKAGE_TEMPLATE = """{{
  "name": "{project_name}",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {{
    "start": "node index.js"
  }},
  "dependencies": {{}}
}}"""

NODE_MAIN_TEMPLATE = """const http = require('http');
const port = {port};

const server = http.createServer((req, res) => {{
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello from {project_name}\\n');
}});

server.listen(port, () => {{
  console.log(`Server running at http://localhost:${{port}}/`);
}});"""

# Web Templates
WEB_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>{project_name}</title><link rel="stylesheet" href="style.css"></head>
<body><h1>{project_name}</h1><script src="script.js"></script></body>
</html>"""

# ======================
# Logic / 로직
# ======================

# i18n Translations / 번역 정보
TRANSLATIONS = {
    'ko': {
        'scaffolder': '만능 프로젝트 스캐폴더 / UNIVERSAL PROJECT SCAFFOLDER',
        'subtitle': '다국어 프로젝트 템플릿 생성 / Multi-language Template Creation',
        'project_type': '프로젝트 유형',
        'project_name': '프로젝트명',
        'port': '포트',
        'target_dir': '대상 디렉토리: 선택 안됨',
        'target_selected': '대상: {path}',
        'choose_dir': '디렉토리 선택...',
        'generate_btn': '프로젝트 생성 / GENERATE PROJECT',
        'warning': '경고',
        'select_dir_first': '디렉토리를 먼저 선택하세요!',
        'success': '성공',
        'created': '{ptype} 프로젝트가 생성되었습니다!',
        'error': '오류'
    },
    'en': {
        'scaffolder': 'UNIVERSAL PROJECT SCAFFOLDER',
        'subtitle': 'Multi-language Template Creation',
        'project_type': 'Project Type',
        'project_name': 'Project Name',
        'port': 'Port',
        'target_dir': 'Target Directory: Not Selected',
        'target_selected': 'Target: {path}',
        'choose_dir': 'Choose Directory...',
        'generate_btn': 'GENERATE PROJECT',
        'warning': 'Warning',
        'select_dir_first': 'Select a directory first!',
        'success': 'Success',
        'created': '{ptype} Project created!',
        'error': 'Error'
    }
}

class TemplateGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_lang = get_system_lang()
        self.title("Universal Template Gen - RheeWorks")
        self.geometry("750x700")
        self.configure(fg_color="#0D1117")
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#161B22")
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Header
        self.title_label = ctk.CTkLabel(self.main_frame, text=TRANSLATIONS[self.current_lang]['scaffolder'], 
                    font=("Inter", 24, "bold"), text_color="#58A6FF")
        self.title_label.pack(pady=(20, 5))
        self.subtitle_label = ctk.CTkLabel(self.main_frame, text=TRANSLATIONS[self.current_lang]['subtitle'], 
                    font=("Inter", 12), text_color="#8b949e")
        self.subtitle_label.pack()

        # Input Container
        self.container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.container.pack(pady=20, padx=40, fill="both", expand=True)

        # 1. Project Type
        self.type_label = ctk.CTkLabel(self.container, text=TRANSLATIONS[self.current_lang]['project_type'], font=("Inter", 12, "bold"))
        self.type_label.pack(anchor="w")
        self.type_var = ctk.StringVar(value="JSP")
        self.type_menu = ctk.CTkSegmentedButton(self.container, 
                                               values=["JSP", "Python", "C", "Node.js", "Web"],
                                               variable=self.type_var, command=self.on_type_change)
        self.type_menu.pack(fill="x", pady=5)

        # 2. General Settings
        self.name_entry = self.create_input(TRANSLATIONS[self.current_lang]['project_name'], "MyAwesomeProject")
        
        # 3. Dynamic Inputs (Port, DB)
        self.dynamic_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.dynamic_frame.pack(fill="x")
        
        self.port_entry = self.create_input(TRANSLATIONS[self.current_lang]['port'], "8080", parent=self.dynamic_frame)
        self.db_var = ctk.StringVar(value="mysql")
        self.db_menu = ctk.CTkOptionMenu(self.dynamic_frame, values=["mysql", "oracle", "postgresql"],
                                        variable=self.db_var, fg_color="#21262d")
        
        # 4. Target Dir
        self.path_label = ctk.CTkLabel(self.container, text=TRANSLATIONS[self.current_lang]['target_dir'], font=("Inter", 11), text_color="#8b949e")
        self.path_label.pack(anchor="w", pady=(10, 0))
        self.path_btn = ctk.CTkButton(self.container, text=TRANSLATIONS[self.current_lang]['choose_dir'], fg_color="#21262d", command=self.browse_path)
        self.path_btn.pack(fill="x", pady=5)
        self.target_path = ""

        # 5. Generate
        self.gen_btn = ctk.CTkButton(self.main_frame, text=TRANSLATIONS[self.current_lang]['generate_btn'], command=self.generate,
                                    fg_color="#58A6FF", hover_color="#1F6FEB", height=50, font=("Inter", 15, "bold"))
        self.gen_btn.pack(pady=10, padx=40, fill="x")

        # Language Toggle / 언어 토글
        self.lang_btn = ctk.CTkButton(
            self.main_frame,
            text=self.current_lang.upper(),
            width=60,
            command=self.toggle_lang,
            fg_color="transparent",
            border_width=1,
            border_color="#58A6FF",
            text_color="#58A6FF"
        )
        self.lang_btn.pack(pady=(0, 20))

        self.on_type_change("JSP") # Initial state

    def create_input(self, label, placeholder, parent=None):
        target = parent if parent else self.container
        frame = ctk.CTkFrame(target, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        lbl = ctk.CTkLabel(frame, text=label, font=("Inter", 12, "bold"))
        lbl.pack(anchor="w")
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color="#0d1117", border_color="#30363d")
        entry.pack(fill="x", pady=2)
        return entry

    def toggle_lang(self):
        self.current_lang = 'en' if self.current_lang == 'ko' else 'ko'
        self.update_ui()

    def update_ui(self):
        lang = TRANSLATIONS[self.current_lang]
        self.title_label.configure(text=lang['scaffolder'])
        self.subtitle_label.configure(text=lang['subtitle'])
        self.type_label.configure(text=lang['project_type'])
        # Note: Entry labels are hard to update post-creation without tracking them
        # For simplicity, we'll focus on primary UI elements
        if not self.target_path:
            self.path_label.configure(text=lang['target_dir'])
        else:
            self.path_label.configure(text=lang['target_selected'].format(path=self.target_path))
        self.path_btn.configure(text=lang['choose_dir'])
        self.gen_btn.configure(text=lang['generate_btn'])
        self.lang_btn.configure(text=self.current_lang.upper())

    def on_type_change(self, val):
        # Only JSP/Node need Port/DB
        if val in ["JSP", "Node.js"]:
            self.dynamic_frame.pack(fill="x")
            if val == "JSP": self.db_menu.pack(pady=5)
            else: self.db_menu.pack_forget()
        else:
            self.dynamic_frame.pack_forget()

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.target_path = path
            self.path_label.configure(text=TRANSLATIONS[self.current_lang]['target_selected'].format(path=path), text_color="#58A6FF")

    def generate(self):
        name = self.name_entry.get().strip() or "NewProject"
        ptype = self.type_var.get()
        lang = TRANSLATIONS[self.current_lang]
        if not self.target_path:
            messagebox.showwarning(lang['warning'], lang['select_dir_first'])
            return
        
        root = os.path.join(self.target_path, name)
        try:
            os.makedirs(root, exist_ok=True)
            if ptype == "JSP": self.gen_jsp(root, name)
            elif ptype == "Python": self.gen_py(root, name)
            elif ptype == "C": self.gen_c(root, name)
            elif ptype == "Node.js": self.gen_node(root, name)
            elif ptype == "Web": self.gen_web(root, name)
            messagebox.showinfo(lang['success'], lang['created'].format(ptype=ptype))
        except Exception as e:
            messagebox.showerror(lang['error'], str(e))

    def gen_jsp(self, root, name):
        for d in ["src/main/java/servlet", "src/main/java/util", "src/main/webapp/WEB-INF"]:
            os.makedirs(os.path.join(root, d), exist_ok=True)
        with open(os.path.join(root, "src/main/webapp/index.jsp"), "w") as f: f.write(INDEX_JSP_TEMPLATE.format(project_name=name))
        with open(os.path.join(root, "src/main/webapp/WEB-INF/web.xml"), "w") as f: f.write(WEB_XML_TEMPLATE.format(project_name=name))

    def gen_py(self, root, name):
        os.makedirs(os.path.join(root, "utils"), exist_ok=True)
        with open(os.path.join(root, "main.py"), "w") as f: f.write(PYTHON_MAIN_TEMPLATE.format(project_name=name))
        with open(os.path.join(root, "requirements.txt"), "w") as f: f.write("# Dependencies")

    def gen_c(self, root, name):
        os.makedirs(os.path.join(root, "include"), exist_ok=True)
        with open(os.path.join(root, "main.c"), "w") as f: f.write(C_MAIN_TEMPLATE.format(project_name=name))
        with open(os.path.join(root, "Makefile"), "w") as f: f.write(C_MAKEFILE_TEMPLATE.format(project_name=name))

    def gen_node(self, root, name):
        port = self.port_entry.get() or "3000"
        os.makedirs(os.path.join(root, "public"), exist_ok=True)
        with open(os.path.join(root, "package.json"), "w") as f: f.write(NODE_PACKAGE_TEMPLATE.format(project_name=name))
        with open(os.path.join(root, "index.js"), "w") as f: f.write(NODE_MAIN_TEMPLATE.format(project_name=name, port=port))

    def gen_web(self, root, name):
        for f in ["style.css", "script.js"]: open(os.path.join(root, f), "w").close()
        with open(os.path.join(root, "index.html"), "w") as f: f.write(WEB_HTML_TEMPLATE.format(project_name=name))

if __name__ == "__main__":
    app = TemplateGenerator()
    app.mainloop()
