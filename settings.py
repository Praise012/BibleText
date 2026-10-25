import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_SETTINGS = {
    "display": {
        "target_screen_index": 1,
        "launch_output_on_start": False,  # Secondary output screen does NOT automatically launch on app open
        "output_mode": "off",  # "off", "bottom-right", "bottom-left", "top-right", "top-left", "fullscreen", "windowed"
        "corner_width_px": 480,       # 16:9 Widescreen (480x270 or 576x324)
        "corner_margin_px": 24,
        "keep_aspect_ratio": True,
        "aspect_ratio": "16:9",
        "hide_cursor": True
    },
    "hotkeys": {
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
    },
    "typography": {
        "font_family": "DejaVu Sans",
        "font_size": 42,
        "font_weight": "Bold",  # "Normal", "Bold", "Black"
        "text_color": "#FFFFFF",
        "reference_color": "#FFD700",  # Golden yellow
        "reference_font_size": 28,
        "shadow_enabled": True,
        "shadow_color": "#000000",
        "shadow_blur": 12,
        "outline_enabled": True,
        "outline_color": "#000000",
        "outline_width": 3,
        "line_spacing": 1.3,
        "text_alignment": "Center",  # "Top", "Center", "Bottom", "LowerThird"
        "max_words_per_slide": 45
    },
    "background": {
        "type": "solid",  # "solid", "image", "video"
        "solid_color": "#0D1117",
        "image_path": "",
        "video_path": "",
        "custom_media_path": "",
        "custom_media_type": "none",  # "image", "video", "none"
        "overlay_dim_percent": 35,  # 0 to 100%
        "overlay_color": "#000000"
    },
    "parallel": {
        "enabled": False,
        "primary_translation": "KJV",
        "secondary_translation": "WEB",
        "layout": "stacked",  # "stacked", "columns"
        "secondary_font_size": 32,
        "secondary_color": "#94A3B8"
    },
    "presentation": {
        "transition_duration_ms": 350,
        "transition_effect": "fade",
        "logo_text": "THE HOLY BIBLE",
        "logo_subtext": "Thy word is a lamp unto my feet, and a light unto my path.",
        "logo_image_path": ""
    }
}

class SettingsManager:
    """Manages reading and writing application configurations from ~/.config/bibletext/settings.json"""
    def __init__(self, config_path: str = None):
        if config_path:
            self.filepath = Path(config_path)
        else:
            base_dir = Path.home() / ".config" / "bibletext"
            base_dir.mkdir(parents=True, exist_ok=True)
            self.filepath = base_dir / "settings.json"

        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Loads configuration from JSON file or populates with defaults."""
        if not self.filepath.exists():
            legacy_file = Path.home() / ".config" / "bibleshow" / "settings.json"
            if legacy_file.exists():
                try:
                    with open(legacy_file, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                    self.data = self._deep_merge(DEFAULT_SETTINGS, loaded)
                    self.save()
                    return
                except Exception:
                    pass

            self.data = DEFAULT_SETTINGS.copy()
            self.save()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.data = self._deep_merge(DEFAULT_SETTINGS, loaded)
        except Exception as e:
            print(f"[BIBLETEXT Settings] Warning loading settings: {e}. Using defaults.")
            self.data = DEFAULT_SETTINGS.copy()

    def save(self):
        """Writes current settings back to JSON file safely."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[BIBLETEXT Settings] Failed to save settings: {e}")

    def get(self, section: str, key: str, fallback=None):
        return self.data.get(section, {}).get(key, fallback)

    def set(self, section: str, key: str, value: Any):
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = value

    def _deep_merge(self, default_dict: dict, user_dict: dict) -> dict:
        result = default_dict.copy()
        for k, v in user_dict.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._deep_merge(result[k], v)
            else:
                result[k] = v
        return result
