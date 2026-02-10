#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Typer Pomodoro CLI - Focus Timer & Hidden Typing Tool
# Rheehose (Rhee Creative) 2008-2026

import os
import time
import random
import sys
import argparse
import threading
import datetime
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

class PomodoroCLI:
    def __init__(self, work_min=25):
        self.work_seconds = work_min * 60
        self.running = False

    def format_time(self, s):
        m = s // 60
        s %= 60
        return f"{m:02}:{s:02}"

    def start(self):
        self.running = True
        print(f"\n[POMODORO] {get_msg('집중 세션 시작', 'Focus session started')} ({self.work_seconds//60} min)")
        print(get_msg("취소하려면 Ctrl+C를 누르세요.", "Press Ctrl+C to cancel."))
        try:
            while self.work_seconds > 0 and self.running:
                sys.stdout.write(f"\r{get_msg('남은 시간', 'Time Remaining')}: {self.format_time(self.work_seconds)}")
                sys.stdout.flush()
                time.sleep(1)
                self.work_seconds -= 1
            if self.work_seconds <= 0:
                print(f"\n\n[FOCUS DONE] {get_msg('휴식 시간입니다!', 'Time to rest!')}")
        except KeyboardInterrupt:
            print(f"\n\n[CANCELLED] {get_msg('포모도로 타이머가 중지되었습니다.', 'Pomodoro timer stopped.')}")

class TyperEngine:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.cursor = 0
        self.recording = False
        self.buffer_text = ""

    def start(self):
        with open(self.source, "r", encoding="utf-8") as f:
            self.buffer_text = f.read()
        
        if os.path.exists(self.target) and os.path.getsize(self.target) > 0:
            print(get_msg("오류: 대상 파일은 반드시 비어 있어야 합니다.", "Error: Target file must be empty."))
            return

        open(self.target, "w", encoding="utf-8").close()
        self.recording = True
        print(f"\n[ENGINE] {get_msg('가짜 타이핑 시작', 'Fake Typing started')}. TARGET: {self.target}")
        print(get_msg("중지하려면 ESC를 누르세요.", "Press ESC to stop."))
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.recording = False
            return False
            
        if not self.recording or self.cursor >= len(self.buffer_text):
            return

        try:
            if hasattr(key, 'char') and key.char: pass
            elif key == keyboard.Key.space: pass
            else: return
        except: return

        count = random.randint(1, 4)
        chunk = self.buffer_text[self.cursor:self.cursor+count]
        self.cursor += count
        with open(self.target, "a", encoding="utf-8") as f:
            f.write(chunk)
        sys.stdout.write(f"\r{get_msg('타이핑 진행률', 'Typing Progress')}: {self.cursor}/{len(self.buffer_text)}")
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Typer Pomodoro CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # Timer command
    timer_parser = subparsers.add_parser("timer", help="Start pomodoro timer")
    timer_parser.add_argument("--min", type=int, default=25, help="Work minutes")
    
    # Engine command
    engine_parser = subparsers.add_parser("engine", help="Start fake typing engine")
    engine_parser.add_argument("--source", required=True)
    engine_parser.add_argument("--target", required=True)
    
    args = parser.parse_args()
    
    if args.command == "timer":
        PomodoroCLI(args.min).start()
    elif args.command == "engine":
        TyperEngine(args.source, args.target).start()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
