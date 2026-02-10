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

class TemplateGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Universal Template Gen - RheeWorks")
        self.geometry("750x650")
        self.configure(fg_color="#0D1117")
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#161B22")
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Header
        ctk.CTkLabel(self.main_frame, text="UNIVERSAL PROJECT SCAFFOLDER", 
                    font=("Inter", 24, "bold"), text_color="#58A6FF").pack(pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text="Multi-language Template Creation / 다국어 템플릿 생성", 
                    font=("Inter", 12), text_color="#8b949e").pack()

        # Input Container
        self.container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.container.pack(pady=20, padx=40, fill="both", expand=True)

        # 1. Project Type
        ctk.CTkLabel(self.container, text="Project Type", font=("Inter", 12, "bold")).pack(anchor="w")
        self.type_var = ctk.StringVar(value="JSP")
        self.type_menu = ctk.CTkSegmentedButton(self.container, 
                                               values=["JSP", "Python", "C", "Node.js", "Web"],
                                               variable=self.type_var, command=self.on_type_change)
        self.type_menu.pack(fill="x", pady=5)

        # 2. General Settings
        self.name_entry = self.create_input("Project Name / 프로젝트명", "MyAwesomeProject")
        
        # 3. Dynamic Inputs (Port, DB)
        self.dynamic_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.dynamic_frame.pack(fill="x")
        
        self.port_entry = self.create_input("Port / 포트", "8080", parent=self.dynamic_frame)
        self.db_var = ctk.StringVar(value="mysql")
        self.db_menu = ctk.CTkOptionMenu(self.dynamic_frame, values=["mysql", "oracle", "postgresql"],
                                        variable=self.db_var, fg_color="#21262d")
        
        # 4. Target Dir
        self.path_label = ctk.CTkLabel(self.container, text="Target Directory: Not Selected", font=("Inter", 11), text_color="#8b949e")
        self.path_label.pack(anchor="w", pady=(10, 0))
        self.path_btn = ctk.CTkButton(self.container, text="Choose Directory...", fg_color="#21262d", command=self.browse_path)
        self.path_btn.pack(fill="x", pady=5)
        self.target_path = ""

        # 5. Generate
        self.gen_btn = ctk.CTkButton(self.main_frame, text="GENERATE PROJECT", command=self.generate,
                                    fg_color="#58A6FF", hover_color="#1F6FEB", height=50, font=("Inter", 15, "bold"))
        self.gen_btn.pack(pady=20, padx=40, fill="x")

        self.on_type_change("JSP") # Initial state

    def create_input(self, label, placeholder, parent=None):
        target = parent if parent else self.container
        frame = ctk.CTkFrame(target, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=label, font=("Inter", 12, "bold")).pack(anchor="w")
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color="#0d1117", border_color="#30363d")
        entry.pack(fill="x", pady=2)
        return entry

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
            self.path_label.configure(text=f"Target: {path}", text_color="#58A6FF")

    def generate(self):
        name = self.name_entry.get().strip() or "NewProject"
        ptype = self.type_var.get()
        if not self.target_path:
            messagebox.showwarning("Warning", "Select a directory first!")
            return
        
        root = os.path.join(self.target_path, name)
        try:
            os.makedirs(root, exist_ok=True)
            if ptype == "JSP": self.gen_jsp(root, name)
            elif ptype == "Python": self.gen_py(root, name)
            elif ptype == "C": self.gen_c(root, name)
            elif ptype == "Node.js": self.gen_node(root, name)
            elif ptype == "Web": self.gen_web(root, name)
            messagebox.showinfo("Success", f"{ptype} Project created!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
