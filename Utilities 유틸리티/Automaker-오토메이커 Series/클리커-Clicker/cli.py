#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Clicker CLI - Auto-Clicker Tool
# Rheehose (Rhee Creative) 2008-2026

import time
import threading
import sys
import argparse
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode
import locale

def get_msg(ko_msg, en_msg):
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith('ko'):
            return f"{ko_msg} / {en_msg}"
    except:
        pass
    return en_msg

class ClickerCLI:
    def __init__(self, delay=0.1, button='left'):
        self.delay = delay
        self.button = Button.left if button == 'left' else Button.right
        self.mouse = Controller()
        self.running = False
        self.exit_signal = False

    def start_clicking(self):
        self.running = True
        print(f"\n[CLICKER] {get_msg('시작됨', 'Started')}.")

    def stop_clicking(self):
        self.running = False
        print(f"\n[CLICKER] {get_msg('중지됨', 'Stopped')}.")

    def toggle(self):
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def run_engine(self):
        while not self.exit_signal:
            if self.running:
                self.mouse.click(self.button)
                time.sleep(self.delay)
            else:
                time.sleep(0.1)

    def on_press(self, key):
        if key == KeyCode(char='s'):
            self.toggle()
        elif key == KeyCode(char='e'):
            print(f"\n[CLICKER] {get_msg('종료 중...', 'Exiting...')}")
            self.exit_signal = True
            return False

def main():
    parser = argparse.ArgumentParser(description="Clicker CLI - Auto-Clicker Tool")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between clicks in seconds")
    parser.add_argument("--button", choices=['left', 'right'], default='left', help="Mouse button to click")
    
    args = parser.parse_args()
    
    clicker = ClickerCLI(args.delay, args.button)
    
    print(get_msg(f"\nClicker CLI - 명령 대기 중", f"\nClicker CLI - Waiting for commands"))
    print(f"{get_msg('지연 시간', 'Delay')}: {args.delay}s | {get_msg('버튼', 'Button')}: {args.button}")
    print(get_msg("'s'는 시작/정지, 'e'는 종료", "Press 's' to START/STOP, 'e' to EXIT"))
    print("="*40)
    
    # Start engine thread
    engine_thread = threading.Thread(target=clicker.run_engine, daemon=True)
    engine_thread.start()
    
    # Listen for keys
    with Listener(on_press=clicker.on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
