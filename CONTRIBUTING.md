# Contributing to RheeWorks ForConvinience (Monorepo)

본 프로젝트는 **모노레포(Monorepo)** 구조를 채택하고 있습니다. 모든 기여자는 다음 수칙을 반드시 준수해야 합니다.  
This project adopts a **Monorepo** structure. All contributors must adhere to the following rules.

---

## 🏗 모노레포 관리 수칙 / Monorepo Rules

1. **독립적 종속성 / Independent Dependencies**
   - 각 프로젝트(예: Typer, Automaker)는 루트가 아닌 각 폴더 내부의 `venv`와 `requirements.txt`를 통해 종속성을 관리합니다.
   - Each project manages dependencies through its own `venv` and `requirements.txt` within its folder.

2. **작업 기록 및 백업 / Logs & Backups (MUST TRACK)**
   - 모든 에이전트 작업 기록(`agents_brain/`)과 파편 백업(`recycle_trash/`)은 깃에 의해 추적됩니다. 수정 전 반드시 `recycle_trash/`에 백업본을 생성하십시오.
   - All agent work logs (`agents_brain/`) and fragment backups (`recycle_trash/`) are tracked by Git. Always create a backup in `recycle_trash/` before modifications.

3. **한영병기 기준 / Bilingual Documentation**
   - 모든 새로운 문서, 주석, 이슈 및 커밋 메시지는 한국어 선행, 영어 후행의 한영병기(`한글 / English`) 형식을 따릅니다.
   - All documents, comments, issues, and commit messages must be bilingual, with Korean first and English second.

4. **프리미엄 미학 / Premium Aesthetics**
   - UI 작업 시 `CustomTkinter`와 HSL 컬러 팔레트를 사용하여 프리미엄 수준의 디자인을 유지해야 합니다.
   - Maintain premium design quality using `CustomTkinter` and HSL color palettes for UI work.

---

## 🚀 워크플로우 / Workflow

1. 작업 전 `TIMELINE.md`에 계획을 추가합니다.
2. 각 프로젝트 폴더의 `venv`를 활용하여 개발 및 테스트를 진행합니다.
3. 작업 완료 후 `agents_brain/docs/session_brain.md`를 업데이트합니다.
4. 모든 문서(README, CONTRIBUTING 등)에 변경 사항이 적절히 반영되었는지 확인합니다.

---

**Rheehose (Rhee Creative) 2008-2026**  
"Quality and Consistency in one place."
