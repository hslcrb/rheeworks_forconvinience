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
from pynput import keyboard

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
        print(f"\n[POMODORO] Focus session started ({self.work_seconds//60} min)")
        print("Press Ctrl+C to cancel.")
        try:
            while self.work_seconds > 0 and self.running:
                sys.stdout.write(f"\rTime Remaining: {self.format_time(self.work_seconds)}")
                sys.stdout.flush()
                time.sleep(1)
                self.work_seconds -= 1
            if self.work_seconds <= 0:
                print("\n\n[FOCUS DONE] Time to rest!")
        except KeyboardInterrupt:
            print("\n\n[CANCELLED] Pomodoro timer stopped.")

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
            print("Error: Target file must be empty.")
            return

        open(self.target, "w", encoding="utf-8").close()
        self.recording = True
        print(f"\n[ENGINE] Fake Typing started. TARGET: {self.target}")
        print("Press ESC to stop.")
        
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
        sys.stdout.write(f"\rTyping Progress: {self.cursor}/{len(self.buffer_text)}")
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
