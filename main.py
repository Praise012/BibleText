#!/usr/bin/env python3
"""
BIBLETEXT Linux - Church Scripture Presentation Software
=========================================================
A production-grade native desktop application replicating the workflow,
instant keyboard navigation, dual-window projection architecture, and
parallel Bible translations of church presentation software on Linux.

Features:
  - Rapid hotkey verse input ('Jn 3 16', 'Gen 1:1-5', 'Ps 23')
  - Fullscreen external display or 16:9 widescreen corner placement (bottom-right / bottom-left)
  - Offline Bible upload from computer (.json, .csv, OpenSong .xml)
  - Direct in-app Free Bibles installer
  - Custom background video loops (.mp4) and pictures upload

Usage:
    python3 main.py
    python3 main.py --db /path/to/custom_bible.sqlite
    python3 main.py --windowed
"""

import sys
import os
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon
    from PyQt6.QtCore import Qt
except ImportError:
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        from PySide6.QtCore import Qt
    except ImportError:
        print("\n[ERROR] PyQt6 or PySide6 is required to run BIBLETEXT Linux.")
        print("Install via pip:")
        print("    pip3 install PyQt6 PyQt6-Multimedia\n")
        print("Or via Ubuntu / Debian apt:")
        print("    sudo apt update && sudo apt install python3-pyqt6 python3-pyqt6.qtmultimedia\n")
        sys.exit(1)

from database import BibleDatabase
from settings import SettingsManager
from ui_projection import ProjectionWindow
from ui_control import ControlWindow
from setup_bible_db import build_database

def parse_args():
    parser = argparse.ArgumentParser(description="BIBLETEXT Linux Presentation Software")
    parser.add_argument("--db", default=str(SCRIPT_DIR / "sample_bible.sqlite"), help="Path to SQLite Bible database")
    parser.add_argument("--windowed", action="store_true", help="Force projection screen to run in windowed mode")
    parser.add_argument("--screen", type=int, default=None, help="Target screen index for projector (0 = Primary, 1 = Secondary)")
    return parser.parse_args()

def main():
    args = parse_args()

    db_file = Path(args.db)
    if not db_file.exists():
        print(f"[BIBLETEXT] Database '{db_file}' not found. Generating default seed database...")
        build_database(str(db_file))

    app = QApplication(sys.argv)
    app.setApplicationName("BIBLETEXT")
    app.setOrganizationName("BIBLETEXT")

    settings = SettingsManager()
    if args.screen is not None:
        settings.set("display", "target_screen_index", args.screen)
    if args.windowed:
        settings.set("display", "output_mode", "windowed")

    db = BibleDatabase(str(db_file))

    # Initialize Projection Window (standby in background, does NOT launch automatically)
    projection_win = ProjectionWindow(settings)
    projection_win.hide()

    # Initialize Operator Control Window
    control_win = ControlWindow(db, settings, projection_win)
    control_win.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
