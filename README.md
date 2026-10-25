# BIBLETEXT Linux - Church Scripture Presentation Software

A native, high-performance Linux desktop application replicating the core workflow, rapid keyboard navigation, dual-window projection architecture, and multi-translation parallel display of church presentation software.

Built with **Python 3**, **PyQt6 / PySide6**, and **SQLite**.

---

## ⚡ Key Highlights & Architecture

## ⚡ Key Highlights & Architecture

1. **Dual-Window Architecture & PIP Screen Controller**:
   - **Operator Control Console (`ui_control.py`)**: Instant search syntax, book/chapter matrix, verse preview, parallel translation switcher, and central PIP output mode controller.
   - **Output Projection Display (`ui_projection.py`)**:
     - **No Auto-Launch on Start**: Secondary output stays closed on app launch until commanded by the operator.
     - **PIP Output Controller**: Select from `Off (Hidden)`, `16:9 Bottom-Right PIP`, `16:9 Bottom-Left PIP`, `16:9 Top-Right PIP`, `16:9 Top-Left PIP`, `Fullscreen Projector`, or `Windowed Mode`.
     - Text stroke outline, drop shadow, and smooth fade transitions.
2. **Pre-Installed Full Bibles & Offline Management**:
   - **Pre-installed Translations**: KJV, WEB, French Louis Segond (LSG), Spanish Reina-Valera (RV1909), Swahili (SUV), American Standard Version (ASV), Darby (DBY), and Young's Literal (YLT) — all 66 books from Genesis to Revelation available offline with zero missing chapters or verses.
   - **Load Bible from Computer**: Import local Bible files in JSON (`.json`), CSV (`.csv`), or OpenSong XML (`.xml`).
   - **Install Free Online Bibles**: 1-click in-app repository installer for additional public domain translations without exiting.
3. **Custom Background Media**:
   - **Upload Background Pictures**: Load church imagery (`.png`, `.jpg`, `.webp`).
   - **Upload Background Videos**: Seamlessly loop worship motion video clips (`.mp4`, `.webm`, `.mov`).
   - Contrast dimming overlay slider (0% to 100%).
4. **Keyboard-First Navigation & Customizable Hotkeys**:
   - **`Ctrl+F` Scripture Search**: Instant hotkey to focus the global search bar (`Jn 3 16`, `Gen 1:1-5`, `Ps 23`, `1 Cor 13 4-8`, `Rom 8:28`).
   - **Hotkeys & Shortcuts Tab in Settings**: Easily re-bind and customize shortcuts for every command:
     - `Ctrl+F`: Focus scripture search
     - `Enter`: Instantly push selected verse to live projection screen
     - `Ctrl+M`: Cycle PIP screen output modes (`off` -> `bottom-right` -> `bottom-left` -> `fullscreen`)
     - `F5` / `Ctrl+P`: Toggle Fullscreen Projection Output
     - `Esc` / `F12`: Clear live scripture text (preserves background)
     - `Ctrl+B`: Toggle Blackout Screen
     - `Ctrl+L`: Toggle Church Hold / Logo Screen
     - `Ctrl+T`: Open Preferences & Appearance Dialog
     - `Up / Down Arrows`: Next / Previous verse
     - `Left / Right Arrows`: Next / Previous chapter
5. **Multi-Translation & Parallel Engine (`database.py`)**:
   - High-speed SQLite schema with multi-column indexes.
   - Dual-Bible rendering: Stacked or Side-by-Side on the same presentation slide.

---

## 🚀 Quick Start on Linux (Ubuntu / Zorin OS / Debian / Mint)

### 1. Install System Dependencies & Python Packages
```bash
# Update package repositories
sudo apt update

# Install Python 3, pip, and PyQt6
sudo apt install -y python3 python3-pip python3-pyqt6 python3-pyqt6.qtmultimedia
```

### 2. Initialize the SQLite Bible Database
```bash
python3 setup_bible_db.py
```

### 3. Run BIBLETEXT
```bash
# Launch with default dual-screen detection
python3 main.py

# Or run in single-screen testing mode
python3 main.py --windowed
```
Or simply run:
```bash
./run.sh
```

---

## 🖥 Corner 16:9 Output Screen Configuration
To display the projection screen anchored in a corner (PIP mode):
1. Press `Ctrl+T` to open **Settings**.
2. Under **Monitor & Display**, select:
   - **Bottom-Right Corner (16:9 Widescreen PIP)**, or
   - **Bottom-Left Corner (16:9 Widescreen PIP)**.
3. Adjust the **Corner Screen Width** slider (e.g. 480px, 560px).
4. Click **Save & Apply Preferences**.
