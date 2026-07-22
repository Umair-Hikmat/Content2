"""
Audio Engine and Background Music Manager.
Handles background music, sound effects (SFX), track looping, trimming, and volume normalization.
"""

from pathlib import Path
from typing import List, Dict, Optional
from pydub import AudioSegment

from config import config
from cache import cache_manager
from logger import logger
from utils import generate_string_hash


class MusicManager:
    """Manages background music, countdown SFX, transition sounds, and audio mixing."""

    def __init__(self) -> None:
        self.music_dir = config.paths.music_dir
        self.sfx_dir = config.paths.sfx_dir
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.sfx_dir.mkdir(parents=True, exist_ok=True)

    def get_available_music(self) -> List[Path]:
        """Lists available background music tracks."""
        return [f for f in self.music_dir.glob("*.[mMsS][pP3aA]*") if f.is_file()]

    def get_available_sfx(self) -> List[Path]:
        """Lists available sound effects."""
        return [f for f in self.sfx_dir.glob("*.[mMsS][pP3aA]*") if f.is_file()]

    def process_background_track(
        self,
        audio_path: Path,
        target_duration: float,
        volume_db: float = -12.0,
        fade_in_sec: float = 0.5,
        fade_out_sec: float = 1.0,
    ) -> Optional[Path]:
        """
        Loops or crops background music track to exact target duration, applying volume gain and fades.
        """
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return None

        cache_key = generate_string_hash(f"{audio_path}:{target_duration}:{volume_db}:{fade_in_sec}:{fade_out_sec}")
        output_file = cache_manager.get_file_path(cache_key, extension="mp3", namespace="music_processed")

        if output_file.exists():
            return output_file

        try:
            sound = AudioSegment.from_file(audio_path)
            target_ms = int(target_duration * 1000)

            # Loop if shorter than required scene/video duration
            if len(sound) < target_ms:
                loop_count = (target_ms // len(sound)) + 1
                sound = sound * loop_count

            # Trim to exact length
            sound = sound[:target_ms]

            # Adjust volume gain
            sound = sound + volume_db

            # Apply fades
            if fade_in_sec > 0:
                sound = sound.fade_in(int(fade_in_sec * 1000))
            if fade_out_sec > 0:
                sound = sound.fade_out(int(fade_out_sec * 1000))

            sound.export(output_file, format="mp3", bitrate="192k")
            logger.info(f"Processed background track exported to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to process background track {audio_path}: {e}")
            return None


# Global Music Manager Singleton
music_manager = MusicManager()
