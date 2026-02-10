"""
StudyAI - MV - Python (Terminal-Style GUI)
터미널 스타일 GUI AI 채팅 애플리케이션 / Terminal-Style GUI AI Chat Application
PySide6 + Mistral AI API

Rheehose (Rhee Creative) 2008-2026
Licensed under Apache-2.0
"""

import sys
import json
import random
import threading
import requests
from datetime import datetime
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


class TerminalWidget(QTextEdit):
    """Terminal-style text widget / 터미널 스타일 텍스트 위젯"""
    
    command_entered = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.prompt_prefix = "studyai> "
        self.input_mode = False
        self.current_input = ""
        
    def append_colored(self, text, color="#d4d4d4"):
        """Append colored text / 색상 텍스트 추가"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        fmt = cursor.charFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


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
        self.input_field = QLineEdit()
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
        """Append text with color / 색상 텍스트 추가"""
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        fmt = cursor.charFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        
        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()
    
    def show_banner(self):
        """Show startup banner / 시작 배너 표시"""
        greeting = random.choice(GREETINGS)
        
        self.append_text("╔══════════════════════════════════════════╗\n", "#6aff6a")
        self.append_text("║          ", "#6aff6a")
        self.append_text("StudyAI Terminal", "#ffffff")
        self.append_text("              ║\n", "#6aff6a")
        self.append_text("║     ", "#6aff6a")
        self.append_text("Python Edition • Mistral AI", "#888888")
        self.append_text("        ║\n", "#6aff6a")
        self.append_text("╚══════════════════════════════════════════╝\n", "#6aff6a")
        self.append_text(f"\n  {greeting}\n", "#aaaaaa")
        self.append_text("  Type your question and press Enter.\n", "#666666")
        self.append_text("  Commands: /clear, /help, /exit\n\n", "#666666")
    
    def on_enter(self):
        """Handle user input / 사용자 입력 처리"""
        text = self.input_field.text().strip()
        if not text or self.is_streaming:
            return
        
        self.input_field.clear()
        
        # Handle commands / 명령어 처리
        if text.startswith("/"):
            self.handle_command(text)
            return
        
        # Show user input / 사용자 입력 표시
        self.append_text("studyai> ", "#6aff6a")
        self.append_text(f"{text}\n", "#ffffff")
        
        # Add to history / 기록에 추가
        if len(self.conversation_history) < 100:
            self.conversation_history.append({"role": "user", "content": text})
            self.total_tokens += len(text) // 4
        
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
        thread = threading.Thread(target=self.api_call, args=(text,), daemon=True)
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
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
