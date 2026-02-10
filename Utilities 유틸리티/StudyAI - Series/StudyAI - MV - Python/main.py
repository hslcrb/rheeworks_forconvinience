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
    QTextEdit, QLineEdit, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer
from PySide6.QtGui import QFont, QTextCursor, QColor, QPalette, QKeyEvent

# API Configuration / API 설정
MISTRAL_API_KEY = "OBfwuYKEEUFvjh5bLt18XOcVIpTYFHVQ"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL_NAME = "mistral-small-latest"
MAX_TOKENS = 32000  # Mistral Small context limit / Mistral Small 컨텍스트 제한

# Random greeting phrases / 랜덤 인사말 문구
GREETINGS = [
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


class StreamSignals(QObject):
    """Signals for thread-safe streaming updates / 스레드 안전 스트리밍 업데이트 시그널"""
    chunk_received = Signal(str)
    stream_finished = Signal()
    stream_error = Signal(str)


def markdown_to_html(text):
    """
    마크다운을 HTML로 변환 (터미널 스타일) / Convert markdown to HTML (terminal style).
    Supports: **bold**, *italic*, `inline code`, ```code blocks```, ### headers, - bullet lists.
    """
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
                    f'<div style="background-color:#2a2a2a; padding:6px 10px; margin:4px 0; '
                    f'border-left:3px solid #6aff6a; font-family:Monospace;">'
                    f'<pre style="margin:0; color:#c8c8c8;">{code_text}</pre></div>'
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
        header_match = re.match(r'^(#{1,3})\s+(.*)', line)
        if header_match:
            level = len(header_match.group(1))
            header_text = header_match.group(2)
            # Apply inline formatting to header text / 헤더 텍스트에 인라인 서식 적용
            header_text = _apply_inline_md(header_text)
            if level == 1:
                html_parts.append(f'<p style="color:#ffffff; font-weight:bold; font-size:15px; margin:6px 0;">{header_text}</p>')
            elif level == 2:
                html_parts.append(f'<p style="color:#e0e0e0; font-weight:bold; font-size:14px; margin:4px 0;">{header_text}</p>')
            else:
                html_parts.append(f'<p style="color:#cccccc; font-weight:bold; margin:3px 0;">{header_text}</p>')
            continue
        
        # Bullet lists / 불릿 목록
        bullet_match = re.match(r'^(\s*)[-*]\s+(.*)', line)
        if bullet_match:
            indent = len(bullet_match.group(1))
            item_text = _apply_inline_md(bullet_match.group(2))
            pad = "&nbsp;" * (indent + 2)
            html_parts.append(f'<p style="margin:1px 0;">{pad}• {item_text}</p>')
            continue
        
        # Numbered lists / 숫자 목록
        num_match = re.match(r'^(\s*)\d+[.)]\s+(.*)', line)
        if num_match:
            indent = len(num_match.group(1))
            item_text = _apply_inline_md(num_match.group(2))
            pad = "&nbsp;" * (indent + 2)
            html_parts.append(f'<p style="margin:1px 0;">{pad}▸ {item_text}</p>')
            continue
        
        # Regular text with inline formatting / 인라인 서식이 있는 일반 텍스트
        if line.strip():
            html_parts.append(f'<p style="margin:1px 0;">{_apply_inline_md(line)}</p>')
        else:
            html_parts.append('<p style="margin:2px 0;">&nbsp;</p>')
    
    # Close unclosed code block / 닫히지 않은 코드 블록 닫기
    if in_code_block and code_block_content:
        code_text = "\n".join(code_block_content)
        code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_parts.append(
            f'<div style="background-color:#2a2a2a; padding:6px 10px; margin:4px 0; '
            f'border-left:3px solid #6aff6a; font-family:Monospace;">'
            f'<pre style="margin:0; color:#c8c8c8;">{code_text}</pre></div>'
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
        ('ㅗ', 'ㅏ'): 'ㅘ', ('ㅗ', 'ㅐ'): 'ㅙ', ('ㅗ', 'ㅣ'): 'ㅚ',
        ('ㅜ', 'ㅓ'): 'ㅝ', ('ㅜ', 'ㅔ'): 'ㅞ', ('ㅜ', 'ㅣ'): 'ㅟ',
        ('ㅡ', 'ㅣ'): 'ㅢ'
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
        self.cho = -1
        self.jung = -1
        self.jong = -1
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
        # Mapping from QWERTY or direct Jamo input
        # QWERTY 또는 직접 입력된 자모 매핑
        if key in self.MAP:
            jamo = self.MAP[key]
        elif key in self.CHO or key in self.JUNG or key in self.JONG:
            jamo = key
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
            
            # If complex jong, break it / 복합 종성 분해 (ㄺ -> ㄹ + ㄱ)
            # Find if current jong is complex / 현재 종성이 복합 종성인지 확인
            comp_found = False
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
            "/sclear", "/draw"
        ]
        self.completer = QCompleter(self.commands, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self.completer)

    def keyPressEvent(self, event: QKeyEvent):
        # Toggle Hangul mode / 한영 전환
        if event.key() in (Qt.Key_AltGr, 108, 65513, Qt.Key_Hangul) or \
           (event.key() == Qt.Key_Alt and event.modifiers() & Qt.AltModifier):
            self.commit_composition()
            self.is_hangul = not self.is_hangul
            mode_str = "KO" if self.is_hangul else "EN"
            print(f"[MODE] Switched to {mode_str}")
            # Update window title to show mode
            window = self.window()
            if window:
                title = window.windowTitle().split(" [")[0]
                window.setWindowTitle(f"{title} [{mode_str}]")
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


def _apply_inline_md(text):
    """
    인라인 마크다운 서식 적용 / Apply inline markdown formatting.
    Supports: **bold**, *italic*, `code`
    """
    import re
    # Inline code / 인라인 코드: `text`
    text = re.sub(
        r'`([^`]+)`',
        r'<span style="background-color:#2a2a2a; color:#9cdcfe; padding:1px 4px;">\1</span>',
        text
    )
    # Bold / 볼드: **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b style="color:#ffffff;">\1</b>', text)
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
        self.last_screen_html = "" # For /cancel_clear restore
        
        self.signals = StreamSignals()
        self.signals.chunk_received.connect(self.on_chunk_received)
        self.signals.stream_finished.connect(self.on_stream_finished)
        self.signals.stream_error.connect(self.on_stream_error)
        
        self.setup_ui()
        self.show_banner()
    
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
        
        # Terminal output / 터미널 출력
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Monospace", 12))
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #d4d4d4;
                border: none;
                padding: 12px;
                selection-background-color: #3a3a3a;
            }
        """)
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
        self.input_field.setFont(QFont("Monospace", 12))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: none;
                padding: 4px;
            }
        """)
        self.input_field.returnPressed.connect(self.on_enter)
        input_layout.addWidget(self.input_field)
        
        input_container = QWidget()
        input_container.setLayout(input_layout)
        input_container.setStyleSheet("background-color: #1a1a1a;")
        layout.addWidget(input_container)
        
        # Context bar / 컨텍스트 바
        self.context_bar = QLabel("Context: 0/32000 tokens (0%)")
        self.context_bar.setFont(QFont("Monospace", 9))
        self.context_bar.setStyleSheet("""
            QLabel {
                color: #666666;
                background-color: #111111;
                padding: 3px 12px;
                border-top: 1px solid #333333;
            }
        """)
        self.context_bar.setAlignment(Qt.AlignRight)
        layout.addWidget(self.context_bar)
        
        # Window styling / 윈도우 스타일링
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
        """)
        
        # Focus input / 입력 포커스
        self.input_field.setFocus()
    
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
        """Show startup banner / 시작 배너 표시"""
        greeting = random.choice(GREETINGS)
        
        # Fixed-width banner with proper alignment / 고정 너비 배너, 올바른 정렬
        BOX_W = 44  # inner width / 내부 너비
        
        title = "StudyAI Terminal"
        subtitle = "Python Edition • Mistral AI"
        
        # Center-pad strings inside the box / 박스 안에 문자열 가운데 정렬
        title_pad = (BOX_W - len(title)) // 2
        title_r = BOX_W - len(title) - title_pad
        sub_pad = (BOX_W - len(subtitle)) // 2
        sub_r = BOX_W - len(subtitle) - sub_pad
        
        self.append_text("╔" + "═" * BOX_W + "╗\n", "#6aff6a")
        self.append_text("║" + " " * title_pad, "#6aff6a")
        self.append_text(title, "#ffffff")
        self.append_text(" " * title_r + "║\n", "#6aff6a")
        self.append_text("║" + " " * sub_pad, "#6aff6a")
        self.append_text(subtitle, "#888888")
        self.append_text(" " * sub_r + "║\n", "#6aff6a")
        self.append_text("╚" + "═" * BOX_W + "╝\n", "#6aff6a")
        self.append_text(f"\n  {greeting}\n", "#aaaaaa")
        self.append_text("  Type your question and press Enter.\n", "#666666")
        self.append_text("  Commands: /clear, /sclear, /draw, /help, /exit\n\n", "#666666")
    
    def on_enter(self):
        """Handle user input / 사용자 입력 처리"""
        if self.is_streaming:
            return

        user_input = self.input_field.text().strip()
        if not user_input:
            return

        # Clear input field / 입력 필드 초기화
        self.input_field.clear()

        # Handle slash commands / 슬래시 명령어 처리
        if user_input == "/sclear":
            # RESET BOTH: Memory and screen / 기억과 화면 모두 초기화
            self.conversation_history = []
            self.total_tokens = 0
            self.terminal.clear()
            self.show_banner()
            self.append_text("\n[SYSTEM] Session and memory cleared. / 세션 및 AI 기억이 초기화되었습니다.\n", "#569cd6")
            return
        
        elif user_input == "/clear":
            # CLEAR SCREEN ONLY: Keep memory / 화면만 지움 (기억 유지)
            self.last_screen_html = self.terminal.toHtml() # Save for undo
            self.terminal.clear()
            self.append_text("\n[SYSTEM] Screen cleared. (AI still remembers) / 화면이 지워졌습니다. (기억 유지됨)\n", "#569cd6")
            return
        
        elif user_input == "/draw":
            # RESTORE PREVIOUS SCREEN / 이전 화면 복구
            if self.last_screen_html:
                self.terminal.setHtml(self.last_screen_html)
                self.append_text("\n[SYSTEM] Screen restored. / 화면이 복구되었습니다.\n", "#569cd6")
            else:
                self.append_text("\n[SYSTEM] Nothing to draw. / 복구할 화면이 없습니다.\n", "#f44747")
            return

        elif user_input == "/help":
            self.show_banner()
            return
        
        elif user_input == "/exit":
            self.close()
            return

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
        if cmd == "/clear":
            self.terminal.clear()
            self.conversation_history.clear()
            self.total_tokens = 0
            self.update_context_bar()
            self.show_banner()
        elif cmd == "/help":
            self.append_text("\n  === Commands / 명령어 ===\n", "#6aff6a")
            self.append_text("  /clear   - Clear screen & history / 화면 및 기록 초기화\n", "#aaaaaa")
            self.append_text("  /help    - Show this help / 도움말 표시\n", "#aaaaaa")
            self.append_text("  /exit    - Exit application / 종료\n\n", "#aaaaaa")
        elif cmd == "/exit":
            QApplication.quit()
        else:
            self.append_text(f"  Unknown command: {cmd}\n\n", "#ff6a6a")
    
    def api_call(self, user_input):
        """Make API call in background thread / 백그라운드 스레드에서 API 호출"""
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(self.conversation_history)
            
            payload = {
                "model": MODEL_NAME,
                "messages": messages,
                "stream": True
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}"
            }
            
            response = requests.post(
                MISTRAL_API_URL,
                json=payload,
                headers=headers,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            parsed = json.loads(data)
                            choices = parsed.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    self.signals.chunk_received.emit(content)
                        except json.JSONDecodeError:
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
        self.append_text(chunk, "#d4d4d4")
    
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
            rendered = markdown_to_html(self.current_response)
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

