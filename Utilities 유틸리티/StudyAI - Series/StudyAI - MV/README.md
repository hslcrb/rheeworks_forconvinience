# StudyAI - MV (Minimum Viable)

간단한 C 언어 기반의 AI 채팅 애플리케이션입니다.
A simple C-based AI chat application.

## 🛠️ 기능 / Features
- **Premium UI**: ChatGPT-style Start Screen & Bubble Chat / ChatGPT 스타일 시작 화면 및 버블 채팅
- **Streaming**: Real-time AI response streaming / 실시간 AI 응답 스트리밍
- **Markdown**: Supports **Bold**, *Italic*, and `Code` rendering / **굵게**, *기울임*, `코드` 렌더링 지원
- **Performance**: High-performance C/GTK implementation / 고성능 C/GTK 구현
- **Mistral API**: Mistral Small Model (Streaming enabled) / Mistral Small 모델 (스트리밍 활성화)

## 🏗️ CI/CD
- **Automated Build**: GitHub Actions automatically builds Linux binaries / GitHub Actions가 리눅스 바이너리를 자동 빌드
- **Release**: Executables included in GitHub Releases / 실행 파일이 깃허브 릴리즈에 포함됨

## 📦 의존성 / Dependencies
```bash
sudo apt-get install libgtk-3-dev libcurl4-openssl-dev
```

## 🚀 빌드 및 실행 / Build & Run
```bash
# 빌드 / Build
make

# 실행 / Run
./studyaimv
```

## 📝 라이선스 / License
Apache 2.0
