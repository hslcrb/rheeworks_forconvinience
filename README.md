# RheeWorks ForConvinience

**RheeWorks ForConvinience**는 개인 일상 편의를 위한 도구들을 모은 Python/C 모노레포입니다.
**RheeWorks ForConvinience** is a Python/C monorepo of personal daily convenience tools.

---

## 기여 안내 / Contribution Notice

본 저장소는 **외부 기여 및 Pull Request를 받지 않습니다.**
This repository does **NOT** accept external contributions or Pull Requests.

---

## 아키텍처 / Architecture (ERD)

```mermaid
graph TB
    subgraph Shared["공유 인프라 / Shared Infrastructure"]
        AG[agents_brain/<br/>에이전트 작업 로그]
        RT[recycle_trash/<br/>코드 백업 보관소]
        CI[.github/workflows/deploy.yml<br/>CI/CD: PyInstaller + Docker + Release]
    end

    subgraph Typer["Typer-타이퍼 Series"]
        TB[베이직 버전-Basic Version<br/>가짜 타이핑 복사 도구]
        TP[포모도로 버전-Pomodoro Version<br/>포모도로 타이머 + 시크릿 엔진]
    end

    subgraph Rucia["Rucia-루시아 Series"]
        RP[Pris-프리스<br/>생산성 통계 대시보드]
        RL[Lavendar-라벤다르<br/>자동 파일 백업]
        RF[Frytesty-프라이테스티<br/>알고리즘 자동 테스터]
    end

    subgraph Automaker["Automaker-오토메이커 Series"]
        AC[클리커-Clicker<br/>마우스 오토 클릭커]
        AT[텍스트생성기-Text Generator<br/>더미 텍스트 생성]
        AP[프로젝트 템플릿 생성<br/>Project Template Generator<br/>다국어 스캐폴딩]
    end

    subgraph StudyAI["StudyAI Series"]
        SC[StudyAI - MV (C/GTK)<br/>AI 채팅 - C 바이너리]
        SP[StudyAI - MV - Python<br/>AI 채팅 - PySide6]
    end

    subgraph External["외부 연동 / External"]
        API[JUNI AI Relay API<br/>api.rheehose.com]
    end

    SC --> API
    SP --> API
    AG -.->|세션 기록| Typer
    AG -.->|세션 기록| Rucia
    AG -.->|세션 기록| Automaker
    AG -.->|세션 기록| StudyAI
```

---

## 패키지 목록 / Package List

본 프로젝트의 모든 디렉토리는 **독립적인 패키지**이며, 각각 고유한 가상환경(`venv`)과 의존성을 가집니다.
Every directory below is an **independent package** with its own venv and dependencies.

### Typer-타이퍼 Series — 가짜 타이핑 / Fake Typing

| 패키지 | 언어 | 프레임워크 | 설명 |
|--------|------|-----------|------|
| [베이직 버전-Basic Version](./Utilities%20유틸리티/Typer-타이퍼%20Series/베이직%20버전-Basic%20Version/) | Python | CustomTkinter | 원천 파일을 읽어 키 입력으로 재생산 |
| [포모도로 버전-Pomodoro Version](./Utilities%20유틸리티/Typer-타이퍼%20Series/포모도로%20버전-Pomodoro%20Version/) | Python | CustomTkinter | 25분 집중 타이머 + 은닉 타이핑 콘솔 |

### Rucia-루시아 Series — 생산성 / Productivity

| 패키지 | 언어 | 프레임워크 | 설명 |
|--------|------|-----------|------|
| [Pris-프리스](./Utilities%20유틸리티/Rucia-루시아%20Series/Pris-프리스/) | Python | CustomTkinter + Matplotlib + SQLite | 공부/코딩 시간 트래킹 대시보드 |
| [Lavendar-라벤다르](./Utilities%20유틸리티/Rucia-루시아%20Series/Lavendar-라벤다르/) | Python | CustomTkinter | 실습실 파일 자동 백업 (주기적 + 정리) |
| [Frytesty-프라이테스티](./Utilities%20유틸리티/Rucia-루시아%20Series/Frytesty-프라이테스티/) | Python | CustomTkinter | 알고리즘 풀이 자동 채점 및 diff 리포팅 |

### Automaker-오토메이커 Series — 자동화 / Automation

| 패키지 | 언어 | 프레임워크 | 설명 |
|--------|------|-----------|------|
| [클리커-Clicker](./Utilities%20유틸리티/Automaker-오토메이커%20Series/클리커-Clicker/) | Python | CustomTkinter + pynput | 단축키 기반 프리미엄 오토 클릭커 |
| [텍스트생성기-Text Generator](./Utilities%20유틸리티/Automaker-오토메이커%20Series/텍스트생성기-Text%20Generator/) | Python | CustomTkinter | 고전 소설체 + Lorem Ipsum 더미 텍스트 생성 |
| [프로젝트 템플릿 생성-Project Template Generator](./Utilities%20유틸리티/Automaker-오토메이커%20Series/프로젝트%20템플릿%20생성-Generate%20Project%20Templates/) | Python | CustomTkinter | JSP/Python/C/Node.js/Web 프로젝트 스캐폴딩 |

### StudyAI Series — AI 채팅 / AI Chat

| 패키지 | 언어 | 프레임워크 | 설명 |
|--------|------|-----------|------|
| [StudyAI - MV](./Utilities%20유틸리티/StudyAI%20-%20Series/StudyAI%20-%20MV/) | C | GTK+3 + libcurl + cJSON | AI 채팅 그레이스케일 GUI (바이너리) |
| [StudyAI - MV - Python](./Utilities%20유틸리티/StudyAI%20-%20Series/StudyAI%20-%20MV%20-%20Python/) | Python | PySide6 | 터미널 스타일 AI 채팅 + 한글 입력 엔진 |

---

## 시작하기 / Quick Start

모든 패키지는 동일한 실행 방식을 따릅니다.

```bash
cd "Utilities 유틸리티/Typer-타이퍼 Series/베이직 버전-Basic Version"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run_gui.sh    # GUI 모드
# 또는 ./run_cli.sh  # CLI 모드
```

---

## 공유 인프라 / Shared Infrastructure

| 디렉토리 | 용도 |
|----------|------|
| `agents_brain/` | AI 에이전트 작업 세션 기록 (추적 중) |
| `recycle_trash/` | 코드 수정 전 원본 파일 백업 (추적 중) |
| `.github/workflows/deploy.yml` | CI/CD: 3OS PyInstaller + Docker (GHCR) + GitHub Release |

---

## 참고 문서 / Reference

- [GEMINI.md](./GEMINI.md) — AI 어시스턴트 작동 규칙
- [JUNI_AI_RELAY_GUIDE.md](./Utilities%20유틸리티/StudyAI%20-%20Series/JUNI_AI_RELAY_GUIDE.md) — StudyAI API 가이드
- [CONTRIBUTING.md](./CONTRIBUTING.md) — 저장소 관리 규칙
- [TIMELINE.md](./TIMELINE.md) — 변경 이력

---

**Copyright (c) 2008-2026 Rheehose (Rhee Creative)**  
**Licensed under the Apache 2.0 License**  
**Website: [rheehose.com](https://rheehose.com)**
