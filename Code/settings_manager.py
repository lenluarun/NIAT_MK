"""
Persistent runtime settings for UI/camera behavior.
"""
import json
import os


SETTINGS_FILE = "app_settings.json"
DEFAULT_SETTINGS = {
    "camera_index": 0,
    "camera_scan_range": 5,
    "max_capture_samples": 120,
    "recognition_pass_mark": 67,
    "ui_theme": "metasploit",
    "boot_animation": True,
    "hud_mode": True
}


def load_settings():
    """Load settings from disk with safe defaults."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        save_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()

    merged = DEFAULT_SETTINGS.copy()
    merged.update(data if isinstance(data, dict) else {})
    return merged


def save_settings(settings):
    """Save settings to disk."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def update_setting(key, value):
    """Update single setting key."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings
