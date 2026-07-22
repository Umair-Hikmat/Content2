"""
Text-to-Speech (TTS) Voiceover Generator for Quiz Studio.
Generates spoken question text, countdown sound effects, and answer announcements.
"""

from pathlib import Path
from typing import Optional
from gtts import gTTS


class VoiceoverGenerator:
    """Engine for converting question text into spoken voiceover audio clips."""

    def __init__(self, language: str = "en", tld: str = "com"):
        self.language = language
        self.tld = tld

    def generate_question_voiceover(
        self,
        text: str,
        output_path: Path
    ) -> Path:
        """
        Synthesizes TTS audio from text and saves it as an MP3 file.
        
        Args:
            text: The text to convert to speech.
            output_path: Target MP3 output file path.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        cleaned_text = text.replace("_", " ").strip()
        if not cleaned_text:
            raise ValueError("Text string is empty; cannot generate voiceover.")

        tts = gTTS(text=cleaned_text, lang=self.language, tld=self.tld, slow=False)
        tts.save(str(out_file))

        return out_file
