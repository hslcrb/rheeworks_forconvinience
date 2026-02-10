#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Typer Basic CLI - Fake Typing Copier
# Rheehose (Rhee Creative) 2008-2026

import os
import random
import time
import sys
import argparse
from pynput import keyboard

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
            print(f"Error: Source file '{self.source}' not found.")
            return

        with open(self.source, "r", encoding="utf-8") as f:
            self.buffer_text = f.read()

        if os.path.exists(self.target) and os.path.getsize(self.target) > 0:
            print(f"Error: Target file '{self.target}' is not empty.")
            return
            
        # Ensure target exists
        open(self.target, "w", encoding="utf-8").close()

        print(f"\nTyper CLI STARTED")
        print(f"Source: {self.source}")
        print(f"Target: {self.target}")
        print("Fake typing is active. Any key you press will write to the target file.")
        print("Press ESC to exit.")
        print("="*40)

        self.recording = True
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        self.listener.join()

    def on_press(self, key):
        if key == keyboard.Key.esc:
            print("\nExiting Typer CLI...")
            self.recording = False
            return False

        if not self.recording:
            return

        if self.cursor >= len(self.buffer_text):
            print("\nEnd of source text reached.")
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
            
        sys.stdout.write(f"\rProgress: {self.cursor}/{len(self.buffer_text)} bytes")
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
