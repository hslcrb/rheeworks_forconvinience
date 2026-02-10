#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Text Generator CLI - Dummy Text Tool
# Rheehose (Rhee Creative) 2008-2026

import random
import sys
import argparse
import locale

def get_msg(ko_msg, en_msg):
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith('ko'):
            return f"{ko_msg} / {en_msg}"
    except:
        pass
    return en_msg

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
KOREAN_DUMMY = "여우비 내리는 날에는 꽃들이 노래를 부르고, 푸른 바다 건너편에는 은하수가 흐릅니다. 가을 바람 소리에 귀를 기울이면 옛이야기가 들려오고, 아침 햇살은 창가에 머무며 새로운 시작을 알립니다."

def generate_text(count, mode):
    base_text = LOREM_IPSUM if mode == "latin" else KOREAN_DUMMY
    words = base_text.split()
    
    result = []
    for _ in range(count):
        chunk = random.sample(words, min(len(words), random.randint(5, 15)))
        result.append(" ".join(chunk))
    
    return "\n\n".join(result)

def main():
    parser = argparse.ArgumentParser(description=get_msg("텍스트 생성기 CLI - 더미 텍스트 도구", "Text Generator CLI - Dummy Text Tool"))
    parser.add_argument("--count", type=int, default=1, help=get_msg("생성할 단락 수", "Number of paragraphs to generate"))
    parser.add_argument("--mode", choices=['korean', 'latin'], default='korean', help=get_msg("언어 모드", "Language mode"))
    
    args = parser.parse_args()
    
    text = generate_text(args.count, args.mode)
    print(text)

if __name__ == "__main__":
    main()
