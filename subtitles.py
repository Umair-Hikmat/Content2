"""
Subtitle Generator Module for Quiz Studio.
Generates synchronized SRT files and ASS (Advanced SubStation Alpha) styled subtitles
from speech timestamps or scene dialogue for FFmpeg burning.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

from logger import logger
from utils import format_seconds_to_timecode


class SubtitleGenerator:
    """Generates SRT and formatted ASS subtitle files for video overlay."""

    @staticmethod
    def generate_srt(
        subtitles_data: List[Dict[str, Any]], output_path: Path
    ) -> Optional[Path]:
        """
        Generates a standard SubRip (.srt) file.
        Expects subtitles_data list with items: {"start": float, "end": float, "text": str}
        """
        try:
            srt_lines = []
            for idx, item in enumerate(subtitles_data, 1):
                start_str = format_seconds_to_timecode(item["start"]).replace(".", ",")
                end_str = format_seconds_to_timecode(item["end"]).replace(".", ",")
                text = item["text"].strip()

                srt_lines.append(f"{idx}")
                srt_lines.append(f"{start_str} --> {end_str}")
                srt_lines.append(f"{text}\n")

            output_path.write_text("\n".join(srt_lines), encoding="utf-8")
            logger.info(f"Generated SRT subtitle file at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate SRT subtitles: {e}")
            return None

    @staticmethod
    def generate_ass(
        subtitles_data: List[Dict[str, Any]],
        output_path: Path,
        font_name: str = "Arial",
        font_size: int = 48,
        primary_color: str = "&H00FFFFFF",  # ASS Hex ABGR
        outline_color: str = "&H00000000",
        alignment: int = 2,  # Bottom Center
    ) -> Optional[Path]:
        """
        Generates styled Advanced SubStation Alpha (.ass) subtitle file for FFmpeg.
        """
        try:
            header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: QuizSubtitle,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,-1,0,0,0,100,100,0,0,1,3,2,{alignment},30,30,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            event_lines = []
            for item in subtitles_data:
                start_ts = SubtitleGenerator._format_ass_time(item["start"])
                end_ts = SubtitleGenerator._format_ass_time(item["end"])
                text = item["text"].replace("\n", "\\N").strip()
                event_lines.append(
                    f"Dialogue: 0,{start_ts},{end_ts},QuizSubtitle,,0,0,0,,{text}"
                )

            full_ass = header + "\n".join(event_lines) + "\n"
            output_path.write_text(full_ass, encoding="utf-8")
            logger.info(f"Generated ASS subtitle file at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate ASS subtitles: {e}")
            return None

    @staticmethod
    def _format_ass_time(seconds: float) -> str:
        """Converts floating seconds to ASS time format: H:MM:SS.cs"""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds - int(seconds)) * 100)
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{centisecs:02d}"


# Global Subtitle Generator Singleton
subtitle_generator = SubtitleGenerator()
