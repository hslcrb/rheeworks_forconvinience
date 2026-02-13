"""
StudyAI - MV - Python (Terminal-Style GUI)
터미널 스타일 GUI AI 채팅 애플리케이션 / Terminal-Style GUI AI Chat Application
PySide6 + Mistral AI API

Rheehose (Rhee Creative) 2008-2026
Licensed under Apache-2.0
"""

import sys
import os
import json
import random
import threading
import platform
import requests
import time
import locale
from datetime import datetime


def setup_input_method():
    """
    OS 독립적 입력 방식 설정 / OS-independent input method setup.
    We respect variables set in the launcher script (run_gui.sh).
    """
    if platform.system() != "Linux":
        return
    
    # We trust the environment variables set by run_gui.sh
    im_module = os.environ.get("QT_IM_MODULE", "")
    xmod = os.environ.get("XMODIFIERS", "")
    
    # If not set, provide a sensible default fallback for Linux
    if not im_module:
        os.environ["QT_IM_MODULE"] = "xim"
    if not xmod:
        os.environ["XMODIFIERS"] = "@im=fcitx"


# Must be called BEFORE QApplication import / QApplication import 전에 호출 필수
setup_input_method()

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QLineEdit, QLabel, QHBoxLayout, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer
from PySide6.QtGui import QFont, QTextCursor, QColor, QPalette, QKeyEvent

# Mistral API Configuration / Mistral API 설정
MISTRAL_API_URL = "https://www.rheehose.com" + "/api/ai/v1/juni/mistral/relay"

# Google Gemini API Configuration / Google Gemini API 설정
GEMINI_API_URL = "https://www.rheehose.com" + "/api/ai/v1/juni/gemini/relay"

# Default Model / 기본 모델
DEFAULT_MODEL = "mistral-tiny"
MAX_TOKENS = 32000

# Available Models / 사용 가능한 모델
AVAILABLE_MODELS = {
    "mistral-small-latest": "mistral",
    "mistral-medium-latest": "mistral",
    "gemini-2.0-flash": "google",
    "gemini-3-flash-preview": "google"
}

# Theme Definitions / 테마 정의
THEMES = {
    "dark": {
        "bg": "#1a1a1a",
        "fg": "#d4d4d4",
        "input_bg": "#1a1a1a",
        "input_fg": "#ffffff",
        "footer_bg": "#1a1a1a",
        "btn_bg": "#333333",
        "btn_fg": "#cccccc",
        "btn_hover": "#444444",
        "prompt_fg": "#6aff6a",
        "context_fg": "#666666",
        "selection_bg": "#ccff00", # Lime Green / 연두색
        "selection_fg": "#000000", # Black / 검정색
        "bold_fg": "#ffffff",
        "code_bg": "#2a2a2a",
        "code_fg": "#9cdcfe",
        "code_block_bg": "#2a2a2a",
        "code_block_border": "#6aff6a",
        "code_block_fg": "#c8c8c8"
    },
    "light": {
        "bg": "#f8f0ff", # Light Lavender / 연보라
        "fg": "#2d005d", # Dark Purple / 어두운 보라
        "input_bg": "#ffffff",
        "input_fg": "#000000",
        "footer_bg": "#efe0ff",
        "btn_bg": "#daafff",
        "btn_fg": "#4a148c",
        "btn_hover": "#c17fff",
        "prompt_fg": "#2e7d32",
        "context_fg": "#7e57c2",
        "selection_bg": "#d1c4e9", # Light Pastel Purple / 연한 파스텔 퍼플
        "selection_fg": "#1a1a1a", # Dark Grey / 어두운 회색
        "bold_fg": "#2d005d", # Match theme fg / 테마 fg와 일치
        "code_bg": "#e1bee7",
        "code_fg": "#4a148c",
        "code_block_bg": "#f3e5f5",
        "code_block_border": "#b39ddb",
        "code_block_fg": "#4a148c"
    }
}

# Simplified model groups for commands and dropdown / 명령 및 드롭다운을 위한 간소화된 모델 그룹
MODEL_GROUPS = {
    "Mistral": "mistral-small-latest",
    "Gemini": "gemini-3-flash-preview"
}

# Random greeting phrases / 랜덤 인사말 문구
GREETINGS = {
    "ko": [
        "안녕하세요? 무엇을 도와드릴까요?", "궁금한 것이 있으신가요?", "새로운 것을 배울 준비가 되셨나요?",
        "무엇이든 물어보세요!", "함께 탐구해 봅시다.", "알고 싶은 것이 무엇인가요?"
    ],
    "en": [
        "How are you?", "What's on your mind?", "Ready to learn something new?",
        "Ask me anything!", "Let's explore together.", "What would you like to know?",
        "Curious about something?", "How can I help you today?", "Let's get started!",
        "What are you studying?", "Need help with homework?", "Let's solve a problem!",
        "What's your question?", "Think. Ask. Learn.", "Knowledge awaits you.",
        "Let's dive in!", "What brings you here?", "Ready when you are.",
        "Let's figure it out together.", "Got a tough question?", "I'm here to help.",
        "Let's make today productive.", "What topic interests you?", "Fire away!",
        "Challenge me with a question.", "Learning never stops.", "Stay curious, stay sharp.",
        "One question at a time.", "Your study buddy is ready.", "Let's crack this together.",
        "No question is too small.", "Explore. Discover. Grow.", "What shall we learn today?",
        "Tell me what you need.", "Stuck on something?", "Let me help you out.",
        "Wisdom starts with a question.", "Every expert was once a beginner.",
        "Keep asking, keep growing.", "Your journey starts here.", "Think big, ask bigger.",
        "Let's build understanding.", "Dare to be curious.", "Questions are the answer.",
        "Unlock your potential.", "Let's make progress.", "What's the next challenge?",
        "I'm all ears.", "Bring it on!", "The world is your classroom."
    ]
}

# UI Strings / UI 문자열
UI_STRINGS = {
    "ko": {
        "title": "StudyAI Terminal - 파이썬 에디션",
        "btn_clear": "화면 지우기",
        "btn_reset": "대화 초기화",
        "btn_draw": "화면 복구",
        "btn_lang_target": "English",
        "prompt": "studyai>",
        "banner_title": "StudyAI Terminal",
        "banner_sub": "파이썬 에디션",
        "banner_hint": "질문을 입력하고 엔터를 누르세요.",
        "banner_cmd": "명령어: /clear, /sclear, /model, /draw, /trans, /help, /exit",
        "msg_sclear": "[SYSTEM] 세션 및 AI 기억이 초기화되었습니다.",
        "msg_clear": "[SYSTEM] 화면이 지워졌습니다. (기억 유지됨)",
        "msg_draw": "[SYSTEM] 화면이 복구되었습니다.",
        "msg_draw_fail": "[SYSTEM] 복구할 화면이 없습니다.",
        "msg_trans": "[SYSTEM] 언어가 한국어로 전환되었습니다."
    },
    "en": {
        "title": "StudyAI Terminal - Python Edition",
        "btn_clear": "Clear Screen",
        "btn_reset": "Reset Session",
        "btn_draw": "Restore Screen",
        "btn_lang_target": "한글",
        "prompt": "studyai>",
        "banner_title": "StudyAI Terminal",
        "banner_sub": "Python Edition",
        "banner_hint": "Type your question and press Enter.",
        "banner_cmd": "Commands: /clear, /sclear, /model, /draw, /trans, /help, /exit",
        "msg_sclear": "[SYSTEM] Session and memory cleared.",
        "msg_clear": "[SYSTEM] Screen cleared. (AI still remembers)",
        "msg_draw": "[SYSTEM] Screen restored.",
        "msg_draw_fail": "[SYSTEM] Nothing to draw.",
        "msg_trans": "[SYSTEM] Language switched to English."
    }
}

# System prompt / 시스템 프롬프트
SYSTEM_PROMPT = (
    "You are StudyAI, a smart study assistant running in a terminal-style interface. "
    "Adapt your response length to the question: "
    "- Simple/greeting questions: 1-2 sentences. "
    "- Factual questions: 1 short paragraph. "
    "- Explanations/how-to: concise but thorough, use bullet points. "
    "- Code requests: provide clean, commented code with brief explanation. "
    "- Deep analysis: comprehensive but well-structured with headers. "
    "Use markdown: ### headers, **bold**, `code`, ```code blocks```, lists. "
    "Never pad responses unnecessarily. Be precise and useful."
)

def _get_display_width(text):
    """Calculate display width of string (Korean = 2 units) / 문자열 표시 너비 계산 (한글=2칸)"""
    width = 0
    for char in text:
        if ord(char) > 0x7F:
            width += 2
        else:
            width += 1
    return width

def _center_text(text, width):
    """Centers text based on display width / 표시 너비 기준 가운데 정렬"""
    d_width = _get_display_width(text)
    pad = (width - d_width) // 2
    return " " * pad + text + " " * (width - d_width - pad)



class StreamSignals(QObject):
    """Signals for thread-safe streaming updates / 스레드 안전 스트리밍 업데이트 시그널"""
    chunk_received = Signal(str)
    stream_finished = Signal()
    stream_error = Signal(str)


