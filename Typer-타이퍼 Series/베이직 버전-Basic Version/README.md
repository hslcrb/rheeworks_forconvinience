# Typer - Basic Version / 타이퍼 - 베이직 버전

**가짜 타이핑 복사 도구 / Fake Typing Copier**

Rheehose (Rhee Creative) 2008-2026

## 개요 / Overview

이 프로그램은 원본 텍스트 파일에서 내용을 읽어 키보드 입력을 감지할 때마다 자동으로 대상 파일에 랜덤한 길이(1-5글자)로 복사하는 도구입니다.  
This program reads content from a source text file and automatically copies random chunks (1-5 characters) to a target file whenever keyboard input is detected.

## 주요 기능 / Key Features

- 📝 **원천 텍스트 선택 / Source Text Selection**: 복사할 원본 파일 선택
- 🎯 **대상 텍스트 선택 / Target Text Selection**: 복사될 빈 파일 선택 (반드시 비어있어야 함)
- ⌨️ **키보드 입력 감지 / Keyboard Input Detection**: 키 입력 시 자동으로 텍스트 복사
- 🎲 **랜덤 길이 복사 / Random Chunk Size**: 매번 1-5글자를 랜덤하게 복사
- 🔴 **녹화 상태 표시 / Recording Status**: 실시간으로 녹화 상태 확인

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

### 1. 프로그램 실행 / Run the Program

```bash
python main.py
```

### 2. 파일 선택 / Select Files

1. **원천텍스트 선택** 버튼 클릭 → 복사할 텍스트 파일 선택
2. **대상텍스트 선택** 버튼 클릭 → 비어있는 새 파일 선택 (중요: 반드시 빈 파일이어야 함!)

### 3. 녹화 시작 / Start Recording

- **START** 버튼 클릭
- 🔴 **REC** 상태 표시 확인
- 이제 아무 키나 입력하면 자동으로 텍스트가 복사됩니다!

### 4. 녹화 중지 / Stop Recording

- **STOP** 버튼 클릭

## 종속성 / Dependencies

- `pynput==1.7.6`: 키보드 입력 감지 / Keyboard input detection
- `tkinter`: GUI 프레임워크 (Python 기본 포함) / GUI framework (included in Python)

## 라이선스 / License

Apache License 2.0

---

**Rheehose (Rhee Creative) 2008-2026**  
Website: https://rheehose.com
