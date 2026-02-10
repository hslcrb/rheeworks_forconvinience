# StudyAI - MV - Python (터미널 스타일 GUI / Terminal-Style GUI)

PySide6 기반 터미널 스타일 AI 채팅 애플리케이션입니다.
A PySide6-based terminal-style AI chat application.

## ✨ 주요 기능 / Key Features
- **터미널 스타일 GUI**: CLI 경험을 GUI 창에서 / Terminal-style CLI experience in a GUI window
- **실시간 스트리밍**: Mistral AI API 실시간 응답 / Real-time streaming from Mistral AI API
- **대화 메모리**: 세션 내 대화 기록 유지 / Conversation history within session
- **컨텍스트 추적**: 32k 토큰 사용량 표시 / 32k token usage tracking
- **슬래시 명령어**: /clear, /help, /exit / Slash commands support
- **깜빡이는 인디케이터**: 응답 생성 중 점 깜빡임 / Blinking dot during response generation

## 🚀 실행 방법 / How to Run

```bash
# 가상환경 생성 / Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 의존성 설치 / Install dependencies
pip install -r requirements.txt

# 실행 / Run
python main.py
```

## 📝 명령어 / Commands
| 명령어   | 설명 / Description                                |
| -------- | ------------------------------------------------- |
| `/clear` | 화면 및 대화 기록 초기화 / Clear screen & history |
| `/help`  | 도움말 표시 / Show help                           |
| `/exit`  | 종료 / Exit                                       |

## 📄 라이선스 / License
Apache-2.0

---
**Rheehose (Rhee Creative) 2008-2026**
