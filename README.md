# RheeWorks ForConvinience (Python & C Monorepo)

**RheeWorks ForConvinience**는 다양한 일상 편의를 위한 도구들을 포함하는 **단일 깃 저장소 기반의 모노레포(Monorepo)** 프로젝트입니다.  
**RheeWorks ForConvinience** is a **Git-based Monorepo** project containing various tools for daily convenience.

---

## 🏗 프로젝트 구조 / Project Structure (Monorepo)

본 프로젝트는 다음과 같은 서브 프로젝트 군으로 구성되어 있으며, 각 프로젝트는 독립적인 가상환경(`venv`)과 종속성을 가집니다.  
This project is organized into the following sub-project series, each with its own virtual environment (`venv`) and dependencies.

### 1. Typer-타이퍼 Series
- **[베이직 버전-Basic Version](./Utilities%20유틸리티/Typer-타이퍼%20Series/베이직%20버전-Basic%20Version/)**: 원천 텍스트 기반 가짜 타이핑 도구 (GUI/CLI)
- **[포모도로 버전-Pomodoro Version](./Utilities%20유틸리티/Typer-타이퍼%20Series/포모도로%20버전-Pomodoro%20Version/)**: 포모도로 타이머 + 비밀 타이핑 콘솔 (GUI/CLI)

### 2. Rucia-루시아 Series
- **[Pris-프리스](./Utilities%20유틸리티/Rucia-루시아%20Series/Pris-프리스/)**: 생산성 통계 대시보드 (GUI/CLI)
- **[Lavendar-라벤다르](./Utilities%20유틸리티/Rucia-루시아%20Series/Lavendar-라벤다르/)**: 자동 파일 백업 도구 (GUI/CLI)
- **[Frytesty-프라이테스티](./Utilities%20유틸리티/Rucia-루시아%20Series/Frytesty-프라이테스티/)**: 알고리즘 문제풀이 자동 테스트기 (GUI/CLI)

### 3. Automaker-오토메이커 Series
- **[클리커-Clicker](./Utilities%20유틸리티/Automaker-오토메이커%20Series/클리커-Clicker/)**: 고성능 마우스 오토 클릭커 (GUI/CLI)
- **[텍스트생성기-Text Generator](./Utilities%20유틸리티/Automaker-오토메이커%20Series/텍스트생성기-Text%20Generator/)**: 더미 텍스트 생성 도구 (GUI/CLI)
- **[프로젝트 템플릿 생성-Project Template Generator](./Utilities%20유틸리티/Automaker-오토메이커%20Series/프로젝트%20템플릿%20생성-Generate%20Project%20Templates/)**: 다국어 스캐폴딩 도구 (GUI/CLI)

### 4. StudyAI Series
- **[StudyAI - MV](./Utilities%20유틸리티/StudyAI%20-%20Series/StudyAI%20-%20MV/)**: AI 채팅 앱 C/GTK 버전 (Grayscale GUI)
- **[StudyAI - MV - Python](./Utilities%20유틸리티/StudyAI%20-%20Series/StudyAI%20-%20MV%20-%20Python/)**: AI 채팅 앱 PySide6 터미널 스타일 GUI 버전 (Terminal-Style GUI)

---

## 🛠 모노레포 관리 및 기여 / Monorepo Management & Contributing

### 프로젝트 공유 폴더 / Shared Folders
- **`agents_brain/`**: 에이전트의 작업 기록 및 세션 데이터가 보관되는 폴더입니다. (추적 중) / Folders for agent work logs and session data. (Tracked)
- **`recycle_trash/`**: 코드 수정 시 원본 파일을 안전하게 백업하는 재활용 휴지통 폴더입니다. / Recycle bin folder for safely backing up original files during modifications.
- **`.github/workflows/`**: 모노레포 전체의 자동 빌드 및 배포(CI/CD) 설정을 관리합니다. / Manages automated build and deployment (CI/CD) for the entire monorepo.

각 프로젝트 폴더로 이동하여 신규 제공되는 실행 스크립트(`run_*.sh` 또는 `run_*.bat`)를 사용하십시오.  
Navigate to each project folder and use the new launch scripts.

```bash
cd "Utilities 유틸리티/Typer-타이퍼 Series/베이직 버전-Basic Version"
./run_gui.sh # GUI 실행
./run_cli.sh # CLI 실행
```

---

## 📜 가이드라인 / Guidelines

- **에이전트 수칙**: [GEMINI.md](./GEMINI.md)
- **API 이용 가이드**: [JUNI_AI_RELAY_GUIDE.md](./Utilities%20유틸리티/StudyAI%20-%20Series/JUNI_AI_RELAY_GUIDE.md)
- **기여 방법**: [CONTRIBUTING.md](./CONTRIBUTING.md)
- **프로젝트 타임라인**: [TIMELINE.md](./TIMELINE.md)

---

**Copyright (c) 2008-2026 Rheehose (Rhee Creative)**  
**Licensed under the Apache 2.0 License**  
**Website: [rheehose.com](https://rheehose.com)**
