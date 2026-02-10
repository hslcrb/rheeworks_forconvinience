# StudyAI - MV (Minimum Viable)

간단한 C 언어 기반의 AI 채팅 애플리케이션입니다.
A simple C-based AI chat application.

## ✨ 주요 기능 / Key Features
- **프리미엄 UI**: SVG 벡터 그래픽, 그라디언트 배경, 부드러운 애니메이션 / Premium UI with SVG vector graphics, gradient backgrounds, smooth animations
- **스트리밍 API**: 실시간 타이핑 효과로 응답 출력 / Streaming API with real-time typing effect
- **마크다운 렌더링**: **굵게**, *기울임*, `코드`, ### 헤딩 지원 / Markdown rendering with **bold**, *italic*, `code`, ### heading support
- **복사/답장 버튼**: 각 응답에 클립보드 복사 및 재전송 버튼 / Copy and reply buttons for each response
- **라이트/다크 모드**: 테마 토글 지원 (연한 보라색/우주 테마) / Light/Dark theme toggle (light purple/cosmic themes)
- **모듈화된 디자인**: SVG 아이콘이 별도 파일로 관리되어 수정 용이 / Modular design with external SVG assets for easy customization
- **고성능 C/GTK 구현**: High-performance C/GTK implementation
- **Mistral API**: Mistral Small Model (Streaming enabled) / Mistral Small 모델 (스트리밍 활성화)

## 🏗️ CI/CD
- **Automated Build**: GitHub Actions automatically builds Linux binaries / GitHub Actions가 리눅스 바이너리를 자동 빌드
- **Release**: Executables included in GitHub Releases / 실행 파일이 깃허브 릴리즈에 포함됨

## 📦 의존성 / Dependencies
```bash
sudo apt-get install libgtk-3-dev libcurl4-openssl-dev librsvg2-dev
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
