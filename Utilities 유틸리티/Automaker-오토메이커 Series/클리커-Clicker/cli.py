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

class ClickerCLI:
    def __init__(self, delay=0.1, button='left'):
        self.delay = delay
        self.button = Button.left if button == 'left' else Button.right
        self.mouse = Controller()
        self.running = False
        self.exit_signal = False

    def start_clicking(self):
        self.running = True
        print("\n[CLICKER] Started.")

    def stop_clicking(self):
        self.running = False
        print("\n[CLICKER] Stopped.")

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
            print("\n[CLICKER] Exiting...")
            self.exit_signal = True
            return False

def main():
    parser = argparse.ArgumentParser(description="Clicker CLI - Auto-Clicker Tool")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between clicks in seconds")
    parser.add_argument("--button", choices=['left', 'right'], default='left', help="Mouse button to click")
    
    args = parser.parse_args()
    
    clicker = ClickerCLI(args.delay, args.button)
    
    print(f"\nClicker CLI - Waiting for commands")
    print(f"Delay: {args.delay}s | Button: {args.button}")
    print("Press 's' to START/STOP, 'e' to EXIT")
    print("="*40)
    
    # Start engine thread
    engine_thread = threading.Thread(target=clicker.run_engine, daemon=True)
    engine_thread.start()
    
    # Listen for keys
    with Listener(on_press=clicker.on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
