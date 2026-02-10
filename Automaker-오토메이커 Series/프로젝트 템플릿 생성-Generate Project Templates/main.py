#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automaker - Project Template Generator / 오토메이커 - 프로젝트 템플릿 생성기
JSP/Web Project Scaffolding Tool / JSP/웹 프로젝트 스캐폴딩 도구

Copyright (c) 2008-2026 Rheehose (Rhee Creative)
Licensed under the Apache License, Version 2.0
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil

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

WEB_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee https://jakarta.ee/xml/ns/jakartaee/web-app_5_0.xsd"
  version="5.0">
  
  <display-name>{project_name}</display-name>
  
  <welcome-file-list>
    <welcome-file>index.jsp</welcome-file>
  </welcome-file-list>
</web-app>
"""

INDEX_JSP_TEMPLATE = """<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{project_name} - Welcome</title>
<style>
    body {{ font-family: 'Inter', sans-serif; background: #0d1117; color: #c9d1d9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
    .card {{ background: #161b22; padding: 40px; border-radius: 20px; border: 1px solid #30363d; text-align: center; }}
    h1 {{ color: #58a6ff; }}
</style>
</head>
<body>
    <div class="card">
        <h1>{project_name}</h1>
        <p>JSP Project initialized successfully!</p>
        <p>Created by RheeWorks Automaker</p>
    </div>
</body>
</html>
"""

DB_UTIL_TEMPLATE = """package util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DBUtil {{
    private static final String URL = "jdbc:{db_type}://localhost:{port}/{db_name}";
    private static final String USER = "root";
    private static final String PWD = "password";

    static {{
        try {{
            Class.forName("{driver_class}");
        }} catch (ClassNotFoundException e) {{
            e.printStackTrace();
        }}
    }}

    public static Connection getConnection() throws SQLException {{
        return DriverManager.getConnection(URL, USER, PWD);
    }}
}}
"""

# ======================
# Logic / 로직
# ======================

class TemplateGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Project Template Gen - RheeWorks")
        self.geometry("700x600")
        self.configure(fg_color="#0D1117")

        # UI Styles
        self.accent_color = "#58A6FF"
        self.card_color = "#161B22"

        self.setup_ui()

    def setup_ui(self):
        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color=self.card_color)
        self.main_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # Title
        ctk.CTkLabel(
            self.main_frame, text="PROJECT TEMPLATE GENERATOR", 
            font=("Inter", 24, "bold"), text_color=self.accent_color
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            self.main_frame, text="Auto-scaffolding for JSP/Web Projects", 
            font=("Inter", 12), text_color="#8b949e"
        ).pack()

        # Inputs
        self.input_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_container.pack(pady=30, padx=50, fill="x")

        # Project Name
        self.name_entry = self.create_input("Project Name / 프로젝트명", "MyJSPProject")
        
        # Port
        self.port_entry = self.create_input("Port / 포트 (Default: 8080)", "8080")

        # DB Setup
        self.db_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        self.db_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.db_frame, text="DB Type", font=("Inter", 12, "bold")).pack(side="left", padx=5)
        self.db_var = ctk.StringVar(value="mysql")
        self.db_menu = ctk.CTkOptionMenu(
            self.db_frame, values=["mysql", "oracle", "postgresql"],
            variable=self.db_var, fg_color="#21262d", button_color="#30363d"
        )
        self.db_menu.pack(side="right", expand=True, fill="x", padx=5)

        # Target Dir
        self.dir_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        self.dir_frame.pack(fill="x", pady=10)
        self.dir_label = ctk.CTkLabel(self.dir_frame, text="Select Target Directory", font=("Inter", 11), text_color="#8b949e")
        self.dir_label.pack(side="left", padx=5)
        self.path_btn = ctk.CTkButton(
            self.dir_frame, text="Browse...", command=self.browse_path,
            fg_color="#21262d", width=100
        )
        self.path_btn.pack(side="right", padx=5)
        self.target_path = ""

        # Generate Button
        self.gen_btn = ctk.CTkButton(
            self.main_frame, text="GENERATE PROJECT", command=self.generate,
            fg_color=self.accent_color, hover_color="#1F6FEB", height=50,
            font=("Inter", 15, "bold")
        )
        self.gen_btn.pack(pady=20, padx=50, fill="x")

        # Copyright
        ctk.CTkLabel(
            self, text="© 2008-2026 Rheehose (Rhee Creative)", 
            font=("Inter", 10), text_color="#484f58"
        ).pack(side="bottom", pady=10)

    def create_input(self, label, placeholder):
        frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=label, font=("Inter", 12, "bold")).pack(anchor="w", padx=5)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color="#0d1117", border_color="#30363d")
        entry.pack(fill="x", padx=5, pady=2)
        return entry

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.target_path = path
            self.dir_label.configure(text=f"Selected: {os.path.basename(path)}", text_color=self.accent_color)

    def generate(self):
        project_name = self.name_entry.get().strip() or "NewProject"
        port = self.port_entry.get().strip() or "8080"
        db_type = self.db_var.get()
        
        if not self.target_path:
            messagebox.showwarning("Warning", "Please select a target directory!")
            return

        full_path = os.path.join(self.target_path, project_name)
        
        try:
            # Structure
            dirs = [
                "src/main/java/servlet",
                "src/main/java/util",
                "src/main/java/dao",
                "src/main/java/dto",
                "src/main/webapp/WEB-INF",
                "src/main/webapp/css",
                "src/main/webapp/js",
            ]
            
            for d in dirs:
                os.makedirs(os.path.join(full_path, d), exist_ok=True)

            # Files
            with open(os.path.join(full_path, "src/main/webapp/WEB-INF/web.xml"), "w") as f:
                f.write(WEB_XML_TEMPLATE.format(project_name=project_name))

            with open(os.path.join(full_path, "src/main/webapp/index.jsp"), "w") as f:
                f.write(INDEX_JSP_TEMPLATE.format(project_name=project_name))

            driver_map = {
                "mysql": "com.mysql.cj.jdbc.Driver",
                "oracle": "oracle.jdbc.driver.OracleDriver",
                "postgresql": "org.postgresql.Driver"
            }

            with open(os.path.join(full_path, "src/main/java/util/DBUtil.java"), "w") as f:
                f.write(DB_UTIL_TEMPLATE.format(
                    db_type=db_type, 
                    port=port, 
                    db_name=project_name.lower(),
                    driver_class=driver_map.get(db_type, "com.mysql.cj.jdbc.Driver")
                ))

            messagebox.showinfo("Success", f"Project '{project_name}' generated at:\n{full_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate project: {str(e)}")

if __name__ == "__main__":
    app = TemplateGenerator()
    app.mainloop()
