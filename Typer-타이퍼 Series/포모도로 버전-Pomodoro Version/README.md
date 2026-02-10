# Typer - Pomodoro Version / 타이퍼 - 포모도로 버전

**집중 타이머 프로 + 숨겨진 타이핑 도구 / Focus Timer Pro + Hidden Typing Tool**

Rheehose (Rhee Creative) 2008-2026

## 개요 / Overview

겉으로는 일반적인 포모도로 타이머로 보이지만, "🚫 누르지 마세요" 버튼을 누르면 비밀 콘솔이 나타나 베이직 버전과 동일한 가짜 타이핑 기능을 사용할 수 있습니다!  
Appears as a normal Pomodoro timer on the surface, but pressing the "🚫 Don't Press" button reveals a secret console with the same fake typing functionality as the basic version!

## 주요 기능 / Key Features

### 메인 화면 / Main Screen
- 🍅 **포모도로 타이머 / Pomodoro Timer**: 25분 작업 타이머
- 🕐 **실시간 시계 / Real-time Clock**: 현재 타임존 기반 시계
- ▶️ **START/STOP 버튼 / START/STOP Buttons**: 타이머 제어

### 비밀 콘솔 / Secret Console
- 📝 **가짜 타이핑 엔진 / Fake Typing Engine**: 베이직 버전과 동일한 기능
- 🕵️ **숨겨진 UI / Hidden UI**: "🚫 누르지 마세요" 버튼으로 접근
- 🔴 **녹화 상태 표시 / Recording Status**: 실시간 상태 확인
- ← **돌아가기 / Back Button**: 메인 화면으로 복귀

## 설치 / Installation

### 1. 가상환경 생성 / Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 종속성 설치 / Install Dependencies

```bash
pip install -r requirements.txt
```

## 사용법 / Usage

### 메인 타이머 사용 / Using the Main Timer

1. **프로그램 실행 / Run the program**: `python main.py`
2. **START** 버튼 클릭 → 25분 타이머 시작
3. **STOP** 버튼 클릭 → 타이머 중지

### 비밀 타이핑 도구 사용 / Using the Secret Typing Tool

1. **"🚫 누르지 마세요"** 버튼 클릭 → 비밀 콘솔 진입
2. **원천텍스트 선택** → 복사할 텍스트 파일 선택
3. **대상텍스트 선택** → 비어있는 새 파일 선택
4. **Start Fake Typing** 클릭
5. 🔴 **REC** 상태 확인 후, 아무 키나 입력하면 자동 복사!
6. **Stop** 버튼으로 중지
7. **← 돌아가기** 버튼으로 메인 화면 복귀

## 종속성 / Dependencies

- `pynput==1.7.6`: 키보드 입력 감지 / Keyboard input detection
- `tzlocal==5.2`: 타임존 감지 / Timezone detection
- `tkinter`: GUI 프레임워크 (Python 기본 포함) / GUI framework (included in Python)

## 특징 / Special Features

### 🎭 위장 모드 / Camouflage Mode
겉으로는 평범한 포모도로 타이머처럼 보여 집중 타이머를 사용하는 것처럼 보이면서, 실제로는 가짜 타이핑 도구를 몰래 사용할 수 있습니다!  
Looks like a normal Pomodoro timer on the outside, so you can secretly use the fake typing tool while appearing to use a focus timer!

### 🕐 실시간 타임존 시계 / Real-time Timezone Clock
현재 시스템 타임존을 자동으로 감지하여 정확한 시간을 표시합니다.  
Automatically detects your system timezone and displays the accurate time.

## 라이선스 / License

Apache License 2.0

---

**Rheehose (Rhee Creative) 2008-2026**  
Website: https://rheehose.com
