#!/bin/bash
# StudyAI - MV - Python 실행 스크립트 / Run Script
# Rheehose (Rhee Creative) 2008-2026

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 입력 방식 설정 (한글 입력 지원) / Input method setup (Korean input support)
# Detect and set IM module for Qt / Qt용 IM 모듈 감지 및 설정
if [ -n "$GTK_IM_MODULE" ]; then
    export QT_IM_MODULE="$GTK_IM_MODULE"
fi

# Ensure system Qt plugins are accessible for IM / IM을 위한 시스템 Qt 플러그인 접근 보장
if [ -d "/usr/lib/x86_64-linux-gnu/qt6/plugins" ]; then
    export QT_PLUGIN_PATH="${QT_PLUGIN_PATH:+$QT_PLUGIN_PATH:}/usr/lib/x86_64-linux-gnu/qt6/plugins"
fi

# 가상환경 확인 및 생성 / Check and create virtual environment
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중... / Creating virtual environment..."
    python3 -m venv venv
fi

# 가상환경 활성화 / Activate virtual environment
source venv/bin/activate

# 의존성 설치 / Install dependencies
pip install -q -r requirements.txt

# 실행 / Run
python main.py
