# RheeWorks ForConvinience (Python Monorepo)

**RheeWorks ForConvinience**는 다양한 일상 편의를 위한 도구들을 포함하는 **단일 깃 저장소 기반의 모노레포(Monorepo)** 프로젝트입니다.  
**RheeWorks ForConvinience** is a **Git-based Monorepo** project containing various tools for daily convenience.

---

## 🏗 프로젝트 구조 / Project Structure (Monorepo)

본 프로젝트는 다음과 같은 서브 프로젝트 군으로 구성되어 있으며, 각 프로젝트는 독립적인 가상환경(`venv`)과 종속성을 가집니다.  
This project is organized into the following sub-project series, each with its own virtual environment (`venv`) and dependencies.

### 1. Typer-타이퍼 Series
- **[베이직 버전-Basic Version](file:///home/rheehose/문서/rheeworks_forconvinience/Typer-타이퍼%20Series/베이직%20버전-Basic%20Version/)**: 원천 텍스트를 읽어 키보드 입력 시 가짜로 타이핑해주는 프리미엄 도구.
- **[포모도로 버전-Pomodoro Version](file:///home/rheehose/문서/rheeworks_forconvinience/Typer-타이퍼%20Series/포모도로%20버전-Pomodoro%20Version/)**: 포모도로 타이머와 가짜 타이핑 비밀 콘솔이 결합된 도구.

### 2. Rucia-루시아 Series [NEW]
- **Dashboard-대시보드**: 공부/코딩 시간 통계 대시보드 (Premium UI) / Study/Coding time stats dashboard.
- **Backup-백업기**: 실습실 파일 자동 백업 도구 / Lab file auto-backup tool.
- **Tester-테스트기**: 알고리즘 문제풀이 로직 테스트기 / Algorithm problem auto-tester.

### 3. Automaker-오토메이커 Series
- **[클리커-Clicker](file:///home/rheehose/문서/rheeworks_forconvinience/Automaker-오토메이커%20Series/클리커-Clicker/)**: 고성능 마우스 오토 클릭커 도구.
- **[텍스트생성기-Text Generator](file:///home/rheehose/문서/rheeworks_forconvinience/Automaker-오토메이커%20Series/텍스트생성기-Text%20Generator/)**
  - 다양한 언어와 옵션의 더미 텍스트 생성 도구
  - Dummy text generation tool with various languages and options
- **[프로젝트 템플릿 생성-Project Template Generator](file:///home/rheehose/문서/rheeworks_forconvinience/Automaker-오토메이커%20Series/프로젝트%20템플릿%20생성-Generate%20Project%20Templates/)**
  - **다국어 지원 (JSP, Python, C, Node.js, Web)** 스캐폴딩 도구
  - **Multi-language Scaffolding Tool** (JSP, Python, C, Node.js, Web)
  - **Premium UI**: 도구별 최적화된 초기 환경 및 코드 자동 구성

---

## 🛠 모노레포 관리 및 기여 / Monorepo Management & Contributing

### 프로젝트 공유 폴더 / Shared Folders
- **`agents_brain/`**: 에이전트의 작업 기록 및 세션 데이터가 보관되는 폴더입니다. (추적 중) / Folders for agent work logs and session data. (Tracked)
- **`recycle_trash/`**: 코드 수정 시 원본 파일을 안전하게 백업하는 재활용 휴지통 폴더입니다. / Recycle bin folder for safely backing up original files during modifications.
- **`.github/workflows/`**: 모노레포 전체의 자동 빌드 및 배포(CI/CD) 설정을 관리합니다. / Manages automated build and deployment (CI/CD) for the entire monorepo.

### 시작하기 / Getting Started
각 프로젝트 폴더로 이동하여 해당 가상환경을 활성화한 후 실행하십시오.  
Navigate to each project folder, activate its venv, and run.

```bash
cd "Typer-타이퍼 Series/베이직 버전-Basic Version"
source venv/bin/activate
python main.py
```

---

## 📜 가이드라인 / Guidelines

- **에이전트 수칙**: [GEMINI.md](file:///home/rheehose/문서/rheeworks_forconvinience/GEMINI.md)
- **기여 방법**: [CONTRIBUTING.md](file:///home/rheehose/문서/rheeworks_forconvinience/CONTRIBUTING.md)
- **프로젝트 타임라인**: [TIMELINE.md](file:///home/rheehose/문서/rheeworks_forconvinience/TIMELINE.md)

---

**Copyright (c) 2008-2026 Rheehose (Rhee Creative)**  
**Licensed under the Apache 2.0 License**  
**Website: [rheehose.com](https://rheehose.com)**
