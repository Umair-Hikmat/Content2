"""
Voice Generator Module for Quiz Studio.
Handles asynchronous TTS synthesis using Edge TTS and Google TTS with full playback caching,
speed adjustments, pitch shifting, and voice listing capabilities.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from gtts import gTTS
import edge_tts

from config import config
from cache import cache_manager
from logger import logger
from utils import generate_string_hash


class VoiceEngine:
    """TTS Synthesizer integrating Edge TTS and Google TTS with custom pitch/speed processing."""

    DEFAULT_VOICES = {
        "Edge TTS": [
            {"id": "en-US-ChristopherNeural", "name": "Christopher (US Male - Deep)", "gender": "Male"},
            {"id": "en-US-JennyNeural", "name": "Jenny (US Female - Clear)", "gender": "Female"},
            {"id": "en-US-GuyNeural", "name": "Guy (US Male - Conversational)", "gender": "Male"},
            {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female - Professional)", "gender": "Female"},
            {"id": "en-AU-WilliamNeural", "name": "William (AU Male - Friendly)", "gender": "Male"},
        ],
        "Google TTS": [
            {"id": "en", "name": "Standard English (gTTS)", "gender": "Neutral"},
            {"id": "es", "name": "Standard Spanish (gTTS)", "gender": "Neutral"},
            {"id": "fr", "name": "Standard French (gTTS)", "gender": "Neutral"},
            {"id": "de", "name": "Standard German (gTTS)", "gender": "Neutral"},
        ],
    }

    @classmethod
    def get_available_voices(cls, provider: str = "Edge TTS") -> List[Dict[str, str]]:
        """Returns registered voices for a given provider."""
        return cls.DEFAULT_VOICES.get(provider, cls.DEFAULT_VOICES["Edge TTS"])

    @classmethod
    async def _synthesize_edge_tts(
        cls, text: str, voice: str, rate_pct: int, pitch_hz: int, output_file: Path
    ) -> bool:
        """Executes synthesis via edge-tts library asynchronously."""
        try:
            rate_str = f"{'+' if rate_pct >= 0 else ''}{rate_pct}%"
            pitch_str = f"{'+' if pitch_hz >= 0 else ''}{pitch_hz}Hz"

            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate_str, pitch=pitch_str)
            await communicate.save(str(output_file))
            return output_file.exists() and output_file.stat().st_size > 0
        except Exception as e:
            logger.error(f"Edge TTS synthesis error: {e}")
            return False

    @classmethod
    def _synthesize_gtts(cls, text: str, lang_code: str, output_file: Path) -> bool:
        """Executes synthesis via Google TTS (gTTS)."""
        try:
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(str(output_file))
            return output_file.exists() and output_file.stat().st_size > 0
        except Exception as e:
            logger.error(f"Google TTS synthesis error: {e}")
            return False

    @classmethod
    def generate_speech(
        cls,
        text: str,
        provider: str = "Edge TTS",
        voice_id: str = "en-US-ChristopherNeural",
        speed: float = 1.0,
        pitch: float = 1.0,
    ) -> Optional[Path]:
        """
        Generates TTS audio file, leveraging local caching to avoid duplicate queries.
        Returns path to generated MP3 file.
        """
        if not text.strip():
            logger.warning("Empty text string provided to VoiceEngine.")
            return None

        # Convert speed/pitch floats to percentage/Hz shifts for Edge TTS
        rate_pct = int((speed - 1.0) * 100)
        pitch_hz = int((pitch - 1.0) * 50)

        cache_key = generate_string_hash(f"{provider}:{voice_id}:{speed}:{pitch}:{text}")
        cached_file = cache_manager.get_file_path(cache_key, extension="mp3", namespace="tts")

        if cached_file.exists() and cached_file.stat().st_size > 0:
            logger.info(f"Retrieved cached TTS audio for: '{text[:20]}...'")
            return cached_file

        logger.info(f"Synthesizing voice [{provider}] voice={voice_id} speed={speed}x pitch={pitch}x: '{text[:30]}...'")

        success = False
        if provider == "Edge TTS":
            success = asyncio.run(cls._synthesize_edge_tts(text, voice_id, rate_pct, pitch_hz, cached_file))
        elif provider == "Google TTS":
            success = cls._synthesize_gtts(text, voice_id, cached_file)

        if success:
            return cached_file
        else:
            logger.error("Voice synthesis failed for current parameters.")
            return None


# Global Voice Engine Instance
voice_engine = VoiceEngine()
