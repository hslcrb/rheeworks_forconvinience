# RheeWorks ForConvinience - Agent Guidelines
# RheeWorks ForConvinience - 에이전트 지침

## 프로젝트 정보 / Project Information

- **프로젝트명 / Project Name**: RheeWorks ForConvinience
- **타입 / Type**: Monorepo (Python, C)
- **저작권 / Copyright**: Rheehose (Rhee Creative) 2008-2026
- **라이선스 / License**: Apache 2.0
- **웹사이트 / Website**: https://rheehose.com

## 구조 개요 / Structure Overview

이 프로젝트는 여러 편의성 도구를 포함하는 모노레포입니다.  
This project is a monorepo containing multiple convenience tools.

### 서브 프로젝트 / Sub-Projects

1. **Typer-타이퍼 Series** (Path: `Utilities 유틸리티/Typer-타이퍼 Series`)
   - 베이직 버전-Basic Version: 기본 가짜 타이핑 도구 (Premium UI/CLI)
   - 포모도로 버전-Pomodoro Version: 포모도로 타이머 + 숨겨진 타이핑 도구 (Premium UI/CLI)

2. **Rucia-루시아 Series** (Path: `Utilities 유틸리티/Rucia-루시아 Series`)
   - Pris-프리스: 공부/코딩 시간 통계 대시보드 (Premium UI/CLI)
   - Lavendar-라벤다르: 실전성 최강 실습실 자동 백업 도구 (Premium UI/CLI)
   - Frytesty-프라이테스티: 알고리즘 문제풀이 로컬 테스트기 (Premium UI/CLI)

3. **Automaker-오토메이커 Series** (Path: `Utilities 유틸리티/Automaker-오토메이커 Series`)
   - 클리커-Clicker: 프리미엄 오토 클릭커 도구 (Premium UI/CLI)
   - 텍스트생성기-Text Generator: 프리미엄 더미 텍스트 생성 도구 (Premium UI/CLI)
   - 프로젝트 템플릿 생성-Generate Project Templates: 다국어 스캐폴딩 도구 (Premium UI/CLI)

4. **StudyAI Series** (Path: `Utilities 유틸리티/StudyAI - Series`)
   - StudyAI - MV: AI 채팅 앱 C/GTK 버전 (GUI, Grayscale Theme)
   - StudyAI - MV - Python: AI 채팅 앱 Python/PySide6 터미널 스타일 GUI 버전 (Terminal-Style GUI)

## 개발 지침 / Development Guidelines

### 가상환경 관리 / Virtual Environment Management

각 서브 프로젝트는 독립적인 `venv`를 가집니다:  
Each sub-project has its own `venv`:

```bash
cd "Utilities 유틸리티/Typer-타이퍼 Series/베이직 버전-Basic Version"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run_gui.sh # or ./run_cli.sh
```

### 파일 보존 정책 / File Preservation Policy

- 파일 삭제 금지 / No file deletions
- 불필요한 코드는 주석 처리 / Comment out unnecessary code
- 모든 수정 전 원본을 `recycle_trash/`에 백업 / Backup originals to `recycle_trash/` before modifications

### CI/CD 파이프라인 / CI/CD Pipeline

GitHub Actions를 통해 다음을 자동화합니다:  
Automated via GitHub Actions:

- 3대 OS별 바이너리 빌드 (PyInstaller --onedir)
- Docker 이미지 빌드 및 GHCR 배포
- 10 커밋마다 자동 버전 업
- GitHub Releases에 자동 업로드

### 커밋 규칙 / Commit Rules

- **커밋 메시지**: `한글메시지 / English Message`
- **예시 / Example**: `문서 업데이트 / Update documentation`
- **빈도 / Frequency**: 최대한 자주 / As frequent as possible

## 에이전트 작업 로그 / Agent Work Log

모든 에이전트 활동은 `agents_brain/docs/session_brain.md`에 기록됩니다.  
All agent activities are logged in `agents_brain/docs/session_brain.md`.

---

**Rheehose (Rhee Creative) 2008-2026**
