#!/bin/bash
# ==========================================================
# BibleShow Linux Quick Launcher Script
# ==========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Run 'sudo apt install python3' first."
    exit 1
fi

# Build seed SQLite database if missing
if [ ! -f "sample_bible.sqlite" ]; then
    echo "[BibleShow] Initializing sample scripture database..."
    python3 setup_bible_db.py
fi

# Launch application
echo "[BibleShow] Launching BibleShow Linux Desktop Presentation..."
python3 main.py "$@"
