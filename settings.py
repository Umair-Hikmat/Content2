"""
Persistent Application Settings Manager storing user preferences in JSON format.
"""

import json
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field

from config import config
from logger import logger


class UserPreferences(BaseModel):
    theme: str = "Cyberpunk Dark"
    default_resolution: str = "9:16 Vertical (Shorts/TikTok/Reels)"
    default_fps: int = 30
    default_quality: str = "High Quality"
    default_tts_provider: str = "Edge TTS"
    default_voice_speed: float = 1.0
    default_voice_pitch: float = 1.0
    enable_hardware_acceleration: bool = True
    max_concurrent_jobs: int = 2
    auto_save_interval: int = 30
    custom_ffmpeg_args: str = ""


class SettingsManager:
    """Manages reading, writing, and applying system-wide preferences."""

    def __init__(self, settings_file: Optional[Path] = None):
        self.settings_file = settings_file or (config.paths.base_dir / "user_settings.json")
        self.preferences = UserPreferences()
        self.load_settings()

    def load_settings(self) -> None:
        """Loads user preferences from disk."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.preferences = UserPreferences(**data)
                    logger.info("Successfully loaded user preferences.")
            except Exception as e:
                logger.error(f"Error loading user settings, reverting to defaults: {e}")
                self.save_settings()
        else:
            self.save_settings()

    def save_settings(self) -> bool:
        """Persists current user preferences to disk."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.preferences.model_dump(), f, indent=4)
            logger.info("User preferences saved to disk.")
            return True
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False

    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Updates preferences with a partial dictionary and saves."""
        current_data = self.preferences.model_dump()
        current_data.update(new_settings)
        self.preferences = UserPreferences(**current_data)
        return self.save_settings()


# Global Settings Manager Singleton
settings_manager = SettingsManager()
