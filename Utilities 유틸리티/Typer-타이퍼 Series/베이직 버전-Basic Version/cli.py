#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Typer Basic CLI - Fake Typing Copier
# Rheehose (Rhee Creative) 2008-2026

import os
import random
import time
import sys
import argparse
import locale
from pynput import keyboard

def get_msg(ko_msg, en_msg):
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith('ko'):
            return f"{ko_msg} / {en_msg}"
    except:
        pass
    return en_msg

class TyperCLI:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.buffer_text = ""
        self.cursor = 0
        self.recording = False
        self.listener = None

    def start(self):
        if not os.path.exists(self.source):
            print(get_msg(f"오류: 원천 파일 '{self.source}'을 찾을 수 없습니다.", f"Error: Source file '{self.source}' not found."))
            return

        with open(self.source, "r", encoding="utf-8") as f:
            self.buffer_text = f.read()

        if os.path.exists(self.target) and os.path.getsize(self.target) > 0:
            print(get_msg(f"오류: 대상 파일 '{self.target}'이 비어 있지 않습니다.", f"Error: Target file '{self.target}' is not empty."))
            return
            
        # Ensure target exists
        open(self.target, "w", encoding="utf-8").close()

        print(f"\nTyper CLI STARTED")
        print(get_msg(f"원천: {self.source}", f"Source: {self.source}"))
        print(get_msg(f"대상: {self.target}", f"Target: {self.target}"))
        print(get_msg("가짜 타이핑이 활성화되었습니다. 아무 키나 누르면 대상 파일에 기록됩니다.", "Fake typing is active. Any key you press will write to the target file."))
        print(get_msg("종료하려면 ESC를 누르세요.", "Press ESC to exit."))
        print("="*40)

        self.recording = True
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        self.listener.join()

    def on_press(self, key):
        if key == keyboard.Key.esc:
            print(get_msg("\n타이퍼 CLI를 종료합니다...", "\nExiting Typer CLI..."))
            self.recording = False
            return False

        if not self.recording:
            return

        if self.cursor >= len(self.buffer_text):
            print(get_msg("\n원천 텍스트의 끝에 도달했습니다.", "\nEnd of source text reached."))
            return False

        try:
            # Only trigger on character keys (or space)
            if hasattr(key, 'char') and key.char is not None:
                pass
            elif key == keyboard.Key.space:
                pass
            else:
                return
        except:
            return

        count = random.randint(1, 5)
        chunk = self.buffer_text[self.cursor:self.cursor+count]
        self.cursor += count

        with open(self.target, "a", encoding="utf-8") as f:
            f.write(chunk)
            
        sys.stdout.write(f"\r{get_msg('진행률', 'Progress')}: {self.cursor}/{len(self.buffer_text)} bytes")
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Typer Basic CLI - Fake Typing Copier")
    parser.add_argument("--source", required=True, help="Source text file")
    parser.add_argument("--target", required=True, help="Target text file (must be empty)")
    
    args = parser.parse_args()
    typer = TyperCLI(args.source, args.target)
    typer.start()

if __name__ == "__main__":
    main()
