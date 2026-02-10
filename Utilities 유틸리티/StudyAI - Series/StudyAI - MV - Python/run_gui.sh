#!/bin/bash
# StudyAI - MV - Python 실행 스크립트 / Run Script
# Rheehose (Rhee Creative) 2008-2026

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 입력 방식 설정 (한글 입력 지원) / Input method setup (Korean input support)
# PySide6 bundled Qt often has symbol mismatch with system fcitx-qt6 plugin.
# We fallback to XIM (X Input Method) which fcitx/ibus both support via Xlib.
# Also forcing LC_CTYPE to ko_KR.utf8 is crucial for IM triggering.

export LC_CTYPE=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8  # Force overall locale to ensure Korean support
export LANG=ko_KR.UTF-8

if pgrep -x "fcitx" > /dev/null; then
    export QT_IM_MODULE=xim
    export XMODIFIERS="@im=fcitx"
    echo "[INFO] Detected fcitx. Using XIM fallback for compatibility."
elif pgrep -x "ibus-daemon" > /dev/null; then
    export QT_IM_MODULE=xim
    export XMODIFIERS="@im=ibus"
    echo "[INFO] Detected IBus. Using XIM fallback for compatibility."
else
    # Default fallback
    export QT_IM_MODULE=xim
    export XMODIFIERS="@im=fcitx"
    echo "[WARN] No active IM daemon detected (fcitx/ibus). Proceeding with XIM/fcitx settings."
fi

# Ensure we don't use the broken fcitx-qt6 plugin we copied earlier
# (Note: main.py setup_input_method should also be cleaned up)


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