def markdown_to_html(text, theme_name="dark"):
    """
    마크다운을 HTML로 변환 (터미널 스타일) / Convert markdown to HTML (terminal style).
    Supports: **bold**, *italic*, `inline code`, ```code blocks```, ### headers, - bullet lists.
    """
    t = THEMES[theme_name]
    import re
    lines = text.split("\n")
    html_parts = []
    in_code_block = False
    code_block_content = []
    
    for line in lines:
        # Code block toggle / 코드 블록 토글
        if line.strip().startswith("```"):
            if in_code_block:
                # Close code block / 코드 블록 닫기
                code_text = "\n".join(code_block_content)
                code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html_parts.append(
                    f'<div style="background-color:{t["code_block_bg"]}; padding:6px 10px; margin:4px 0; '
                    f'border-left:3px solid {t["code_block_border"]}; font-family:Monospace;">'
                    f'<pre style="margin:0; color:{t["code_block_fg"]};">{code_text}</pre></div>'
                )
                code_block_content = []
                in_code_block = False
            else:
                in_code_block = True
            continue
        
        if in_code_block:
            code_block_content.append(line)
            continue
        
        # Escape HTML / HTML 이스케이프
        line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Headers / 헤더 (### > ## > #)
        header_match = re.match(r'^(#{1,3})\s*(.*)', line)
        if header_match:
            level = len(header_match.group(1))
            header_text = header_match.group(2)
            # Apply inline formatting to header text / 헤더 텍스트에 인라인 서식 적용
            header_text = _apply_inline_md(header_text, theme_name)
            if level == 1:
                html_parts.append(f'<p style="color:{t["bold_fg"]}; font-weight:bold; font-size:15px; margin:6px 0;">{header_text}</p>')
            elif level == 2:
                html_parts.append(f'<p style="color:{t["prompt_fg"]}; font-weight:bold; font-size:14px; margin:4px 0;">{header_text}</p>')
            else:
                html_parts.append(f'<p style="color:{t["prompt_fg"]}; font-weight:bold; margin:3px 0;">{header_text}</p>')
            continue
        
        # Bullet lists / 불릿 목록
        bullet_match = re.match(r'^(\s*)[-*]\s+(.*)', line)
        if bullet_match:
            indent = len(bullet_match.group(1))
            item_text = _apply_inline_md(bullet_match.group(2), theme_name)
            pad = "&nbsp;" * (indent + 2)
            html_parts.append(f'<p style="margin:1px 0;">{pad}• {item_text}</p>')
            continue
        
        # Numbered lists / 숫자 목록
        num_match = re.match(r'^(\s*)\d+[.)]\s+(.*)', line)
        if num_match:
            indent = len(num_match.group(1))
            item_text = _apply_inline_md(num_match.group(2), theme_name)
            pad = "&nbsp;" * (indent + 2)
            html_parts.append(f'<p style="margin:1px 0;">{pad}▸ {item_text}</p>')
            continue
        
        # Regular text with inline formatting / 인라인 서식이 있는 일반 텍스트
        if line.strip():
            html_parts.append(f'<p style="margin:1px 0;">{_apply_inline_md(line, theme_name)}</p>')
        else:
            html_parts.append('<p style="margin:2px 0;">&nbsp;</p>')
    
    # Close unclosed code block / 닫히지 않은 코드 블록 닫기
    if in_code_block and code_block_content:
        code_text = "\n".join(code_block_content)
        code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_parts.append(
            f'<div style="background-color:{t["code_block_bg"]}; padding:6px 10px; margin:4px 0; '
            f'border-left:3px solid {t["code_block_border"]}; font-family:Monospace;">'
            f'<pre style="margin:0; color:{t["code_block_fg"]};">{code_text}</pre></div>'
        )
    
    return "".join(html_parts)


# Hangul Automata Logic / 한글 오토마타 로직
class HangulAutomata:
    """
    Simple 2-beolsik Hangul Automata / 간단한 2벌식 한글 오토마타.
    Handles Jamo combination (Cho/Jung/Jong).
    """
    CHO = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
        'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]
    JUNG = [
        'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
        'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'
    ]
    JONG = [
        '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
        'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
        'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]

    # Jamo Mapping / 자모 매핑 (QWERTY to Jamo)
    MAP = {
        'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ',
        'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
        'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ',
        'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
        'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ',
        'O': 'ㅒ', 'P': 'ㅖ'
    }

    # Complex Jamo Combination / 복합 자모 조합
    COMPLEX_JUNG = {
        ('ㅏ', 'ㅣ'): 'ㅐ', ('ㅑ', 'ㅣ'): 'ㅒ', ('ㅓ', 'ㅣ'): 'ㅔ', ('ㅕ', 'ㅣ'): 'ㅖ',
        ('ㅗ', 'ㅏ'): 'ㅘ', ('ㅗ', 'ㅐ'): 'ㅙ', ('ㅗ', 'ㅣ'): 'ㅚ',
        ('ㅜ', 'ㅓ'): 'ㅝ', ('ㅜ', 'ㅔ'): 'ㅞ', ('ㅜ', 'ㅣ'): 'ㅟ',
        ('ㅡ', 'ㅣ'): 'ㅢ', ('ㅘ', 'ㅣ'): 'ㅙ', ('ㅝ', 'ㅣ'): 'ㅞ'
    }
    COMPLEX_JONG = {
        ('ㄱ', 'ㅅ'): 'ㄳ', ('ㄴ', 'ㅈ'): 'ㄵ', ('ㄴ', 'ㅎ'): 'ㄶ',
        ('ㄹ', 'ㄱ'): 'ㄺ', ('ㄹ', 'ㅁ'): 'ㄻ', ('ㄹ', 'ㅂ'): 'ㄼ',
        ('ㄹ', 'ㅅ'): 'ㄽ', ('ㄹ', 'ㄾ'): 'ㄾ', ('ㄹ', 'ㅍ'): 'ㄿ',
        ('ㄹ', 'ㅎ'): 'ㅀ', ('ㅂ', 'ㅅ'): 'ㅄ',
        ('ㅅ', 'ㅅ'): 'ㅆ', ('ㄱ', 'ㄱ'): 'ㄲ'  # Support double-typing for double consonants
    }

    def __init__(self):
        self.reset()

    def reset(self):
        """Initializes automata state / 오토마타 상태 초기화"""
        self.cho = -1
        self.jung = -1
        self.jong = -1
        self.jong_is_combined = False
        self.buffer = ""

    def decompose(self, char):
        """
        Decomposes a finished Hangul character into Jamo indices.
        완성된 한글 한 글자를 자모 인덱스로 분해합니다.
        """
        code = ord(char)
        if not (0xAC00 <= code <= 0xD7A3):
            # Not a Hangul syllable / 한글 음절이 아님
            if char in self.CHO:
                self.cho = self.CHO.index(char)
                self.jung = -1
                self.jong = -1
                return True
            return False

        code -= 0xAC00
        self.jong = code % 28
        self.jung = (code // 28) % 21
        self.cho = (code // 28) // 21
        # Jong 0 means no jongseong
        if self.jong == 0:
            self.jong = -1
        return True

    def backspace(self):
        """
        Deletes one Jamo from the current composition.
        현재 조합 중인 글자에서 자모 하나를 지웁니다.
        """
        if self.jong != -1:
            # Check complex jong / 복합 종성 분체
            current_jong = self.JONG[self.jong]
            for (j1, j2), combined in self.COMPLEX_JONG.items():
                if combined == current_jong:
                    self.jong = self.JONG.index(j1)
                    return self.combine()
            self.jong = -1
        elif self.jung != -1:
            # Check complex jung / 복합 중성 분체
            current_jung = self.JUNG[self.jung]
            for (j1, j2), combined in self.COMPLEX_JUNG.items():
                if combined == current_jung:
                    self.jung = self.JUNG.index(j1)
                    return self.combine()
            self.jung = -1
        elif self.cho != -1:
            self.cho = -1
        
        return self.combine()


    def combine(self):
        if self.cho == -1:
            return self.buffer
        
        # Base Hangul Char: 0xAC00
        cho_idx = self.cho
        jung_idx = self.jung if self.jung != -1 else 0
        jong_idx = self.jong if self.jong != -1 else 0
        
        if self.jung == -1: # Consonant only
            return self.CHO[cho_idx]
            
        code = 0xAC00 + (cho_idx * 21 * 28) + (jung_idx * 28) + jong_idx
        return chr(code)

    def process_key(self, key):
        """Processes a char key, returns (committed, current_composition)"""
        # Normalize Syllable Jamos to Compatibility Jamos / 첫/가/끝 자모를 호환용 자모로 정규화
        j_map = {
            0x1100: 'ㄱ', 0x1101: 'ㄲ', 0x1102: 'ㄴ', 0x1103: 'ㄷ', 0x1104: 'ㄸ', 0x1105: 'ㄹ',
            0x1106: 'ㅁ', 0x1107: 'ㅂ', 0x1108: 'ㅃ', 0x1109: 'ㅅ', 0x110A: 'ㅆ', 0x110B: 'ㅇ',
            0x110C: 'ㅈ', 0x110D: 'ㅉ', 0x110E: 'ㅊ', 0x110F: 'ㅋ', 0x1110: 'ㅌ', 0x1111: 'ㅍ', 0x1112: 'ㅎ',
            0x1161: 'ㅏ', 0x1162: 'ㅐ', 0x1163: 'ㅑ', 0x1164: 'ㅒ', 0x1165: 'ㅓ', 0x1166: 'ㅔ',
            0x1167: 'ㅕ', 0x1168: 'ㅖ', 0x1169: 'ㅗ', 0x116A: 'ㅘ', 0x116B: 'ㅙ', 0x116C: 'ㅚ',
            0x116D: 'ㅛ', 0x116E: 'ㅜ', 0x116F: 'ㅝ', 0x1170: 'ㅞ', 0x1171: 'ㅟ', 0x1172: 'ㅠ',
            0x1173: 'ㅡ', 0x1174: 'ㅢ', 0x1175: 'ㅣ',
            0x11A8: 'ㄱ', 0x11A9: 'ㄲ', 0x11AA: 'ㄳ', 0x11AB: 'ㄴ', 0x11AC: 'ㄵ', 0x11AD: 'ㄶ',
            0x11AE: 'ㄷ', 0x11AF: 'ㄹ', 0x11B0: 'ㄺ', 0x11B1: 'ㄻ', 0x11B2: 'ㄼ', 0x11B3: 'ㄽ',
            0x11B4: 'ㄾ', 0x11B5: 'ㄿ', 0x11B6: 'ㅀ', 0x11B7: 'ㅁ', 0x11B8: 'ㅂ', 0x11B9: 'ㅄ',
            0x11BA: 'ㅅ', 0x11BB: 'ㅆ', 0x11BC: 'ㅇ', 0x11BD: 'ㅈ', 0x11BE: 'ㅊ', 0x11BF: 'ㅋ',
            0x11C0: 'ㅌ', 0x11C1: 'ㅍ', 0x11C2: 'ㅎ'
        }
        if ord(key) in j_map:
            key = j_map[ord(key)]

        # Mapping from QWERTY or direct Jamo input (Normalize to Compatibility Jamo)
        # QWERTY 또는 직접 입력 자모 매핑 (호환용 자모로 정규화)
        jamo_norm = {
            'ㅃ': 'ㅃ', 'ㅉ': 'ㅉ', 'ㄸ': 'ㄸ', 'ㄲ': 'ㄲ', 'ㅆ': 'ㅆ',
            'ㅐ': 'ㅐ', 'ㅒ': 'ㅒ', 'ㅔ': 'ㅔ', 'ㅖ': 'ㅖ', 'ㅘ': 'ㅘ', 'ㅙ': 'ㅙ', 'ㅚ': 'ㅚ',
            'ㅝ': 'ㅝ', 'ㅞ': 'ㅞ', 'ㅟ': 'ㅟ', 'ㅢ': 'ㅢ'
        }
        if key in self.MAP:
            jamo = self.MAP[key]
        elif key in self.CHO or key in self.JUNG or key in self.JONG:
            jamo = key
        elif key in jamo_norm:
            jamo = jamo_norm[key]
        else:
            committed = self.combine()
            self.reset()
            return committed + key, ""

        # 1. Start or Cho / 초성 시작 또는 글자 없음
        if self.cho == -1:
            if jamo in self.CHO:
                self.cho = self.CHO.index(jamo)
                return "", self.combine()
            else: # Solo vowel / 단독 모음
                return jamo, ""

        # 2. Jung (Currently only have Cho)
        if self.jung == -1:
            if jamo in self.JUNG:
                self.jung = self.JUNG.index(jamo)
                return "", self.combine()
            else: # New Cho (Commit previous)
                prev = self.combine()
                self.reset()
                self.cho = self.CHO.index(jamo)
                return prev, self.combine()

        # 3. Jong or Complex Jung
        if self.jong == -1:
            # Check complex jung / 복합 모음 조합
            cur_jung = self.JUNG[self.jung]
            if (cur_jung, jamo) in self.COMPLEX_JUNG:
                new_jung = self.COMPLEX_JUNG[(cur_jung, jamo)]
                self.jung = self.JUNG.index(new_jung)
                return "", self.combine()
            
            # Start Jong / 종성 시작
            if jamo in self.JONG:
                self.jong = self.JONG.index(jamo)
                self.jong_is_combined = False
                return "", self.combine()
            
            # If jamo is not in JONG but is a valid CHO (like ㄸ, ㅃ, ㅉ), start new block
            # 종성이 될 수 없는 자음(ㄸ, ㅃ, ㅉ 등)인 경우 새 글자 시작
            prev = self.combine()
            self.reset()
            if jamo in self.CHO:
                self.cho = self.CHO.index(jamo)
                return prev, self.combine()
            else:
                return prev + jamo, ""

        # 4. Complex Jong or Break Jong to new Cho
        if jamo in self.JUNG:
            # Shift Jong to become new Cho / 종성을 다음 글자 초성으로 이동 (연음)
            jong_char = self.JONG[self.jong]
            
            # Smart shifting for double consonants / 쌍자음 지능형 연음
            # If combined (ㄱ+ㄱ, ㅅ+ㅅ), split them (e.g., 국가)
            # If single key (Shift+R, Shift+T), move as a whole (e.g., 닦아, 있어)
            if jong_char in ['ㄲ', 'ㅆ'] and self.jong_is_combined:
                # Fall through to COMPLEX_JONG split logic below
                pass
            elif jong_char in ['ㄲ', 'ㅆ']:
                # Move as a whole / 통째로 이동
                self.jong = 0 # No jong
                prev = self.combine()
                self.reset()
                self.cho = self.CHO.index(jong_char)
                self.jung = self.JUNG.index(jamo)
                return prev, self.combine()

            # If complex jong, break it / 복합 종성 분해 (ㄺ -> ㄹ + ㄱ)
            for (j1, j2), combined in self.COMPLEX_JONG.items():
                if combined == jong_char:
                    # Keep j1 as jong, j2 becomes new cho
                    self.jong = self.JONG.index(j1)
                    prev = self.combine()
                    self.reset()
                    self.cho = self.CHO.index(j2)
                    self.jung = self.JUNG.index(jamo)
                    return prev, self.combine()
            
            # Simple jong becomes new cho / 단순 종성이 다음 초성으로
            self.jong = 0 # No jong
            prev = self.combine()
            self.reset()
            self.cho = self.CHO.index(jong_char)
            self.jung = self.JUNG.index(jamo)
            return prev, self.combine()

        # Check complex jong / 복합 종성 조합
        cur_jong = self.JONG[self.jong]
        if (cur_jong, jamo) in self.COMPLEX_JONG:
            new_jong = self.COMPLEX_JONG[(cur_jong, jamo)]
            self.jong = self.JONG.index(new_jong)
            self.jong_is_combined = True
            return "", self.combine()

        # New block / 시러운 글자 시작
        prev = self.combine()
        self.reset()
        if jamo in self.CHO:
            self.cho = self.CHO.index(jamo)
            return prev, self.combine()
        else:
            return prev + jamo, ""


class HangulLineEdit(QLineEdit):
    """
    Custom LineEdit with internal Hangul engine / 자체 한글 엔진을 포함한 LineEdit.
    Toggles mode with Right Alt (Hangul key).
    """
    mode_changed = Signal(bool) # Signal for mode change / 모드 변경 신호

    def __init__(self, parent=None):

        super().__init__(parent)
        self.is_hangul = False
        self.automata = HangulAutomata()
        self.temp_composition = ""
        
        # Setup autocompletion / 자동완성 설정
        from PySide6.QtWidgets import QCompleter
        from PySide6.QtCore import QStringListModel
        self.commands = [
            "/clear", "/help", "/exit", 
            "/sclear", "/draw", "/trans"
        ]
        self.completer = QCompleter(self.commands, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self.completer)

    def set_mode(self, is_hangul):
        """External control of mode / 외부에서 모드 제어"""
        if self.is_hangul != is_hangul:
            self.commit_composition()
            self.is_hangul = is_hangul
            mode_str = "KO" if self.is_hangul else "EN"
            # print(f"[MODE] Switched to {mode_str}") # Debug print
            return True
        return False


    def keyPressEvent(self, event: QKeyEvent):
        # Toggle Hangul mode / 한영 전환
        if event.key() in (Qt.Key_AltGr, 108, 65513, Qt.Key_Hangul) or \
           (event.key() == Qt.Key_Alt and event.modifiers() & Qt.AltModifier):
            self.commit_composition()
            self.is_hangul = not self.is_hangul
            self.mode_changed.emit(self.is_hangul)
            return

        # Trigger completer for '/' / 슬래시 입력 시 자동완성 트리거
        if event.text() == "/":
            self.is_hangul = False # Switch to English temporarily for commands
            super().keyPressEvent(event)
            self.completer.complete()
            return

        if not self.is_hangul:
            super().keyPressEvent(event)
            return

        # Handle Backspace / 백스페이스 처리 (자모 단위 삭제)
        if event.key() == Qt.Key_Backspace:
            if self.temp_composition:
                # Decompose current composition / 현재 조합 중인 글자 분해
                self.temp_composition = self.automata.backspace()
                self.update_display()
            else:
                # No composition, try to decompose the character before cursor
                # 커서 앞의 글자를 가져와서 분해 시도
                cursor_pos = self.cursorPosition()
                if cursor_pos > 0:
                    text = self.text()
                    char_to_del = text[cursor_pos-1]
                    if self.automata.decompose(char_to_del):
                        # Delete the character from LineEdit first
                        self.setSelection(cursor_pos-1, 1)
                        self.del_()
                        # Now it's in composition mode
                        self.temp_composition = self.automata.backspace()
                        self.update_display()
                    else:
                        super().keyPressEvent(event)
                else:
                    super().keyPressEvent(event)
            return


        # Handle Return/Enter / 엔터 처리
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.commit_composition()
            super().keyPressEvent(event)
            return

        # Handle text input / 텍스트 입력 처리
        text = event.text()
        if not text or len(text) > 1 or not text.isprintable():
            # Special keys or non-char input / 특수 키 또는 문자 아닌 입력
            # Just commit and let parent handle it
            self.commit_composition()
            super().keyPressEvent(event)
            return

        # Process with automata / 오토마타로 처리
        committed, current = self.automata.process_key(text)
        
        # Clear previous selection (composition) / 이전 조합 문자 제거
        if self.hasSelectedText():
            self.del_()
            
        if committed:
            self.insert(committed)
        
        self.temp_composition = current
        self.update_display()

    def commit_composition(self):
        if self.temp_composition:
            self.deselect()
            # Move cursor to end of composition / 커서를 조합 문자 끝으로 이동
            self.setSelection(self.cursorPosition(), 0)
            self.temp_composition = ""
            self.automata.reset()

    def update_display(self):
        """
        Shows composition char at cursor using selection trick.
        시각적으로 조합 중인 글자를 커서 위치에 선택 상태로 표시.
        """
        # Note: insert() will replace any current selection
        # insert()는 현재 선택된 영역을 대체함
        pos = self.cursorPosition()
        if self.hasSelectedText():
            # If we already have a composition, the cursor is at the end of it
            # 이미 조합 중인 경우, 커서는 선택 영역의 끝에 있음
            pos = self.selectionStart()
        
        self.insert(self.temp_composition)
        
        if self.temp_composition:
            # Select the newly inserted text to show it's "in-progress"
            self.setSelection(pos, len(self.temp_composition))


    def inputMethodEvent(self, event):
        # Disable system input method to prevent conflict / 시스템 입력기 충돌 방지
        event.ignore()


def _apply_inline_md(text, theme_name="dark"):
    """
    인라인 마크다운 서식 적용 / Apply inline markdown formatting.
    Supports: **bold**, *italic*, `code`
    """
    t = THEMES[theme_name]
    import re
    # Inline code / 인라인 코드: `text`
    text = re.sub(
        r'`([^`]+)`',
        f'<span style="background-color:{t["code_bg"]}; color:{t["code_fg"]}; padding:1px 4px;">\\1</span>',
        text
    )
    # Bold / 볼드: **text**
    text = re.sub(r'\*\*([^*]+)\*\*', f'<b style="color:{t["bold_fg"]};">\\1</b>', text)
    # Italic / 이탤릭: *text*
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
    return text


class StudyAITerminal(QMainWindow):
    """Main terminal window / 메인 터미널 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.conversation_history = []
        self.total_tokens = 0
        self.is_streaming = False
        self.current_response = ""
        self.dot_count = 0
        self.dot_timer = None
        self.last_screen_html = "" # For /draw restore
        self.current_model = DEFAULT_MODEL
        self.current_theme = "dark" # Initial theme / 초기 테마
        
        # UI language based on locale / 로캘 기반 UI 언어
        try:
            # sys_lang = locale.getdefaultlocale()[0] # Deprecated
            sys_lang, _ = locale.getlocale()
            if not sys_lang:
                # setlocale often needs to be called once to populate getlocale
                locale.setlocale(locale.LC_ALL, "")
                sys_lang, _ = locale.getlocale()
            self.ui_lang = "ko" if sys_lang and "ko" in sys_lang.lower() else "en"
        except:
            self.ui_lang = "en"
            
        self.signals = StreamSignals()
        self.signals.chunk_received.connect(self.on_chunk_received)
        self.signals.stream_error.connect(self.on_stream_error) # Corrected from error_occurred
        self.signals.stream_finished.connect(self.on_stream_finished)
        
        self.setup_ui()
        self.sync_language_state()
        # show_banner is called inside sync_language_state if needed
        # sync_language_state 내부에서 필요한 경우 show_banner가 호출됨

    
    def setup_ui(self):
        """Setup the terminal UI / 터미널 UI 설정"""
        self.setWindowTitle("StudyAI Terminal - Python Edition")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
        
        # Central widget / 중앙 위젯
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header area (Theme Buttons) / 상단 영역 (테마 버튼)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 12, 5)
        header_layout.addStretch()
        
        theme_btn_style = """
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 2px 8px;
                font-family: Monospace;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #ffffff;
            }
        """
        
        self.btn_theme_light = QPushButton("LIGHT")
        self.btn_theme_light.setCursor(Qt.PointingHandCursor)
        self.btn_theme_light.setStyleSheet(theme_btn_style)
        self.btn_theme_light.clicked.connect(lambda: self.set_theme("light"))
        
        self.btn_theme_dark = QPushButton("DARK")
        self.btn_theme_dark.setCursor(Qt.PointingHandCursor)
        self.btn_theme_dark.setStyleSheet(theme_btn_style)
        self.btn_theme_dark.clicked.connect(lambda: self.set_theme("dark"))
        
        header_layout.addWidget(self.btn_theme_light)
        header_layout.addWidget(self.btn_theme_dark)
        
        header_container = QWidget()
        header_container.setObjectName("header_container")
        header_container.setLayout(header_layout)
        layout.addWidget(header_container)
        
        # Terminal output / 터미널 출력
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        # Using a more robust font / 보다 견고한 폰트 사용
        self.terminal.setFont(QFont("DejaVu Sans Mono, monospace", 11))
        layout.addWidget(self.terminal)
        
        # Input area / 입력 영역
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(12, 6, 12, 8)
        input_layout.setSpacing(8)
        
        # Prompt label / 프롬프트 레이블
        self.prompt_label = QLabel("studyai>")
        self.prompt_label.setFont(QFont("Monospace", 12, QFont.Bold))
        self.prompt_label.setStyleSheet("color: #6aff6a; background: transparent;")
        input_layout.addWidget(self.prompt_label)
        
        # Input field / 입력 필드
        self.input_field = HangulLineEdit()
        self.input_field.mode_changed.connect(self.on_mode_changed)
        self.input_field.setFont(QFont("Monospace", 12))

        self.input_field.returnPressed.connect(self.on_enter)
        input_layout.addWidget(self.input_field)
        
        self.input_container = QWidget()
        self.input_container.setLayout(input_layout)
        layout.addWidget(self.input_container)
        
        # Footer area (Buttons + Context) / 하단 영역
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(12, 4, 12, 4)
        footer_layout.setSpacing(10)
        
        # Action Buttons
        btn_style = """
            QPushButton {
                background-color: #333333;
                color: #cccccc;
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                font-family: Monospace;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #444444; color: #ffffff; }
        """
        
        self.btn_clear = QPushButton()
        self.btn_clear.setStyleSheet(btn_style)
        self.btn_clear.clicked.connect(lambda: self.execute_command("/clear"))
        
        self.btn_reset = QPushButton()
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_reset.clicked.connect(lambda: self.execute_command("/sclear"))
        
        self.btn_draw = QPushButton()
        self.btn_draw.setStyleSheet(btn_style)
        self.btn_draw.clicked.connect(lambda: self.execute_command("/draw"))
        
        # Model Selector Dropdown / 모델 선택 드롭다운
        self.model_selector = QComboBox()
        self.model_selector.addItems(list(MODEL_GROUPS.keys()))
        self.model_selector.currentIndexChanged.connect(self.on_model_selected)
        self.model_selector.setFixedWidth(100)
        self.model_selector.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 2px 5px;
                font-family: Monospace;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #888888;
                margin-top: 2px;
            }
            QComboBox QAbstractItemView {
                background-color: #222222;
                color: #cccccc;
                selection-background-color: #444444;
                border: 1px solid #444444;
            }
        """)
        
        footer_layout.addWidget(self.btn_clear)
        footer_layout.addWidget(self.btn_reset)
        footer_layout.addWidget(self.btn_draw)
        footer_layout.addWidget(self.model_selector)
        footer_layout.addStretch()
        
        # Context bar
        self.context_bar = QLabel("Context: 0/32000 tokens (0%)")
        self.context_bar.setFont(QFont("Monospace", 9))
        footer_layout.addWidget(self.context_bar)
        
        # Toggle Button
        self.lang_btn = QPushButton()
        self.lang_btn.setFixedWidth(80)
        self.lang_btn.setFont(QFont("Monospace", 10, QFont.Bold))
        self.lang_btn.clicked.connect(self.toggle_lang)
        footer_layout.addWidget(self.lang_btn)
        
        self.footer_container = QWidget()
        self.footer_container.setLayout(footer_layout)
        layout.addWidget(self.footer_container)
        
        self.apply_theme() # Apply initial theme / 초기 테마 적용
        self.update_ui_texts()
        
        # Focus input
        self.input_field.setFocus()

    def execute_command(self, cmd):
        self.input_field.setText(cmd)
        self.on_enter()

    def sync_language_state(self):
        """Syncs all lang-related states / 모든 언어 관련 상태 동기화"""
        is_ko = (self.ui_lang == "ko")
        self.input_field.set_mode(is_ko)
        self.update_ui_texts()
        self.update_lang_btn_style()
        
        # If no conversation yet, refresh banner to show new language
        # 대화가 시작되지 않았다면 새 언어로 배너를 새로고침
        if len(self.conversation_history) == 0:
            self.terminal.clear()
            self.show_banner()


    def on_mode_changed(self, is_ko):
        """Handle mode change from hotkey / 핫키를 통한 모드 변경 처리"""
        self.ui_lang = "ko" if is_ko else "en"
        self.update_ui_texts()
        self.update_lang_btn_style()

    def toggle_lang(self):
        """Manual toggle via button / 버튼을 통한 수동 전환"""
        self.ui_lang = "en" if self.ui_lang == "ko" else "ko"
        self.sync_language_state()

    def set_theme(self, theme_name):
        """Set the current theme and refresh UI / 테마 설정 및 UI 갱신"""
        if theme_name in THEMES and self.current_theme != theme_name:
            self.current_theme = theme_name
            self.apply_theme()
            # Mark current theme button / 현재 테마 버튼 표시
            self.update_theme_buttons()

    def apply_theme(self):
        """Apply current theme colors to all widgets / 모든 위젯에 현재 테마 색상 적용"""
        t = THEMES[self.current_theme]
        
        # Application Palette / 애플리케이션 팔레트
        palette = QApplication.palette()
        palette.setColor(QPalette.Window, QColor(t['bg']))
        palette.setColor(QPalette.WindowText, QColor(t['fg']))
        palette.setColor(QPalette.Base, QColor(t['bg']))
        palette.setColor(QPalette.AlternateBase, QColor(t['bg']))
        palette.setColor(QPalette.ToolTipBase, QColor(t['bg']))
        palette.setColor(QPalette.ToolTipText, QColor(t['fg']))
        palette.setColor(QPalette.Text, QColor(t['fg']))
        palette.setColor(QPalette.Button, QColor(t['btn_bg']))
        palette.setColor(QPalette.ButtonText, QColor(t['btn_fg']))
        palette.setColor(QPalette.Highlight, QColor(t['selection_bg']))
        palette.setColor(QPalette.HighlightedText, QColor(t['selection_fg']))
        QApplication.setPalette(palette)

        # Central widget and layout containers / 중앙 위젯 및 컨테이너
        self.centralWidget().setStyleSheet(f"background-color: {t['bg']};")
        
        # Terminal styling / 터미널 스타일링
        self.terminal.setStyleSheet(f"""
            QTextEdit {{
                background-color: {t['bg']};
                color: {t['fg']};
                border: none;
                padding: 12px;
                selection-background-color: {t['selection_bg']};
                selection-color: {t['selection_fg']};
            }}
        """)
        
        # Input Section / 입력 섹션
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {t['input_bg']};
                color: {t['input_fg']};
                border: none;
                padding: 4px;
                selection-background-color: {t['selection_bg']};
                selection-color: {t['selection_fg']};
            }}
        """)
        self.input_container.setStyleSheet(f"background-color: {t['input_bg']};")
        self.prompt_label.setStyleSheet(f"color: {t['prompt_fg']}; background: transparent;")
        
        # Buttons / 버튼
        btn_style = f"""
            QPushButton {{
                background-color: {t['btn_bg']};
                color: {t['btn_fg']};
                border: none;
                padding: 4px 10px;
                border-radius: 3px;
                font-family: Monospace;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {t['btn_hover']}; color: #ffffff; }}
        """
        self.btn_clear.setStyleSheet(btn_style)
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_draw.setStyleSheet(btn_style)
        self.lang_btn.setStyleSheet(btn_style)
        
        # Model Selector / 모델 선택기
        self.model_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {t['btn_bg']};
                color: {t['btn_fg']};
                border: 1px solid {t['btn_hover']};
                border-radius: 3px;
                padding: 2px 5px;
                font-family: Monospace;
                font-size: 11px;
            }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox::down-arrow {{
                image: none; border-left: 4px solid transparent; border-right: 4px solid transparent;
                border-top: 5px solid {t['btn_fg']}; margin-top: 2px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['bg']};
                color: {t['fg']};
                selection-background-color: {t['btn_hover']};
                border: 1px solid {t['btn_hover']};
            }}
        """)
        
        # Footer and Context / 하단 및 맥락
        self.footer_container.setStyleSheet(f"background-color: {t['footer_bg']}; border-top: 1px solid {t['btn_hover']};")
        self.context_bar.setStyleSheet(f"color: {t['context_fg']};")
        
        self.update_theme_buttons()

    def update_theme_buttons(self):
        """Update style of theme toggle buttons / 테마 토글 버튼 스타일 업데이트"""
        active_style = "border: 2px solid #6aff6a; color: #ffffff; background-color: #333333;"
        inactive_style = "border: 1px solid #444444; color: #888888; background-color: transparent;"
        
        # For simplicity, adjust standard theme_btn_style
        # 다크/라이트 테마에 상관없이 상단 버튼 가시성 유지
        base_style = """
            QPushButton {
                border-radius: 4px; padding: 2px 8px; font-family: Monospace; font-size: 10px; font-weight: bold;
            }
        """
        
        if self.current_theme == "dark":
            self.btn_theme_dark.setStyleSheet(base_style + "border: 1px solid #6aff6a; color: #6aff6a; background-color: #333333;")
            self.btn_theme_light.setStyleSheet(base_style + "border: 1px solid #444444; color: #888888; background-color: transparent;")
        else:
            self.btn_theme_light.setStyleSheet(base_style + "border: 1px solid #4a148c; color: #4a148c; background-color: #f3e5f5;")
            self.btn_theme_dark.setStyleSheet(base_style + "border: 1px solid #aaaaaa; color: #888888; background-color: transparent;")

    def on_model_selected(self, index):
        """Handle model selection from dropdown / 드롭다운 모델 선택 처리"""
        selected_group = self.model_selector.itemText(index)
        target_model = MODEL_GROUPS.get(selected_group)
        if target_model and self.current_model != target_model:
            self.current_model = target_model
            self.append_text(f"\n[SYSTEM] Model switched to: {selected_group}\n", "#569cd6")
            self.append_text(f"[INFO] Switch will apply to the NEXT question / 다음 질문부터 적용됩니다.\n", "#aaaaaa")

    def update_ui_texts(self):
        strs = UI_STRINGS[self.ui_lang]
        self.setWindowTitle(strs["title"])
        self.btn_clear.setText(strs["btn_clear"])
        self.btn_reset.setText(strs["btn_reset"])
        self.btn_draw.setText(strs["btn_draw"])
        self.prompt_label.setText(strs["prompt"])
        
        # Tooltips update / 툴팁 업데이트
        self.btn_clear.setToolTip(strs["btn_clear"])
        self.btn_reset.setToolTip(strs["btn_reset"])
        self.btn_draw.setToolTip(strs["btn_draw"])


    def update_lang_btn_style(self):
        """Update button appearance / 버튼 외형 업데이트"""
        strs = UI_STRINGS[self.ui_lang]
        self.lang_btn.setText(strs["btn_lang_target"])
        
        is_ko = (self.ui_lang == "ko")
        if is_ko:
            # High-visibility KO mode / 눈에 띄는 한국어 모드
            self.lang_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: 1px solid #005a9e;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #008be5;
                }
            """)
        else:
            # Subtle EN mode / 차분한 영어 모드
            self.lang_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #aaaaaa;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #444444;
                    color: white;
                }
            """)
    
    def append_text(self, text, color="#d4d4d4"):
        """Append plain text with color / 색상 일반 텍스트 추가"""
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        fmt = cursor.charFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        
        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()
    
    def append_html(self, html):
        """Append HTML content / HTML 콘텐츠 추가"""
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(html)
        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()
    
    def show_banner(self):
        """Show startup banner (HTML version for perfect alignment) / 시작 배너 표시 (완벽한 정렬을 위한 HTML 버전)"""
        strs = UI_STRINGS[self.ui_lang]
        greeting = random.choice(GREETINGS[self.ui_lang])
        
        # Logo remains English, but subtitle translates / 로고는 영어로 유지되지만 부제목은 번역됨
        title = "StudyAI Terminal"
        provider_name = AVAILABLE_MODELS.get(self.current_model, "mistral").title()
        subtitle = f"{strs['banner_sub']} • {provider_name} ({self.current_model})"
        
        # HTML Banner Box / HTML 배너 박스
        banner_html = f"""
        <div style="margin-bottom: 10px;">
            <table style="border: 2px solid #6aff6a; background-color: transparent; width: 100%; border-radius: 5px;">
                <tr>
                    <td style="padding: 15px; text-align: center;">
                        <div style="color: #6aff6a; font-family: 'DejaVu Sans Mono', monospace; font-size: 18pt; font-weight: bold; margin-bottom: 5px;">
                            {title}
                        </div>
                        <div style="color: #888888; font-family: 'DejaVu Sans Mono', monospace; font-size: 11pt;">
                            {subtitle}
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        <div style="color: #aaaaaa; margin-top: 15px; font-family: 'DejaVu Sans Mono', monospace; font-size: 11pt;">
            &nbsp;&nbsp;{greeting}
        </div>
        <div style="color: #666666; margin-top: 5px; font-family: 'DejaVu Sans Mono', monospace; font-size: 10pt;">
            &nbsp;&nbsp;{strs['banner_hint']}
        </div>
        <div style="color: #666666; font-family: 'DejaVu Sans Mono', monospace; font-size: 10pt;">
            &nbsp;&nbsp;{strs['banner_cmd']}
        </div>
        <br>
        """
        self.append_html(banner_html)



    
    def on_enter(self):
        """Handle user input / 사용자 입력 처리"""
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        # Clear input field / 입력 필드 초기화
        self.input_field.clear()

        # Handle slash commands / 슬래시 명령어 처리
        if user_input.startswith("/"):
            self.handle_command(user_input)
            return
            
        if self.is_streaming:
            return

        # Append user message to terminal / 사용자 메시지 터미널에 추가
            
        # Append user message to terminal / 사용자 메시지 터미널에 추가
        self.append_text(f"\nYOU: {user_input}\n", "#4ec9b0")
        
        # Add to history / 기록에 추가 (max 100 turns)
        self.conversation_history.append({"role": "user", "content": user_input})
        self.total_tokens += len(user_input) // 4
        if len(self.conversation_history) > 100:
            self.conversation_history.pop(0)
        
        # Start streaming / 스트리밍 시작
        self.is_streaming = True
        self.current_response = ""
        self.input_field.setEnabled(False)
        self.prompt_label.setStyleSheet("color: #555555; background: transparent;")
        
        # Show thinking indicator / 생각 중 인디케이터 표시
        self.append_text("\n")
        self.dot_count = 0
        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self.blink_dot)
        self.dot_timer.start(300)
        
        # Start API thread / API 스레드 시작
        thread = threading.Thread(target=self.api_call, args=(user_input,), daemon=True)
        thread.start()
    
    def blink_dot(self):
        """Blink the streaming dot indicator / 스트리밍 점 인디케이터 깜빡임"""
        if not self.is_streaming:
            return
        
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Remove previous dot if exists / 이전 점 제거
        if self.dot_count > 0:
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            cursor.removeSelectedText()
        
        # Toggle dot / 점 토글
        self.dot_count += 1
        if self.dot_count % 2 == 1:
            fmt = cursor.charFormat()
            fmt.setForeground(QColor("#ffffff"))
            cursor.setCharFormat(fmt)
            cursor.insertText("●")
        else:
            fmt = cursor.charFormat()
            fmt.setForeground(QColor("#1a1a1a"))
            cursor.setCharFormat(fmt)
            cursor.insertText("●")
        
        self.terminal.setTextCursor(cursor)
    
    def handle_command(self, cmd):
        """Handle slash commands / 슬래시 명령어 처리"""
        strs = UI_STRINGS[self.ui_lang]
        
        if cmd == "/sclear":
            # RESET BOTH: Memory and screen / 기억과 화면 모두 초기화
            self.conversation_history = []
            self.total_tokens = 0
            self.terminal.clear()
            self.show_banner()
            self.append_text("\n" + strs["msg_sclear"] + "\n", "#569cd6")
            self.update_context_bar()
        elif cmd == "/clear":
            # CLEAR SCREEN ONLY: Keep memory / 화면만 지움 (기억 유지)
            self.last_screen_html = self.terminal.toHtml() # Save for undo
            self.terminal.clear()
            self.append_text("\n" + strs["msg_clear"] + "\n", "#569cd6")
        elif cmd == "/draw":
            # RESTORE PREVIOUS SCREEN / 이전 화면 복구
            if self.last_screen_html:
                self.terminal.setHtml(self.last_screen_html)
                self.append_text("\n" + strs["msg_draw"] + "\n", "#569cd6")
            else:
                self.append_text("\n" + strs["msg_draw_fail"] + "\n", "#f44747")
        elif cmd == "/trans":
            self.toggle_lang()
            self.append_text("\n" + strs["msg_trans"] + "\n", "#569cd6")
        elif cmd == "/help":
            self.show_banner()
        elif cmd.startswith("/model"):
            parts = cmd.split(" ", 1)
            if len(parts) > 1:
                target_input = parts[1].strip().lower()
                
                # Check simplified names first / 간소화된 이름 먼저 확인
                group_map = {k.lower(): k for k in MODEL_GROUPS.keys()}
                if target_input in group_map:
                    group_name = group_map[target_input]
                    target_model = MODEL_GROUPS[group_name]
                    self.current_model = target_model
                    # Sync dropdown / 드롭다운 동기화
                    idx = self.model_selector.findText(group_name)
                    if idx >= 0:
                        self.model_selector.blockSignals(True)
                        self.model_selector.setCurrentIndex(idx)
                        self.model_selector.blockSignals(False)
                    self.append_text(f"\n[SYSTEM] Model switched to: {group_name} ({self.current_model})\n", "#569cd6")
                    self.append_text(f"[INFO] Switch will apply to the NEXT question / 다음 질문부터 적용됩니다.\n", "#aaaaaa")
                elif target_input in AVAILABLE_MODELS:
                    self.current_model = target_input
                    self.append_text(f"\n[SYSTEM] Model switched to: {self.current_model}\n", "#569cd6")
                    self.append_text(f"[INFO] Switch will apply to the NEXT question / 다음 질문부터 적용됩니다.\n", "#aaaaaa")
                else:
                    self.append_text(f"\n[SYSTEM] Unknown model. Available keywords: mistral, gpt, gemini\n", "#ff6a6a")
            else:
                self.append_text(f"\n[SYSTEM] Current model: {self.current_model}\n", "#aaaaaa")
                self.append_text(f"  Available: {', '.join(AVAILABLE_MODELS.keys())}\n", "#aaaaaa")
                self.append_text("  Usage: /model <mistral|gpt|gemini>\n", "#aaaaaa")
        elif cmd == "/exit":
            self.close()
        else:
            self.append_text(f"\n[SYSTEM] Unknown command: {cmd}\n", "#ff6a6a")
    
    def api_call(self, user_input):
        """Make API call in background thread / 백그라운드 스레드에서 API 호출"""
        # Capture model and provider at START to handle mid-request switches / 시작 시 모델과 제공자를 캡처하여 중간 전환 처리
        active_model = self.current_model
        provider = AVAILABLE_MODELS.get(active_model, "mistral")
        
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(self.conversation_history)
            
            if provider == "mistral":
                payload = {
                    "model": active_model,
                    "messages": messages,
                    "stream": True
                }
                headers = {"Content-Type": "application/json"}
                print(f"[DEBUG] Sending Mistral request to {MISTRAL_API_URL}")
                print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
                response = requests.post(
                    MISTRAL_API_URL, json=payload, headers=headers,
                    stream=True, timeout=60
                )
                print(f"[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response headers: {dict(response.headers)}")
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode("utf-8")
                        print(f"[DEBUG] Received line: {line[:200]}")
                        
                        # Handle both SSE format ("data: {...}") and direct JSON
                        if line.startswith("data: "):
                            data = line[6:]  # SSE format
                        elif line.startswith("{"):  # Direct JSON response
                            data = line
                        else:
                            continue  # Skip non-data lines
                        
                        if data == "[DONE]":
                            print("[DEBUG] Received [DONE] marker")
                            break
                            
                        try:
                            parsed = json.loads(data)
                            print(f"[DEBUG] Parsed JSON: {json.dumps(parsed, indent=2)[:300]}")
                            
                            # Extract from payload wrapper for juni_relay
                            payload_data = parsed.get("payload", parsed)
                            choices = payload_data.get("choices", [])
                            
                            if choices:
                                # Try streaming format first (delta.content)
                                content = choices[0].get("delta", {}).get("content", "")
                                # Fallback to complete response format (message.content)
                                if not content:
                                    content = choices[0].get("message", {}).get("content", "")
                                
                                if content:
                                    print(f"[DEBUG] Emitting content: {content[:50]}")
                                    self.signals.chunk_received.emit(content)
                            else:
                                print(f"[DEBUG] No choices found in: {json.dumps(payload_data, indent=2)[:200]}")
                        except Exception as e:
                            print(f"[DEBUG] Mistral parse error: {e}, data: {data[:100]}")
                            import traceback
                            traceback.print_exc()
                            pass
                            
            elif provider == "google":
                # Google Gemini Relay Implementation / Google Gemini 중계 구현
                google_messages = []
                for msg in messages:
                    role = "user" if msg["role"] in ["user", "system"] else "model"
                    google_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
                
                payload = {"contents": google_messages}
                headers = {"Content-Type": "application/json"}
                
                response = requests.post(
                    GEMINI_API_URL, json=payload, headers=headers,
                    stream=True, timeout=60
                )
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode("utf-8")
                        try:
                            if line.startswith("data: "): line = line[6:]
                            parsed = json.loads(line)
                            # Extract from payload wrapper for juni_relay (if present)
                            payload = parsed.get("payload", parsed)
                            candidates = payload.get("candidates", [])
                            if candidates:
                                content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                if content: self.signals.chunk_received.emit(content)
                        except Exception as e:
                            print(f"[DEBUG] Gemini parse error: {e}, line: {line[:100]}")
                            pass

            self.signals.stream_finished.emit()
            
        except Exception as e:
            self.signals.stream_error.emit(str(e))
    
    def on_chunk_received(self, chunk):
        """Handle received chunk / 수신된 청크 처리"""
        # Stop dot timer on first chunk / 첫 번째 청크에서 점 타이머 정지
        if self.dot_timer and self.dot_timer.isActive():
            self.dot_timer.stop()
            # Remove the dot / 점 제거
            cursor = self.terminal.textCursor()
            cursor.movePosition(QTextCursor.End)
            if self.dot_count > 0:
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
                cursor.removeSelectedText()
            self.terminal.setTextCursor(cursor)
            self.dot_count = 0
        
        self.current_response += chunk
        # Stream raw text during streaming (markdown rendered on finish)
        # 스트리밍 중에는 원시 텍스트 출력 (완료 시 마크다운 렌더링)
        color = THEMES[self.current_theme]['fg']
        self.append_text(chunk, color)
    
    def on_stream_finished(self):
        """Handle stream completion / 스트림 완료 처리"""
        self.is_streaming = False
        
        if self.dot_timer:
            self.dot_timer.stop()
            # Clean up any remaining dot / 남은 점 정리
            cursor = self.terminal.textCursor()
            cursor.movePosition(QTextCursor.End)
            if self.dot_count > 0:
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
                cursor.removeSelectedText()
            self.terminal.setTextCursor(cursor)
        
        # Re-render with markdown / 마크다운으로 재렌더링
        if self.current_response:
            # Find and remove the raw streamed text, replace with rendered markdown
            # 원시 스트리밍 텍스트를 찾아 제거 후 렌더링된 마크다운으로 교체
            cursor = self.terminal.textCursor()
            cursor.movePosition(QTextCursor.End)
            
            # Move back by the length of the raw response to select it
            # 원시 응답 길이만큼 뒤로 이동하여 선택
            raw_len = len(self.current_response)
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, raw_len)
            cursor.removeSelectedText()
            
            # Insert rendered markdown HTML / 렌더링된 마크다운 HTML 삽입
            rendered = markdown_to_html(self.current_response, self.current_theme)
            cursor.insertHtml(rendered)
            
            self.terminal.setTextCursor(cursor)
            self.terminal.ensureCursorVisible()
        
        self.append_text("\n\n", "#d4d4d4")
        
        # Add to history / 기록에 추가
        if self.current_response and len(self.conversation_history) < 100:
            self.conversation_history.append({"role": "assistant", "content": self.current_response})
            self.total_tokens += len(self.current_response) // 4
        
        self.update_context_bar()
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self.prompt_label.setStyleSheet("color: #6aff6a; background: transparent;")
    
    def on_stream_error(self, error):
        """Handle stream error / 스트림 에러 처리"""
        self.is_streaming = False
        
        if self.dot_timer:
            self.dot_timer.stop()
        
        self.append_text(f"\n  [ERROR] {error}\n\n", "#ff6a6a")
        
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self.prompt_label.setStyleSheet("color: #6aff6a; background: transparent;")
    
    def update_context_bar(self):
        """Update context usage bar / 컨텍스트 사용량 바 업데이트"""
        pct = (self.total_tokens * 100) // MAX_TOKENS if MAX_TOKENS > 0 else 0
        self.context_bar.setText(f"Context: {self.total_tokens}/{MAX_TOKENS} tokens ({pct}%)")


def main():
    """Main entry point / 메인 진입점"""
    app = QApplication(sys.argv)
    
    # Set dark palette / 다크 팔레트 설정
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1a1a1a"))
    palette.setColor(QPalette.WindowText, QColor("#d4d4d4"))
    palette.setColor(QPalette.Base, QColor("#1a1a1a"))
    palette.setColor(QPalette.Text, QColor("#d4d4d4"))
    app.setPalette(palette)
    
    window = StudyAITerminal()
    
    # Debug IM status / IM 상태 디버그
    im = app.inputMethod()
    print(f"[IM DEBUG] Visible: {im.isVisible()}")
    print(f"[IM DEBUG] Locale: {im.locale().name()}")
    print(f"[IM DEBUG] QT_IM_MODULE: {os.environ.get('QT_IM_MODULE')}")
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

