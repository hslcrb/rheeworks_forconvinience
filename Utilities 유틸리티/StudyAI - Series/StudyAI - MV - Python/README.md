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

## 🌐 API Relay Guide / API 릴레이 가이드
본 프로젝트는 JUNI AI 릴레이 API를 사용하여 AI 모델과 통신합니다. 자세한 사용법은 다음 가이드를 참조하십시오:  
This project uses the JUNI AI Relay API for AI communication. See the full guide for details:  
👉 **[JUNI AI Relay API Guide](../JUNI_AI_RELAY_GUIDE.md)**

## 🚀 실행 방법 / How to Run

가장 간단한 실행 방법은 제공된 쉘 스크립트를 사용하는 것입니다:
The simplest way to run is by using the provided shell script:

```bash
chmod +x run_gui.sh
./run_gui.sh
```

또는 수동으로 가상환경을 설정하여 실행할 수 있습니다:
Or you can manually setup the virtual environment:

```bash
# 가상환경 생성 및 활성화 / Create and activate venv
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
