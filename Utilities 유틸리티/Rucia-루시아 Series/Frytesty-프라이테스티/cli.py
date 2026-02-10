#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Frytesty CLI - Algorithm Problem Auto-Tester
# Rheehose (Rhee Creative) 2008-2026

import os
import subprocess
import time
import sys
import argparse
import difflib

def run_test(script, in_data, expected):
    start_time = time.time()
    try:
        process = subprocess.Popen(
            ["python3", script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=in_data, timeout=5)
        elapsed = (time.time() - start_time) * 1000 # ms
        
        actual = stdout.strip()
        passed = actual == expected.strip()
        
        return {
            "passed": passed,
            "actual": actual,
            "expected": expected.strip(),
            "elapsed": elapsed,
            "error": stderr.strip()
        }
    except Exception as e:
        return {
            "passed": False,
            "actual": "ERROR",
            "expected": expected.strip(),
            "elapsed": 0,
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Frytesty CLI - Auto-Tester")
    parser.add_argument("--script", required=True, help="Target script to test")
    parser.add_argument("--input", help="Input string for the test")
    parser.add_argument("--expected", help="Expected output string")
    parser.add_argument("--file", help="Path to a test file (input and expected separated by '---')")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.script):
        print(f"Error: Script '{args.script}' not found.")
        return

    test_cases = []
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, "r") as f:
                parts = f.read().split("---")
                if len(parts) >= 2:
                    test_cases.append((parts[0].strip(), parts[1].strip()))
        else:
            print(f"Error: Test file '{args.file}' not found.")
            return
    elif args.input and args.expected:
        test_cases.append((args.input, args.expected))
    else:
        print("Error: Provide either --input/--expected or --file.")
        return

    print(f"\nFrytesty CLI - Testing: {args.script}")
    print("="*40)
    
    for i, (in_data, expected) in enumerate(test_cases):
        res = run_test(args.script, in_data, expected)
        status = "PASS" if res["passed"] else "FAIL"
        print(f"Case #{i+1}: {status} ({res['elapsed']:.2f}ms)")
        if not res["passed"]:
            print(f"  Expected: {res['expected']}")
            print(f"  Actual:   {res['actual']}")
            if res["error"]:
                print(f"  Error:    {res['error']}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
