import sys
import os
from typing import Optional, Dict

try:
    from PyQt6.QtWidgets import (
        QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect,
        QStackedLayout, QFrame, QApplication
    )
    from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QUrl, QRect
    from PyQt6.QtGui import (
        QFont, QColor, QPainter, QPainterPath, QPen, QBrush, QPixmap, QLinearGradient
    )
    try:
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PyQt6.QtMultimediaWidgets import QVideoWidget
        HAS_MULTIMEDIA = True
    except ImportError:
        HAS_MULTIMEDIA = False
except ImportError:
    from PySide6.QtWidgets import (
        QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect,
        QStackedLayout, QFrame, QApplication
    )
    from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QUrl, QRect
    from PySide6.QtGui import (
        QFont, QColor, QPainter, QPainterPath, QPen, QBrush, QPixmap, QLinearGradient
    )
    try:
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PySide6.QtMultimediaWidgets import QVideoWidget
        HAS_MULTIMEDIA = True
    except ImportError:
        HAS_MULTIMEDIA = False

from settings import SettingsManager

class ScriptureRenderCanvas(QWidget):
    """
    High-performance QPainter canvas for rendering anti-aliased scripture
    with sharp outline strokes, drop shadows, and lower-third banners.
    Guarantees 100% legibility over any bright or moving video background.
    """
    def __init__(self, settings_mgr: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings = settings_mgr
        self.reference = ""
        self.primary_text = ""
        self.secondary_text = ""
        self.is_blank = False
        self.is_logo = False
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_content(self, reference: str, primary_text: str, secondary_text: str = "", is_logo: bool = False):
        self.reference = reference
        self.primary_text = primary_text
        self.secondary_text = secondary_text
        self.is_logo = is_logo
        self.is_blank = False
        self.update()

    def clear_content(self):
        self.is_blank = True
        self.update()

    def paintEvent(self, event):
        if self.is_blank:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()

        typo = self.settings.data.get("typography", {})
        bg_cfg = self.settings.data.get("background", {})
        parallel_cfg = self.settings.data.get("parallel", {})

        # Dark overlay dimming over background media
        dim_pct = bg_cfg.get("overlay_dim_percent", 35)
        if dim_pct > 0:
            overlay_alpha = int(255 * (dim_pct / 100.0))
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0, overlay_alpha))

        # Check logo mode
        if self.is_logo:
            self._render_logo_mode(painter, w, h)
            return

        if not self.primary_text and not self.reference:
            return

        alignment_mode = typo.get("text_alignment", "Center")
        font_family = typo.get("font_family", "DejaVu Sans")
        scale_factor = min(w / 1280.0, h / 720.0)
        base_font_size = max(14, int(typo.get("font_size", 42) * scale_factor))
        ref_size = max(12, int(typo.get("reference_font_size", 28) * scale_factor))
        font_weight = QFont.Weight.Bold if typo.get("font_weight", "Bold") == "Bold" else QFont.Weight.Normal

        text_color = QColor(typo.get("text_color", "#FFFFFF"))
        ref_color = QColor(typo.get("reference_color", "#FFD700"))
        outline_enabled = typo.get("outline_enabled", True)
        outline_color = QColor(typo.get("outline_color", "#000000"))
        shadow_enabled = typo.get("shadow_enabled", True)

        if alignment_mode == "LowerThird":
            self._render_lower_third(painter, w, h, font_family, base_font_size, ref_size, text_color, ref_color)
            return

        # Standard layout
        margin_x = int(w * 0.08)
        margin_y = int(h * 0.08)
        content_rect = QRect(margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

        ref_font = QFont(font_family, ref_size, QFont.Weight.DemiBold)
        verse_font = QFont(font_family, base_font_size, font_weight)

        painter.setFont(ref_font)
        ref_h = max(24, int(36 * scale_factor))

        align_flags = Qt.AlignmentFlag.TextWordWrap | (
            Qt.AlignmentFlag.AlignCenter if alignment_mode == "Center"
            else Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        full_display_text = self.primary_text
        if parallel_cfg.get("enabled", False) and self.secondary_text:
            if parallel_cfg.get("layout", "stacked") == "stacked":
                full_display_text = f"{self.primary_text}\n\n[{parallel_cfg.get('secondary_translation', 'WEB')}] {self.secondary_text}"
            else:
                full_display_text = f"{self.primary_text}   |   {self.secondary_text}"

        verse_rect = QRect(content_rect.x(), content_rect.y() + ref_h + 10,
                           content_rect.width(), content_rect.height() - ref_h - 10)

        # Draw drop shadow
        if shadow_enabled:
            painter.setFont(verse_font)
            painter.setPen(QColor(0, 0, 0, 220))
            offset_rect = QRect(verse_rect.x() + 3, verse_rect.y() + 3, verse_rect.width(), verse_rect.height())
            painter.drawText(offset_rect, align_flags, full_display_text)

        # Draw outline stroke
        if outline_enabled:
            painter.setFont(verse_font)
            painter.setPen(outline_color)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                p_rect = QRect(verse_rect.x() + dx, verse_rect.y() + dy, verse_rect.width(), verse_rect.height())
                painter.drawText(p_rect, align_flags, full_display_text)

        # Main text
        painter.setFont(verse_font)
        painter.setPen(text_color)
        painter.drawText(verse_rect, align_flags, full_display_text)

        # Reference Pill
        painter.setFont(ref_font)
        if shadow_enabled:
            painter.setPen(QColor(0, 0, 0, 220))
            painter.drawText(content_rect.x() + 2, content_rect.y() + 2, content_rect.width(), ref_h,
                             Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.reference)
        painter.setPen(ref_color)
        painter.drawText(content_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.reference)

    def _render_lower_third(self, painter: QPainter, w: int, h: int, font_family: str, font_size: int,
                            ref_size: int, text_color: QColor, ref_color: QColor):
        banner_h = int(h * 0.30)
        banner_y = h - banner_h - int(h * 0.05)
        banner_x = int(w * 0.05)
        banner_w = int(w * 0.90)

        gradient = QLinearGradient(banner_x, banner_y, banner_x + banner_w, banner_y)
        gradient.setColorAt(0.0, QColor(10, 15, 25, 240))
        gradient.setColorAt(0.5, QColor(15, 23, 42, 230))
        gradient.setColorAt(1.0, QColor(10, 15, 25, 240))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(234, 179, 8, 200), 2))
        painter.drawRoundedRect(banner_x, banner_y, banner_w, banner_h, 12, 12)

        ref_badge_rect = QRect(banner_x + 20, banner_y + 12, banner_w - 40, int(ref_size * 1.5))
        painter.setFont(QFont(font_family, int(ref_size * 0.9), QFont.Weight.Bold))
        painter.setPen(ref_color)
        painter.drawText(ref_badge_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"📖 {self.reference}")

        text_rect = QRect(banner_x + 20, banner_y + int(ref_size * 1.6) + 6, banner_w - 40, banner_h - int(ref_size * 1.8))
        painter.setFont(QFont(font_family, int(font_size * 0.8), QFont.Weight.DemiBold))
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self.primary_text)

    def _render_logo_mode(self, painter: QPainter, w: int, h: int):
        pres = self.settings.data.get("presentation", {})
        title = pres.get("logo_text", "THE HOLY BIBLE")
        subtext = pres.get("logo_subtext", "Thy word is a lamp unto my feet, and a light unto my path.")
        scale = min(w / 1280.0, h / 720.0)

        painter.setFont(QFont("Cinzel", max(20, int(54 * scale)), QFont.Weight.Bold))
        painter.setPen(QColor("#FFD700"))
        painter.drawText(QRect(0, h // 2 - int(80 * scale), w, int(80 * scale)), Qt.AlignmentFlag.AlignCenter, title)

        painter.setFont(QFont("DejaVu Sans", max(12, int(22 * scale)), QFont.Weight.Normal))
        painter.setPen(QColor("#E2E8F0"))
        painter.drawText(QRect(int(w * 0.12), h // 2 + int(10 * scale), int(w * 0.76), int(100 * scale)),
                         Qt.AlignmentFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter, subtext)


class ProjectionWindow(QWidget):
    """
    Projection window for BIBLETEXT Linux.
    Supports:
      - Fullscreen external monitor
      - Floating 16:9 Widescreen Corner Output:
          * Bottom-Right Corner
          * Bottom-Left Corner
          * Top-Right / Top-Left Corner
      - Custom uploaded background pictures (.jpg, .png, .webp)
      - Custom uploaded background videos (.mp4, .webm)
    """
    def __init__(self, settings_mgr: SettingsManager):
        super().__init__()
        self.settings = settings_mgr
        self.is_blackout = False

        self.setWindowTitle("BIBLETEXT Output Screen")
        self._setup_window_flags()
        self._init_ui()

    def _setup_window_flags(self):
        mode = self.settings.get("display", "output_mode", "fullscreen")
        if mode in ("bottom-right", "bottom-left", "top-right", "top-left"):
            # Floating Picture-in-Picture mode on top
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
        else:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Window
            )

    def _init_ui(self):
        self.layout_stack = QStackedLayout(self)
        self.layout_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.layout_stack.addWidget(self.bg_label)

        self.video_widget = None
        self.media_player = None
        if HAS_MULTIMEDIA:
            self.video_widget = QVideoWidget(self)
            self.media_player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.audio_output.setMuted(True)
            self.media_player.setAudioOutput(self.audio_output)
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.setLoops(QMediaPlayer.Infinite)
            self.layout_stack.addWidget(self.video_widget)
            self.video_widget.hide()

        self.canvas = ScriptureRenderCanvas(self.settings, self)
        self.canvas_opacity = QGraphicsOpacityEffect(self.canvas)
        self.canvas.setGraphicsEffect(self.canvas_opacity)
        self.layout_stack.addWidget(self.canvas)

        self.blackout_overlay = QFrame(self)
        self.blackout_overlay.setStyleSheet("background-color: #000000;")
        self.blackout_overlay.hide()
        self.layout_stack.addWidget(self.blackout_overlay)

        self.anim = QPropertyAnimation(self.canvas_opacity, b"opacity")
        self.anim.setDuration(self.settings.get("presentation", "transition_duration_ms", 300))
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.apply_theme()
        if self.settings.get("display", "launch_output_on_start", False):
            self.apply_geometry_mode()
        else:
            self.hide()

    def set_pip_mode(self, mode: str):
        """Sets the screen output / PIP mode dynamically."""
        self.settings.set("display", "output_mode", mode)
        self.settings.save()
        self.apply_geometry_mode()

    def apply_geometry_mode(self):
        """
        Positions window based on monitor & display settings:
        Supports Off (Hidden), Fullscreen, or 16:9 widescreen corner placement (bottom-right, bottom-left, etc.).
        """
        mode = self.settings.get("display", "output_mode", "off")

        if mode == "off":
            self.hide()
            return

        # Setup correct window flags depending on corner vs windowed/fullscreen
        if mode in ("bottom-right", "bottom-left", "top-right", "top-left"):
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
        else:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Window
            )

        target_idx = self.settings.get("display", "target_screen_index", 1)
        screens = QApplication.screens()

        screen = screens[target_idx] if target_idx < len(screens) else screens[0]
        s_geom = screen.geometry()

        # 16:9 Widescreen Dimensions for corner modes
        corner_w = self.settings.get("display", "corner_width_px", 480)
        corner_h = int(corner_w * 9 / 16)  # Precise 16:9 ratio
        margin = self.settings.get("display", "corner_margin_px", 24)

        if mode == "bottom-right":
            self.resize(corner_w, corner_h)
            pos_x = s_geom.right() - corner_w - margin
            pos_y = s_geom.bottom() - corner_h - margin
            self.move(pos_x, pos_y)
            self.show()

        elif mode == "bottom-left":
            self.resize(corner_w, corner_h)
            pos_x = s_geom.left() + margin
            pos_y = s_geom.bottom() - corner_h - margin
            self.move(pos_x, pos_y)
            self.show()

        elif mode == "top-right":
            self.resize(corner_w, corner_h)
            pos_x = s_geom.right() - corner_w - margin
            pos_y = s_geom.top() + margin
            self.move(pos_x, pos_y)
            self.show()

        elif mode == "top-left":
            self.resize(corner_w, corner_h)
            pos_x = s_geom.left() + margin
            pos_y = s_geom.top() + margin
            self.move(pos_x, pos_y)
            self.show()

        elif mode == "fullscreen":
            self.move(s_geom.left(), s_geom.top())
            self.resize(s_geom.width(), s_geom.height())
            self.showFullScreen()
        else:
            self.resize(960, 540)
            self.move(s_geom.left() + 80, s_geom.top() + 80)
            self.show()

    def apply_theme(self):
        """Applies solid color, image, video, or user-uploaded background media."""
        bg_cfg = self.settings.data.get("background", {})
        bg_type = bg_cfg.get("type", "solid")
        custom_path = bg_cfg.get("custom_media_path", "")
        custom_type = bg_cfg.get("custom_media_type", "none")

        # 1. Custom uploaded media takes priority if set
        if custom_path and os.path.exists(custom_path):
            if custom_type == "video" or custom_path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm')):
                if HAS_MULTIMEDIA:
                    self.video_widget.show()
                    self.media_player.setSource(QUrl.fromLocalFile(custom_path))
                    self.media_player.play()
                    self.canvas.update()
                    return
            else:
                pixmap = QPixmap(custom_path)
                self.bg_label.setPixmap(pixmap)
                if self.video_widget:
                    self.video_widget.hide()
                    if self.media_player:
                        self.media_player.stop()
                self.canvas.update()
                return

        # 2. Standard background settings
        if bg_type == "video" and HAS_MULTIMEDIA and bg_cfg.get("video_path"):
            v_path = bg_cfg.get("video_path")
            self.video_widget.show()
            self.media_player.setSource(QUrl.fromLocalFile(v_path))
            self.media_player.play()
        else:
            if self.video_widget:
                self.video_widget.hide()
                if self.media_player:
                    self.media_player.stop()

            if bg_type == "image" and bg_cfg.get("image_path"):
                pixmap = QPixmap(bg_cfg.get("image_path"))
                self.bg_label.setPixmap(pixmap)
            else:
                solid = bg_cfg.get("solid_color", "#0B0F19")
                self.bg_label.setStyleSheet(f"background-color: {solid};")

        self.canvas.update()

    def show_verse(self, reference: str, primary_text: str, secondary_text: str = ""):
        self.blackout_overlay.hide()
        self.is_blackout = False

        duration = self.settings.get("presentation", "transition_duration_ms", 250)
        self.anim.stop()
        self.anim.setDuration(duration // 2)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.15)

        def on_fade_out_finished():
            self.anim.finished.disconnect()
            self.canvas.set_content(reference, primary_text, secondary_text, is_logo=False)
            self.anim.setStartValue(0.15)
            self.anim.setEndValue(1.0)
            self.anim.start()

        self.anim.finished.connect(on_fade_out_finished)
        self.anim.start()

    def show_logo(self):
        self.blackout_overlay.hide()
        self.is_blackout = False
        self.canvas.set_content("", "", is_logo=True)

    def clear_text(self):
        self.canvas.clear_content()

    def toggle_blackout(self):
        self.is_blackout = not self.is_blackout
        if self.is_blackout:
            self.blackout_overlay.show()
        else:
            self.blackout_overlay.hide()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_F12):
            self.toggle_blackout()
        elif event.key() == Qt.Key.Key_F5:
            if self.isFullScreen():
                self.apply_geometry_mode()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)
