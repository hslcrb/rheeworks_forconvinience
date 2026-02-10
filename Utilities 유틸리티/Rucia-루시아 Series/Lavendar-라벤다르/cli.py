#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Lavendar CLI - Laboratory File Auto-Backup Tool
# Rheehose (Rhee Creative) 2008-2026

import os
import shutil
import time
import datetime
import sys
import argparse

def log(message):
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    print(f"{timestamp} {message}")

def run_backup(source, dest, keep=10):
    try:
        if not os.path.exists(source):
            print(f"Error: Source directory '{source}' does not exist.")
            return False
        
        if not os.path.exists(dest):
            os.makedirs(dest)
            
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = os.path.join(dest, f"backup_{now}")
        
        log(f"Starting backup to {os.path.basename(target_path)}...")
        shutil.copytree(source, target_path)
        log("Backup Successful.")
        
        # Cleanup
        cleanup_old_backups(dest, keep)
        return True
    except Exception as e:
        log(f"ERROR: {str(e)}")
        return False

def cleanup_old_backups(dest, keep):
    try:
        backups = [os.path.join(dest, d) for d in os.listdir(dest) if d.startswith("backup_")]
        backups.sort(key=os.path.getmtime)
        
        while len(backups) > keep:
            oldest = backups.pop(0)
            shutil.rmtree(oldest)
            log(f"Removed old backup: {os.path.basename(oldest)}")
    except Exception as e:
        log(f"Cleanup Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Lavendar CLI - Auto-Backup Tool")
    parser.add_argument("--source", required=True, help="Source directory to backup")
    parser.add_argument("--dest", required=True, help="Destination directory for backups")
    parser.add_argument("--interval", type=int, default=0, help="Backup interval in minutes (0 for one-time)")
    parser.add_argument("--keep", type=int, default=10, help="Number of backups to keep")
    
    args = parser.parse_args()
    
    if args.interval == 0:
        run_backup(args.source, args.dest, args.keep)
    else:
        log(f"Starting continuous backup protection (every {args.interval} min)...")
        try:
            while True:
                run_backup(args.source, args.dest, args.keep)
                time.sleep(args.interval * 60)
        except KeyboardInterrupt:
            log("Backup protection stopped by user.")

if __name__ == "__main__":
    main()
