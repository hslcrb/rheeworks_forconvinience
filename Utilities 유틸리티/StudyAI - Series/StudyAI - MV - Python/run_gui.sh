#!/bin/bash
# StudyAI - MV - Python 실행 스크립트 / Run Script
# Rheehose (Rhee Creative) 2008-2026

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 입력 방식 설정 (한글 입력 지원) / Input method setup (Korean input support)
# PySide6 bundled Qt often conflicts with system fcitx plugin.
# Using 'ibus' is generally more stable with PySide6's bundled ibus plugin.

if command -v ibus-daemon >/dev/null 2>&1; then
    export QT_IM_MODULE=ibus
    export XMODIFIERS="@im=ibus"
    echo "[INFO] Using IBus for Korean input support."
else
    # Fallback to fcitx if ibus is not found, but warn about potential issues
    export QT_IM_MODULE=fcitx
    export XMODIFIERS="@im=fcitx"
    echo "[WARN] IBus not found. Falling back to fcitx (might have compatibility issues with Alt-key)."
fi

# Ensure system Qt plugins are NOT mixed if using bundled PySide6 plugins
# Instead, we rely on PySide6's own plugins now.

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
