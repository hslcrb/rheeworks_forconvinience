#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Generator CLI - Project Scaffolding Tool
# Rheehose (Rhee Creative) 2008-2026

import os
import sys
import argparse

# --- Templates (Extracted for CLI) ---
INDEX_JSP = """<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<html><body><h1>{project_name}</h1><p>JSP Project initialized!</p></body></html>"""

PYTHON_MAIN = """if __name__ == "__main__":
    print("Hello from {project_name}!")
"""

C_MAIN = """#include <stdio.h>
int main() { printf("Hello from {project_name}!\\n"); return 0; }
"""

NODE_PACKAGE = """{{
  "name": "{project_name}",
  "version": "1.0.0",
  "scripts": {{ "start": "node index.js" }}
}}"""

WEB_HTML = """<!DOCTYPE html><html><head><title>{project_name}</title></head><body><h1>{project_name}</h1></body></html>"""

class GeneratorCLI:
    def __init__(self, target_dir):
        self.target_dir = target_dir

    def generate(self, name, ptype, port=8080):
        root = os.path.join(self.target_dir, name)
        os.makedirs(root, exist_ok=True)
        
        if ptype == "jsp":
            self._gen_jsp(root, name)
        elif ptype == "python":
            self._gen_py(root, name)
        elif ptype == "c":
            self._gen_c(root, name)
        elif ptype == "node":
            self._gen_node(root, name, port)
        elif ptype == "web":
            self._gen_web(root, name)
        
        print(f"Success: {ptype.upper()} project '{name}' created at {root}")

    def _gen_jsp(self, root, name):
        os.makedirs(os.path.join(root, "src/main/webapp/WEB-INF"), exist_ok=True)
        with open(os.path.join(root, "src/main/webapp/index.jsp"), "w") as f: f.write(INDEX_JSP.format(project_name=name))

    def _gen_py(self, root, name):
        with open(os.path.join(root, "main.py"), "w") as f: f.write(PYTHON_MAIN.format(project_name=name))
        with open(os.path.join(root, "requirements.txt"), "w") as f: f.write("# Dependencies")

    def _gen_c(self, root, name):
        with open(os.path.join(root, "main.c"), "w") as f: f.write(C_MAIN.format(project_name=name))

    def _gen_node(self, root, name, port):
        with open(os.path.join(root, "package.json"), "w") as f: f.write(NODE_PACKAGE.format(project_name=name))
        with open(os.path.join(root, "index.js"), "w") as f: f.write(f"console.log('App {name} running on {port}');")

    def _gen_web(self, root, name):
        with open(os.path.join(root, "index.html"), "w") as f: f.write(WEB_HTML.format(project_name=name))

def main():
    parser = argparse.ArgumentParser(description="Template Generator CLI")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--type", choices=['jsp', 'python', 'c', 'node', 'web'], required=True, help="Project type")
    parser.add_argument("--path", default=".", help="Target parent directory")
    parser.add_argument("--port", type=int, default=8080, help="Port (for Node/JSP)")
    
    args = parser.parse_args()
    gen = GeneratorCLI(args.path)
    gen.generate(args.name, args.type, args.port)

if __name__ == "__main__":
    main()
