# RheeWorks ForConvinience

**편의성 도구 모음집 / Collection of Convenience Tools**

Rheehose (Rhee Creative) 2008-2026

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 개요 / Overview

이 리포지토리는 일상적인 작업을 더 편리하게 만드는 여러 유틸리티 도구를 포함하는 모노레포입니다.  
This repository is a monorepo containing multiple utility tools designed to make everyday tasks more convenient.

## 프로젝트 구조 / Project Structure

```
rheeworks_forconvinience/
├── Typer-타이퍼 Series/          # 자동 타이핑 도구 / Auto-typing tools
│   ├── 베이직 버전-Basic Version/
│   └── 포모도로 버전-Pomodoro Version/
├── Automaker-오토메이커 Series/  # 자동화 도구 / Automation tools
├── .github/workflows/            # CI/CD 파이프라인 / CI/CD pipeline
├── recycle_trash/                # 파일 보존 / File preservation
└── agents_brain/                 # 에이전트 문서 / Agent documentation
```

---

## Typer Series / 타이퍼 시리즈

### 🔹 베이직 버전 (Basic Version)

**가짜 타이핑 복사 도구 / Fake Typing Copier**

원본 텍스트 파일을 읽어 키보드 입력을 감지할 때마다 자동으로 대상 파일에 랜덤한 길이(1-5글자)로 복사합니다.  
Reads a source text file and automatically copies random chunks (1-5 characters) to a target file whenever keyboard input is detected.

#### 주요 기능 / Key Features
- 📝 원천 텍스트 선택 / Select source text
- 🎯 대상 텍스트 선택 (빈 파일 필수) / Select target text (must be empty)
- ⌨️ 키보드 입력 감지 시 자동 복사 / Auto-copy on keyboard input
- 🎲 랜덤 길이 복사 (1-5글자) / Random chunk size (1-5 chars)
- 🔴 실시간 녹화 상태 표시 / Real-time recording status

#### 설치 및 실행 / Installation & Usage
```bash
cd "Typer-타이퍼 Series/베이직 버전-Basic Version"
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### 종속성 / Dependencies
- `tkinter`: GUI 프레임워크 / GUI framework
- `pynput`: 키보드 입력 감지 / Keyboard input detection

---

### 🔹 포모도로 버전 (Pomodoro Version)

**집중 타이머 프로 + 숨겨진 타이핑 도구 / Focus Timer Pro + Hidden Typing Tool**

겉으로는 일반적인 포모도로 타이머처럼 보이지만, 숨겨진 "비밀 방"에는 베이직 버전과 동일한 가짜 타이핑 기능이 숨어있습니다.  
Appears as a normal Pomodoro timer on the surface, but contains a hidden "secret room" with the same fake typing functionality as the basic version.

#### 주요 기능 / Key Features
- 🍅 포모도로 타이머 (25분 기본) / Pomodoro timer (25 min default)
- 🕐 실시간 타임존 시계 / Real-time timezone clock
- 🚫 "누르지 마세요" 버튼 → 비밀 콘솔 / "Don't Press" button → Secret console
- 🕵️ 숨겨진 가짜 타이핑 엔진 / Hidden fake typing engine
- 🔴 녹화 상태 표시 / Recording status indicator

#### 설치 및 실행 / Installation & Usage
```bash
cd "Typer-타이퍼 Series/포모도로 버전-Pomodoro Version"
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### 종속성 / Dependencies
- `tkinter`: GUI 프레임워크 / GUI framework
- `pynput`: 키보드 입력 감지 / Keyboard input detection
- `tzlocal`: 타임존 감지 / Timezone detection

---

## Automaker Series / 오토메이커 시리즈

*Coming soon / 개발 예정*

---

## 라이선스 / License

Apache License 2.0 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.  
Apache License 2.0 - See the [LICENSE](LICENSE) file for details.

## 저작권 / Copyright

© Rheehose (Rhee Creative) 2008-2026  
Website: https://rheehose.com

## 기여 / Contributing

이슈 및 풀 리퀘스트는 언제나 환영합니다!  
Issues and pull requests are always welcome!

---

**Made with ❤️ by Rheehose (Rhee Creative)**
