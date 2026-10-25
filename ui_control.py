import sys
import os
from typing import Optional, List, Dict

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem,
        QSplitter, QGroupBox, QDialog, QTabWidget, QSpinBox, QCheckBox,
        QFileDialog, QColorDialog, QFontComboBox, QSlider, QFrame, QShortcut,
        QApplication, QButtonGroup, QRadioButton, QMessageBox, QProgressBar
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
    from PyQt6.QtGui import (
        QFont, QColor, QKeySequence, QIcon, QPalette, QLinearGradient, QBrush, QPainter
    )
except ImportError:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem,
        QSplitter, QGroupBox, QDialog, QTabWidget, QSpinBox, QCheckBox,
        QFileDialog, QColorDialog, QFontComboBox, QSlider, QFrame, QShortcut,
        QApplication, QButtonGroup, QRadioButton, QMessageBox, QProgressBar
    )
    from PySide6.QtCore import Qt, Signal as pyqtSignal, QTimer, QSize
    from PySide6.QtGui import (
        QFont, QColor, QKeySequence, QIcon, QPalette, QLinearGradient, QBrush, QPainter
    )

from database import BibleDatabase, ONLINE_BIBLE_CATALOG
from parser import BibleReferenceParser
from settings import SettingsManager
from ui_projection import ProjectionWindow, ScriptureRenderCanvas

DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 12px;
    font-weight: bold;
    color: #94A3B8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 5px;
}
QLineEdit {
    background-color: #1E293B;
    border: 1.5px solid #475569;
    border-radius: 6px;
    padding: 8px 12px;
    color: #F8FAFC;
    font-size: 14px;
    selection-background-color: #3B82F6;
}
QLineEdit:focus {
    border: 1.5px solid #38BDF8;
    background-color: #0F172A;
}
QPushButton {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #64748B;
}
QPushButton:pressed {
    background-color: #0EA5E9;
    color: white;
}
QPushButton#btnGoLive {
    background-color: #16A34A;
    color: white;
    border: 1px solid #22C55E;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#btnGoLive:hover {
    background-color: #15803D;
}
QPushButton#btnBlackout {
    background-color: #B91C1C;
    color: white;
    border: 1px solid #EF4444;
}
QPushButton#btnBlackout:hover {
    background-color: #991B1B;
}
QListWidget {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #F1F5F9;
}
QListWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #283548;
}
QListWidget::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
}
QListWidget::item:hover {
    background-color: #2A384F;
}
QComboBox {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 5px 10px;
    color: #F8FAFC;
}
QTabWidget::pane {
    border: 1px solid #334155;
    background: #0F172A;
}
QTabBar::tab {
    background: #1E293B;
    color: #94A3B8;
    padding: 8px 18px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #0F172A;
    color: #38BDF8;
    border-top: 2px solid #38BDF8;
    font-weight: bold;
}
"""

class PreferencesDialog(QDialog):
    """Tabbed Preferences configuration matching BIBLETEXT settings."""
    def __init__(self, db: BibleDatabase, settings_mgr: SettingsManager, projection_win: ProjectionWindow, parent=None):
        super().__init__(parent)
        self.db = db
        self.settings = settings_mgr
        self.proj_win = projection_win
        self.parent_win = parent

        self.custom_media_path = self.settings.get("background", "custom_media_path", "")
        self.custom_media_type = self.settings.get("background", "custom_media_type", "none")

        self.setWindowTitle("BIBLETEXT Preferences & Bible Management")
        self.resize(720, 520)
        self.setStyleSheet(DARK_STYLESHEET)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # TAB 1: MONITOR & DISPLAY (Includes 16:9 Corner Screen Placement)
        tab_monitor = QWidget()
        mon_layout = QVBoxLayout(tab_monitor)
        
        # Output Mode Group
        out_grp = QGroupBox("Screen Placement & Corner 16:9 Output")
        og_layout = QVBoxLayout(out_grp)

        og_layout.addWidget(QLabel("Output Screen Display Position:"))
        self.combo_out_mode = QComboBox()
        self.combo_out_mode.addItem("Fullscreen on Projector (Screen 2)", "fullscreen")
        self.combo_out_mode.addItem("Bottom-Right Corner (16:9 Widescreen PIP)", "bottom-right")
        self.combo_out_mode.addItem("Bottom-Left Corner (16:9 Widescreen PIP)", "bottom-left")
        self.combo_out_mode.addItem("Top-Right Corner (16:9 Widescreen PIP)", "top-right")
        self.combo_out_mode.addItem("Top-Left Corner (16:9 Widescreen PIP)", "top-left")
        self.combo_out_mode.addItem("Windowed Preview Mode", "windowed")

        curr_mode = self.settings.get("display", "output_mode", "fullscreen")
        idx = self.combo_out_mode.findData(curr_mode)
        if idx >= 0:
            self.combo_out_mode.setCurrentIndex(idx)
        og_layout.addWidget(self.combo_out_mode)

        # Corner Width
        c_layout = QHBoxLayout()
        c_layout.addWidget(QLabel("Corner Screen Width (px, 16:9 ratio):"))
        self.spin_corner_w = QSpinBox()
        self.spin_corner_w.setRange(320, 960)
        self.spin_corner_w.setSingleStep(20)
        self.spin_corner_w.setValue(self.settings.get("display", "corner_width_px", 480))
        c_layout.addWidget(self.spin_corner_w)
        og_layout.addLayout(c_layout)

        mon_layout.addWidget(out_grp)

        # Target Monitor Selector
        mon_grp = QGroupBox("Target Physical Monitor")
        mg_layout = QVBoxLayout(mon_grp)
        self.screen_combo = QComboBox()
        screens = QApplication.screens()
        for s_idx, s in enumerate(screens):
            geom = s.geometry()
            self.screen_combo.addItem(f"Monitor {s_idx + 1}: {s.name()} ({geom.width()}x{geom.height()})", s_idx)

        target_idx = self.settings.get("display", "target_screen_index", 1)
        if target_idx < len(screens):
            self.screen_combo.setCurrentIndex(target_idx)
        mg_layout.addWidget(self.screen_combo)

        self.chk_fullscreen = QCheckBox("Automatically lock into fullscreen on launch")
        self.chk_fullscreen.setChecked(self.settings.get("display", "fullscreen_on_launch", True))
        mg_layout.addWidget(self.chk_fullscreen)

        mon_layout.addWidget(mon_grp)
        mon_layout.addStretch()
        self.tabs.addTab(tab_monitor, "Monitor & Display")

        # TAB 2: BIBLES & INSTALLATION (Offline upload + In-app Free Bible Store)
        tab_bibles = QWidget()
        b_layout = QVBoxLayout(tab_bibles)

        # Offline Import Group
        offline_grp = QGroupBox("Load Bible from Computer (Offline Upload)")
        of_layout = QVBoxLayout(offline_grp)
        of_layout.addWidget(QLabel("Import local Bible files (.json, .csv, OpenSong .xml):"))
        
        btn_import_file = QPushButton("📂 Browse and Load Bible File from Computer...")
        btn_import_file.clicked.connect(self.on_load_offline_bible)
        of_layout.addWidget(btn_import_file)

        self.lbl_import_status = QLabel("Ready to import custom translation files.")
        self.lbl_import_status.setStyleSheet("color: #94A3B8; font-size: 11px;")
        of_layout.addWidget(self.lbl_import_status)
        b_layout.addWidget(offline_grp)

        # In-App Free Bibles Catalog
        store_grp = QGroupBox("Install Free Public Domain Bibles (In-App)")
        sg_layout = QVBoxLayout(store_grp)
        sg_layout.addWidget(QLabel("Download & activate free Bibles directly without exiting:"))

        self.bible_catalog_list = QListWidget()
        for b in ONLINE_BIBLE_CATALOG:
            item = QListWidgetItem(f"📖 {b['name']} [{b['abbreviation']}] - {b['language']}")
            item.setData(Qt.ItemDataRole.UserRole, b)
            self.bible_catalog_list.addItem(item)
        sg_layout.addWidget(self.bible_catalog_list)

        btn_install_online = QPushButton("⚡ Install Selected Bible Directly")
        btn_install_online.setObjectName("btnGoLive")
        btn_install_online.clicked.connect(self.on_install_online_bible)
        sg_layout.addWidget(btn_install_online)

        b_layout.addWidget(store_grp)
        self.tabs.addTab(tab_bibles, "Bibles & Catalog")

        # TAB 3: BACKGROUND & MEDIA (Includes Video & Picture upload buttons)
        tab_bg = QWidget()
        bg_layout = QVBoxLayout(tab_bg)

        upload_grp = QGroupBox("Upload Custom Background Media")
        ug_layout = QVBoxLayout(upload_grp)

        btn_row = QHBoxLayout()
        self.btn_upload_pic = QPushButton("🖼 Upload Background Picture...")
        self.btn_upload_pic.clicked.connect(self.on_upload_picture)
        btn_row.addWidget(self.btn_upload_pic)

        self.btn_upload_vid = QPushButton("🎬 Upload Background Video (.mp4)...")
        self.btn_upload_vid.clicked.connect(self.on_upload_video)
        btn_row.addWidget(self.btn_upload_vid)
        ug_layout.addLayout(btn_row)

        self.lbl_custom_media = QLabel(f"Active Media: {os.path.basename(self.custom_media_path) if self.custom_media_path else 'None (Using default)'}")
        self.lbl_custom_media.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 11px;")
        ug_layout.addWidget(self.lbl_custom_media)

        btn_clear_media = QPushButton("Reset / Remove Custom Media")
        btn_clear_media.clicked.connect(self.on_clear_custom_media)
        ug_layout.addWidget(btn_clear_media)

        bg_layout.addWidget(upload_grp)

        # Standard Background options
        bg_grp = QGroupBox("Preset Background Options")
        bgg_layout = QVBoxLayout(bg_grp)
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["Solid Color", "Preset Image", "Looping MP4 Video"])
        bgg_layout.addWidget(self.bg_type_combo)

        bgg_layout.addWidget(QLabel("Dark Contrast Overlay Dimming (0% - 100%):"))
        self.slider_dim = QSlider(Qt.Orientation.Horizontal)
        self.slider_dim.setRange(0, 100)
        self.slider_dim.setValue(self.settings.get("background", "overlay_dim_percent", 35))
        bgg_layout.addWidget(self.slider_dim)
        bg_layout.addWidget(bg_grp)
        bg_layout.addStretch()

        self.tabs.addTab(tab_bg, "Background & Media")

        # TAB 4: TYPOGRAPHY
        tab_typo = QWidget()
        t_layout = QVBoxLayout(tab_typo)
        t_grp = QGroupBox("Scripture Font & Colors")
        tg_layout = QGridLayout(t_grp)

        tg_layout.addWidget(QLabel("Font Family:"), 0, 0)
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.settings.get("typography", "font_family", "DejaVu Sans")))
        tg_layout.addWidget(self.font_combo, 0, 1)

        tg_layout.addWidget(QLabel("Font Size (px):"), 1, 0)
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(20, 120)
        self.spin_font_size.setValue(self.settings.get("typography", "font_size", 42))
        tg_layout.addWidget(self.spin_font_size, 1, 1)

        tg_layout.addWidget(QLabel("Reference Size (px):"), 2, 0)
        self.spin_ref_size = QSpinBox()
        self.spin_ref_size.setRange(16, 80)
        self.spin_ref_size.setValue(self.settings.get("typography", "reference_font_size", 28))
        tg_layout.addWidget(self.spin_ref_size, 2, 1)

        tg_layout.addWidget(QLabel("Text Alignment:"), 3, 0)
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Center", "Top", "Bottom", "LowerThird"])
        self.align_combo.setCurrentText(self.settings.get("typography", "text_alignment", "Center"))
        tg_layout.addWidget(self.align_combo, 3, 1)

        self.chk_outline = QCheckBox("Render High-Contrast Text Outline Stroke")
        self.chk_outline.setChecked(self.settings.get("typography", "outline_enabled", True))
        tg_layout.addWidget(self.chk_outline, 4, 0, 1, 2)

        self.chk_shadow = QCheckBox("Render Deep Drop Shadow")
        self.chk_shadow.setChecked(self.settings.get("typography", "shadow_enabled", True))
        tg_layout.addWidget(self.chk_shadow, 5, 0, 1, 2)

        t_layout.addWidget(t_grp)
        t_layout.addStretch()
        self.tabs.addTab(tab_typo, "Typography")

        # TAB 5: HOTKEYS & KEYBOARD SHORTCUTS
        tab_hotkeys = QWidget()
        hk_layout = QVBoxLayout(tab_hotkeys)
        hk_grp = QGroupBox("Customizable Keyboard Shortcuts")
        hkg_layout = QGridLayout(hk_grp)

        self.hotkey_inputs = {}
        hk_cfg = self.settings.data.get("hotkeys", {})

        shortcut_definitions = [
            ("search", "Focus Scripture Search", hk_cfg.get("search", "Ctrl+F")),
            ("go_live", "Push Verse Live (Go Live)", hk_cfg.get("go_live", "Return")),
            ("clear", "Clear Text from Screen", hk_cfg.get("clear", "Escape")),
            ("blackout", "Toggle Blackout Screen", hk_cfg.get("blackout", "Ctrl+B")),
            ("logo", "Toggle Logo / Hold Screen", hk_cfg.get("logo", "Ctrl+L")),
            ("fullscreen", "Toggle Output Fullscreen", hk_cfg.get("fullscreen", "F5")),
            ("settings", "Open Settings & Preferences", hk_cfg.get("settings", "Ctrl+T")),
            ("next_verse", "Navigate to Next Verse", hk_cfg.get("next_verse", "Down")),
            ("prev_verse", "Navigate to Previous Verse", hk_cfg.get("prev_verse", "Up")),
            ("next_chapter", "Next Chapter", hk_cfg.get("next_chapter", "Right")),
            ("prev_chapter", "Previous Chapter", hk_cfg.get("prev_chapter", "Left")),
            ("toggle_pip", "Toggle Screen Output / PIP", hk_cfg.get("toggle_pip", "Ctrl+M")),
        ]

        for row_idx, (key, label, val) in enumerate(shortcut_definitions):
            hkg_layout.addWidget(QLabel(f"{label}:"), row_idx, 0)
            line_edit = QLineEdit(val)
            line_edit.setMaximumWidth(200)
            hkg_layout.addWidget(line_edit, row_idx, 1)
            self.hotkey_inputs[key] = line_edit

        hk_layout.addWidget(hk_grp)

        btn_reset_hk = QPushButton("Reset Hotkeys to Default")
        btn_reset_hk.clicked.connect(self.on_reset_hotkeys)
        hk_layout.addWidget(btn_reset_hk)
        hk_layout.addStretch()

        self.tabs.addTab(tab_hotkeys, "Hotkeys & Shortcuts")

        main_layout.addWidget(self.tabs)

        # Dialog Buttons
        btn_box = QHBoxLayout()
        btn_save = QPushButton("Save & Apply Preferences")
        btn_save.setObjectName("btnGoLive")
        btn_save.clicked.connect(self.save_and_apply)

        btn_cancel = QPushButton("Close")
        btn_cancel.clicked.connect(self.accept)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        main_layout.addLayout(btn_box)

    def on_load_offline_bible(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Offline Bible File",
            "",
            "Bible Files (*.json *.csv *.xml);;JSON Files (*.json);;CSV Files (*.csv);;XML Files (*.xml);;All Files (*.*)"
        )
        if not file_path:
            return

        success, msg = self.db.import_bible_from_file(file_path)
        if success:
            QMessageBox.information(self, "Bible Imported", msg)
            self.lbl_import_status.setText(f"✓ {msg}")
            self.lbl_import_status.setStyleSheet("color: #22C55E; font-size: 11px;")
            if self.parent_win and hasattr(self.parent_win, "_load_translations"):
                self.parent_win._load_translations()
        else:
            QMessageBox.warning(self, "Import Failed", msg)
            self.lbl_import_status.setText(f"✗ {msg}")
            self.lbl_import_status.setStyleSheet("color: #EF4444; font-size: 11px;")

    def on_install_online_bible(self):
        item = self.bible_catalog_list.currentItem()
        if not item:
            QMessageBox.information(self, "Select Bible", "Please choose a translation from the list first.")
            return

        b = item.data(Qt.ItemDataRole.UserRole)
        success, msg = self.db.download_online_bible(b["id"])
        if success:
            QMessageBox.information(self, "Installation Complete", msg)
            if self.parent_win and hasattr(self.parent_win, "_load_translations"):
                self.parent_win._load_translations()
        else:
            QMessageBox.warning(self, "Installation Issue", msg)

    def on_upload_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Picture", "", "Image Files (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file_path:
            self.custom_media_path = file_path
            self.custom_media_type = "image"
            self.lbl_custom_media.setText(f"Active Picture: {os.path.basename(file_path)}")

    def on_upload_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Video", "", "Video Files (*.mp4 *.mkv *.avi *.mov *.webm)"
        )
        if file_path:
            self.custom_media_path = file_path
            self.custom_media_type = "video"
            self.lbl_custom_media.setText(f"Active Video: {os.path.basename(file_path)}")

    def on_clear_custom_media(self):
        self.custom_media_path = ""
        self.custom_media_type = "none"
        self.lbl_custom_media.setText("Active Media: None (Using default)")

    def on_reset_hotkeys(self):
        defaults = {
            "search": "Ctrl+F",
            "go_live": "Return",
            "clear": "Escape",
            "blackout": "Ctrl+B",
            "logo": "Ctrl+L",
            "fullscreen": "F5",
            "settings": "Ctrl+T",
            "next_verse": "Down",
            "prev_verse": "Up",
            "next_chapter": "Right",
            "prev_chapter": "Left",
            "toggle_pip": "Ctrl+M"
        }
        for k, v in defaults.items():
            if k in self.hotkey_inputs:
                self.hotkey_inputs[k].setText(v)

    def save_and_apply(self):
        # Save display settings
        self.settings.set("display", "target_screen_index", self.screen_combo.currentData())
        self.settings.set("display", "output_mode", self.combo_out_mode.currentData())
        self.settings.set("display", "corner_width_px", self.spin_corner_w.value())
        self.settings.set("display", "fullscreen_on_launch", self.chk_fullscreen.isChecked())

        # Save media upload settings
        self.settings.set("background", "custom_media_path", self.custom_media_path)
        self.settings.set("background", "custom_media_type", self.custom_media_type)
        self.settings.set("background", "overlay_dim_percent", self.slider_dim.value())

        # Save typography
        self.settings.set("typography", "font_family", self.font_combo.currentFont().family())
        self.settings.set("typography", "font_size", self.spin_font_size.value())
        self.settings.set("typography", "reference_font_size", self.spin_ref_size.value())
        self.settings.set("typography", "text_alignment", self.align_combo.currentText())
        self.settings.set("typography", "outline_enabled", self.chk_outline.isChecked())
        self.settings.set("typography", "shadow_enabled", self.chk_shadow.isChecked())

        # Save hotkeys
        hotkeys_data = {}
        for k, line_edit in self.hotkey_inputs.items():
            val = line_edit.text().strip()
            if val:
                hotkeys_data[k] = val
        self.settings.set("hotkeys", hotkeys_data, None) if False else None
        if "hotkeys" not in self.settings.data:
            self.settings.data["hotkeys"] = {}
        self.settings.data["hotkeys"].update(hotkeys_data)

        self.settings.save()
        self.proj_win.apply_theme()
        self.proj_win.apply_geometry_mode()

        if self.parent_win:
            if hasattr(self.parent_win, "rebind_shortcuts"):
                self.parent_win.rebind_shortcuts()
            if hasattr(self.parent_win, "sync_pip_combo"):
                self.parent_win.sync_pip_combo()

        self.accept()


class ControlWindow(QMainWindow):
    """
    Main Operator Dashboard for BIBLETEXT Linux.
    Controls:
      - Rapid hotkey search ("Jn 3 16", "Gen 1:1-5", "Ps 23")
      - Live slide preview
      - Scripture database browser (OT / NT tabs, Chapter grid, Verse list)
      - Dual translation controls
      - Offline Bible loading & online Bible catalog installer
      - Quick actions: Go Live (Enter), Clear (Esc), Blackout (Ctrl+B), Logo (Ctrl+L), Preferences (Ctrl+T)
    """
    def __init__(self, db: BibleDatabase, settings_mgr: SettingsManager, projection_win: ProjectionWindow):
        super().__init__()
        self.db = db
        self.settings = settings_mgr
        self.proj_win = projection_win
        self.parser = BibleReferenceParser(self.db)

        self.current_book: Optional[Dict] = None
        self.current_chapter: int = 1
        self.current_verse: int = 1
        self.active_verses: List[Dict] = []
        self.selected_verse_data: Optional[Dict] = None

        self.setWindowTitle("BIBLETEXT Linux - Operator Control Console")
        self.resize(1180, 760)
        self.setStyleSheet(DARK_STYLESHEET)

        self._init_ui()
        self._init_shortcuts()
        self._load_translations()
        self._load_books("OT")

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # 1. TOP HEADER & QUICK SEARCH BAR
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        title_lbl = QLabel("📖 BIBLETEXT")
        title_lbl.setStyleSheet("font-weight: 900; color: #F59E0B; font-size: 15px; letter-spacing: 1px;")
        top_bar.addWidget(title_lbl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Instant verse search: 'Jn 3 16', 'Gen 1:1-5', 'Ps 23' [Ctrl+F]...")
        self.search_input.returnPressed.connect(self.on_search_enter)
        top_bar.addWidget(self.search_input, 2)

        # Primary Translation
        top_bar.addWidget(QLabel("Primary:"))
        self.combo_primary = QComboBox()
        self.combo_primary.currentIndexChanged.connect(self.on_translation_changed)
        top_bar.addWidget(self.combo_primary)

        # Parallel Translation Toggle
        self.chk_parallel = QCheckBox("Dual / Parallel:")
        self.chk_parallel.setChecked(self.settings.get("parallel", "enabled", False))
        self.chk_parallel.toggled.connect(self.on_parallel_toggled)
        top_bar.addWidget(self.chk_parallel)

        self.combo_secondary = QComboBox()
        self.combo_secondary.setEnabled(self.chk_parallel.isChecked())
        top_bar.addWidget(self.combo_secondary)

        # Screen Output & PIP Controller
        top_bar.addWidget(QLabel("Output / PIP:"))
        self.combo_pip_mode = QComboBox()
        self.combo_pip_mode.addItem("🔴 Off (Display Hidden)", "off")
        self.combo_pip_mode.addItem("↘ 16:9 Bottom-Right (PIP)", "bottom-right")
        self.combo_pip_mode.addItem("↙ 16:9 Bottom-Left (PIP)", "bottom-left")
        self.combo_pip_mode.addItem("↗ 16:9 Top-Right (PIP)", "top-right")
        self.combo_pip_mode.addItem("↖ 16:9 Top-Left (PIP)", "top-left")
        self.combo_pip_mode.addItem("🖥 Fullscreen Projector", "fullscreen")
        self.combo_pip_mode.addItem("🪟 Windowed Screen", "windowed")

        curr_mode = self.settings.get("display", "output_mode", "off")
        idx = self.combo_pip_mode.findData(curr_mode)
        if idx >= 0:
            self.combo_pip_mode.setCurrentIndex(idx)
        self.combo_pip_mode.currentIndexChanged.connect(self.on_pip_mode_changed)
        top_bar.addWidget(self.combo_pip_mode)

        # Preferences button
        self.btn_prefs = QPushButton("⚙ Settings (Ctrl+T)")
        self.btn_prefs.clicked.connect(self.open_preferences)
        top_bar.addWidget(self.btn_prefs)

        main_layout.addLayout(top_bar)

        # 2. MAIN BODY (Splitter: Left = Bible Browser, Right = Live Preview & Controls)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT PANE: Book & Verse Browser
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)

        tab_buttons = QHBoxLayout()
        self.btn_ot = QPushButton("Old Testament (39)")
        self.btn_nt = QPushButton("New Testament (27)")
        self.btn_ot.setCheckable(True)
        self.btn_nt.setCheckable(True)
        self.btn_ot.setChecked(True)

        self.testament_group = QButtonGroup(self)
        self.testament_group.addButton(self.btn_ot)
        self.testament_group.addButton(self.btn_nt)
        self.btn_ot.clicked.connect(lambda: self._load_books("OT"))
        self.btn_nt.clicked.connect(lambda: self._load_books("NT"))

        tab_buttons.addWidget(self.btn_ot)
        tab_buttons.addWidget(self.btn_nt)
        browser_layout.addLayout(tab_buttons)

        book_verse_split = QSplitter(Qt.Orientation.Horizontal)

        self.book_list = QListWidget()
        self.book_list.itemClicked.connect(self.on_book_selected)
        book_verse_split.addWidget(self.book_list)

        cv_container = QWidget()
        cv_layout = QVBoxLayout(cv_container)
        cv_layout.setContentsMargins(0, 0, 0, 0)

        cv_header = QHBoxLayout()
        cv_header.addWidget(QLabel("Chapters:"))
        cv_header.addWidget(QLabel("Verses:"))
        cv_layout.addLayout(cv_header)

        cv_lists_layout = QHBoxLayout()
        self.chapter_list = QListWidget()
        self.chapter_list.setMaximumWidth(80)
        self.chapter_list.itemClicked.connect(self.on_chapter_selected)

        self.verse_list = QListWidget()
        self.verse_list.itemClicked.connect(self.on_verse_selected)
        self.verse_list.itemDoubleClicked.connect(self.go_live)

        cv_lists_layout.addWidget(self.chapter_list)
        cv_lists_layout.addWidget(self.verse_list)
        cv_layout.addLayout(cv_lists_layout)

        book_verse_split.addWidget(cv_container)
        book_verse_split.setSizes([180, 320])
        browser_layout.addWidget(book_verse_split)

        splitter.addWidget(browser_widget)

        # RIGHT PANE: Live Slide Preview & Quick Action Bar
        preview_panel = QWidget()
        p_layout = QVBoxLayout(preview_panel)
        p_layout.setContentsMargins(6, 0, 0, 0)

        preview_header = QHBoxLayout()
        preview_header.addWidget(QLabel("🖥 LIVE PROJECTOR PREVIEW MONITOR"))
        self.lbl_active_status = QLabel("● IDLE")
        self.lbl_active_status.setStyleSheet("color: #94A3B8; font-weight: bold;")
        preview_header.addStretch()
        preview_header.addWidget(self.lbl_active_status)
        p_layout.addLayout(preview_header)

        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet("background-color: #030712; border: 2px solid #334155; border-radius: 8px;")
        pf_layout = QVBoxLayout(self.preview_frame)
        pf_layout.setContentsMargins(8, 8, 8, 8)

        self.preview_canvas = ScriptureRenderCanvas(self.settings, self.preview_frame)
        pf_layout.addWidget(self.preview_canvas)
        p_layout.addWidget(self.preview_frame, 3)

        self.lbl_staged_ref = QLabel("Staged: No verse selected")
        self.lbl_staged_ref.setStyleSheet("font-size: 16px; font-weight: bold; color: #F59E0B;")
        p_layout.addWidget(self.lbl_staged_ref)

        self.lbl_staged_text = QLabel("Use the search bar or book list to select scriptures.")
        self.lbl_staged_text.setWordWrap(True)
        self.lbl_staged_text.setStyleSheet("color: #CBD5E1; font-size: 14px; padding: 4px 0;")
        p_layout.addWidget(self.lbl_staged_text, 1)

        action_bar = QGridLayout()
        action_bar.setSpacing(8)

        self.btn_live = QPushButton("▶ GO LIVE (Enter)")
        self.btn_live.setObjectName("btnGoLive")
        self.btn_live.setFixedHeight(44)
        self.btn_live.clicked.connect(self.go_live)
        action_bar.addWidget(self.btn_live, 0, 0, 1, 2)

        self.btn_clear = QPushButton("Clear Text (Esc)")
        self.btn_clear.clicked.connect(self.clear_text)
        action_bar.addWidget(self.btn_clear, 1, 0)

        self.btn_blackout = QPushButton("Blackout (Ctrl+B)")
        self.btn_blackout.setObjectName("btnBlackout")
        self.btn_blackout.clicked.connect(self.toggle_blackout)
        action_bar.addWidget(self.btn_blackout, 1, 1)

        self.btn_logo = QPushButton("Logo / Hold Screen (Ctrl+L)")
        self.btn_logo.clicked.connect(self.show_logo)
        action_bar.addWidget(self.btn_logo, 2, 0)

        self.btn_fullscreen = QPushButton("Toggle Output Mode (F5)")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen_output)
        action_bar.addWidget(self.btn_fullscreen, 2, 1)

        p_layout.addLayout(action_bar)
        splitter.addWidget(preview_panel)
        splitter.setSizes([520, 560])

        main_layout.addWidget(splitter)
        self.statusBar().showMessage("Ready. Press Enter to push selected verse to projection.")

    def focus_search(self):
        """Focuses the scripture search bar and highlights text for rapid input (Ctrl+F)."""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def on_pip_mode_changed(self, index: int):
        """Called when the user selects a PIP or display output mode from the top bar dropdown."""
        mode = self.combo_pip_mode.currentData() or "off"
        self.proj_win.set_pip_mode(mode)
        self.statusBar().showMessage(f"Screen output mode: {self.combo_pip_mode.currentText()}")

    def sync_pip_combo(self):
        """Synchronizes top bar dropdown with settings display output mode."""
        curr = self.settings.get("display", "output_mode", "off")
        idx = self.combo_pip_mode.findData(curr)
        if idx >= 0:
            self.combo_pip_mode.blockSignals(True)
            self.combo_pip_mode.setCurrentIndex(idx)
            self.combo_pip_mode.blockSignals(False)

    def cycle_pip_mode(self):
        """Cycles PIP modes: off -> bottom-right -> bottom-left -> fullscreen -> off."""
        modes = ["off", "bottom-right", "bottom-left", "fullscreen"]
        curr = self.settings.get("display", "output_mode", "off")
        next_mode = modes[(modes.index(curr) + 1) % len(modes)] if curr in modes else "bottom-right"
        self.proj_win.set_pip_mode(next_mode)
        self.sync_pip_combo()
        self.statusBar().showMessage(f"Toggled PIP output: {next_mode}")

    def rebind_shortcuts(self):
        """Dynamically binds and updates keyboard shortcuts from user settings."""
        if hasattr(self, "_active_shortcuts"):
            for sc in self._active_shortcuts:
                sc.setEnabled(False)
                sc.deleteLater()
        self._active_shortcuts = []

        hk = self.settings.data.get("hotkeys", {})

        def bind(key_str, callback):
            if key_str:
                try:
                    sc = QShortcut(QKeySequence(key_str), self, callback)
                    self._active_shortcuts.append(sc)
                except Exception as e:
                    print(f"Error binding key {key_str}: {e}")

        # Bind customizable shortcuts
        bind(hk.get("search", "Ctrl+F"), self.focus_search)
        bind(hk.get("go_live", "Return"), self.go_live)
        bind("Enter", self.go_live)
        bind(hk.get("clear", "Escape"), self.clear_text)
        bind("F12", self.clear_text)
        bind(hk.get("blackout", "Ctrl+B"), self.toggle_blackout)
        bind(hk.get("logo", "Ctrl+L"), self.show_logo)
        bind(hk.get("fullscreen", "F5"), self.toggle_fullscreen_output)
        bind("Ctrl+P", self.toggle_fullscreen_output)
        bind(hk.get("settings", "Ctrl+T"), self.open_preferences)
        bind(hk.get("next_verse", "Down"), self.nav_next_verse)
        bind(hk.get("prev_verse", "Up"), self.nav_prev_verse)
        bind(hk.get("next_chapter", "Right"), self.nav_next_chapter)
        bind(hk.get("prev_chapter", "Left"), self.nav_prev_chapter)
        bind(hk.get("toggle_pip", "Ctrl+M"), self.cycle_pip_mode)

    def _init_shortcuts(self):
        self._active_shortcuts = []
        self.rebind_shortcuts()

    def _load_translations(self):
        translations = self.db.get_translations()
        self.combo_primary.clear()
        self.combo_secondary.clear()
        for t in translations:
            self.combo_primary.addItem(f"{t['name']} ({t['abbreviation']})", t['id'])
            self.combo_secondary.addItem(f"{t['name']} ({t['abbreviation']})", t['id'])

        p_id = self.settings.get("parallel", "primary_translation", "KJV")
        s_id = self.settings.get("parallel", "secondary_translation", "WEB")

        p_idx = self.combo_primary.findData(p_id)
        if p_idx >= 0:
            self.combo_primary.setCurrentIndex(p_idx)

        s_idx = self.combo_secondary.findData(s_id)
        if s_idx >= 0:
            self.combo_secondary.setCurrentIndex(s_idx)

    def _load_books(self, testament: str):
        self.book_list.clear()
        books = self.db.get_books(testament)
        for b in books:
            item = QListWidgetItem(b['name'])
            item.setData(Qt.ItemDataRole.UserRole, b)
            self.book_list.addItem(item)

        if self.book_list.count() > 0:
            self.book_list.setCurrentRow(0)
            self.on_book_selected(self.book_list.item(0))

    def on_book_selected(self, item: QListWidgetItem):
        book = item.data(Qt.ItemDataRole.UserRole)
        self.current_book = book
        self.chapter_list.clear()
        for c in range(1, book['chapter_count'] + 1):
            c_item = QListWidgetItem(f"Ch. {c}")
            c_item.setData(Qt.ItemDataRole.UserRole, c)
            self.chapter_list.addItem(c_item)

        self.chapter_list.setCurrentRow(0)
        self.on_chapter_selected(self.chapter_list.item(0))

    def on_chapter_selected(self, item: QListWidgetItem):
        if not item:
            return
        chap = item.data(Qt.ItemDataRole.UserRole)
        self.current_chapter = chap
        self._refresh_verses()

    def _refresh_verses(self):
        if not self.current_book:
            return

        t_id = self.combo_primary.currentData() or "KJV"
        self.active_verses = self.db.get_verses(t_id, self.current_book['id'], self.current_chapter)

        self.verse_list.clear()
        for v in self.active_verses:
            v_item = QListWidgetItem(f"v{v['verse']} - {v['text']}")
            v_item.setData(Qt.ItemDataRole.UserRole, v)
            self.verse_list.addItem(v_item)

        if self.verse_list.count() > 0:
            self.verse_list.setCurrentRow(0)
            self.on_verse_selected(self.verse_list.item(0))

    def on_verse_selected(self, item: QListWidgetItem):
        if not item:
            return
        verse = item.data(Qt.ItemDataRole.UserRole)
        self.selected_verse_data = verse
        self.current_verse = verse['verse']

        ref_str = f"{self.current_book['name']} {self.current_chapter}:{verse['verse']}"
        self.lbl_staged_ref.setText(f"Staged: {ref_str}")
        self.lbl_staged_text.setText(verse['text'])

        secondary_text = ""
        if self.chk_parallel.isChecked():
            sec_tid = self.combo_secondary.currentData()
            sec_verses = self.db.get_verses(sec_tid, self.current_book['id'], self.current_chapter, verse['verse'], verse['verse'])
            if sec_verses:
                secondary_text = sec_verses[0]['text']

        self.preview_canvas.set_content(ref_str, verse['text'], secondary_text)

    def on_search_enter(self):
        text = self.search_input.text().strip()
        parsed = self.parser.parse(text)
        if not parsed:
            self.statusBar().showMessage(f"Could not parse '{text}'. Try e.g. 'Jn 3 16' or 'Gen 1:1-5'")
            return

        book = parsed['book']
        chap = parsed['chapter']
        start_v = parsed['start_verse'] or 1

        testament = book['testament']
        if testament == "OT" and not self.btn_ot.isChecked():
            self.btn_ot.setChecked(True)
            self._load_books("OT")
        elif testament == "NT" and not self.btn_nt.isChecked():
            self.btn_nt.setChecked(True)
            self._load_books("NT")

        for idx in range(self.book_list.count()):
            b = self.book_list.item(idx).data(Qt.ItemDataRole.UserRole)
            if b['id'] == book['id']:
                self.book_list.setCurrentRow(idx)
                self.on_book_selected(self.book_list.item(idx))
                break

        if chap <= self.chapter_list.count():
            self.chapter_list.setCurrentRow(chap - 1)
            self.on_chapter_selected(self.chapter_list.item(chap - 1))

        for v_idx in range(self.verse_list.count()):
            v = self.verse_list.item(v_idx).data(Qt.ItemDataRole.UserRole)
            if v['verse'] == start_v:
                self.verse_list.setCurrentRow(v_idx)
                self.on_verse_selected(self.verse_list.item(v_idx))
                break

        self.go_live()
        self.search_input.clear()

    def go_live(self):
        if not self.selected_verse_data or not self.current_book:
            return

        ref_str = f"{self.current_book['name']} {self.current_chapter}:{self.selected_verse_data['verse']}"
        primary_text = self.selected_verse_data['text']

        secondary_text = ""
        if self.chk_parallel.isChecked():
            sec_tid = self.combo_secondary.currentData()
            sec_verses = self.db.get_verses(sec_tid, self.current_book['id'], self.current_chapter,
                                            self.selected_verse_data['verse'], self.selected_verse_data['verse'])
            if sec_verses:
                secondary_text = sec_verses[0]['text']

        self.proj_win.show_verse(ref_str, primary_text, secondary_text)
        self.lbl_active_status.setText(f"● LIVE: {ref_str}")
        self.lbl_active_status.setStyleSheet("color: #22C55E; font-weight: bold;")
        self.statusBar().showMessage(f"Projecting live: {ref_str}")

    def clear_text(self):
        self.proj_win.clear_text()
        self.preview_canvas.clear_content()
        self.lbl_active_status.setText("● TEXT CLEARED")
        self.lbl_active_status.setStyleSheet("color: #F59E0B; font-weight: bold;")

    def toggle_blackout(self):
        self.proj_win.toggle_blackout()
        if self.proj_win.is_blackout:
            self.lbl_active_status.setText("● BLACKOUT ACTIVE")
            self.lbl_active_status.setStyleSheet("color: #EF4444; font-weight: bold;")
        else:
            self.lbl_active_status.setText("● LIVE")
            self.lbl_active_status.setStyleSheet("color: #22C55E; font-weight: bold;")

    def show_logo(self):
        self.proj_win.show_logo()
        self.preview_canvas.set_content("", "", is_logo=True)
        self.lbl_active_status.setText("● LOGO / HOLD SCREEN")
        self.lbl_active_status.setStyleSheet("color: #38BDF8; font-weight: bold;")

    def toggle_fullscreen_output(self):
        curr = self.settings.get("display", "output_mode", "off")
        if curr == "fullscreen":
            self.proj_win.set_pip_mode("bottom-right")
        else:
            self.proj_win.set_pip_mode("fullscreen")
        self.sync_pip_combo()

    def nav_next_verse(self):
        curr = self.verse_list.currentRow()
        if curr + 1 < self.verse_list.count():
            self.verse_list.setCurrentRow(curr + 1)
            self.on_verse_selected(self.verse_list.item(curr + 1))
            self.go_live()

    def nav_prev_verse(self):
        curr = self.verse_list.currentRow()
        if curr - 1 >= 0:
            self.verse_list.setCurrentRow(curr - 1)
            self.on_verse_selected(self.verse_list.item(curr - 1))
            self.go_live()

    def nav_next_chapter(self):
        curr = self.chapter_list.currentRow()
        if curr + 1 < self.chapter_list.count():
            self.chapter_list.setCurrentRow(curr + 1)
            self.on_chapter_selected(self.chapter_list.item(curr + 1))
            self.go_live()

    def nav_prev_chapter(self):
        curr = self.chapter_list.currentRow()
        if curr - 1 >= 0:
            self.chapter_list.setCurrentRow(curr - 1)
            self.on_chapter_selected(self.chapter_list.item(curr - 1))
            self.go_live()

    def on_translation_changed(self):
        self._refresh_verses()

    def on_parallel_toggled(self, checked: bool):
        self.combo_secondary.setEnabled(checked)
        self.settings.set("parallel", "enabled", checked)
        self.settings.save()
        if self.verse_list.currentItem():
            self.on_verse_selected(self.verse_list.currentItem())

    def open_preferences(self):
        dlg = PreferencesDialog(self.db, self.settings, self.proj_win, self)
        dlg.exec()
        self._load_translations()
        if self.verse_list.currentItem():
            self.on_verse_selected(self.verse_list.currentItem())
