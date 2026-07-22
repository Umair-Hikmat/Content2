"""
Global Configuration Management, Environment Setup, and Hardware Encoder Auto-Detection.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field


class SystemPaths(BaseModel):
    base_dir: Path = Path(__file__).parent.resolve()
    assets_dir: Path = base_dir / "assets"
    projects_dir: Path = base_dir / "projects"
    output_dir: Path = base_dir / "output"
    cache_dir: Path = base_dir / ".cache"
    temp_dir: Path = base_dir / "temp"
    music_dir: Path = assets_dir / "music"
    sfx_dir: Path = assets_dir / "sfx"
    fonts_dir: Path = assets_dir / "fonts"

    def ensure_directories(self) -> None:
        """Create all runtime directories if they do not exist."""
        for path in self.__dict__.values():
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)


class HardwareEncoderDetector:
    """Detects available GPU/Hardware encoders via FFmpeg."""

    @staticmethod
    def get_ffmpeg_path() -> str:
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            raise RuntimeError("FFmpeg executable not found in system PATH.")
        return ffmpeg_bin

    @classmethod
    def detect_best_encoder(cls) -> Dict[str, str]:
        ffmpeg_bin = cls.get_ffmpeg_path()
        try:
            result = subprocess.run(
                [ffmpeg_bin, "-encoders"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            encoders_output = result.stdout

            if "h264_nvenc" in encoders_output:
                return {"h264": "h264_nvenc", "hevc": "hevc_nvenc", "type": "NVIDIA NVENC"}
            elif "h264_qsv" in encoders_output:
                return {"h264": "h264_qsv", "hevc": "hevc_qsv", "type": "Intel QuickSync"}
            elif "h264_amf" in encoders_output:
                return {"h264": "h264_amf", "hevc": "hevc_amf", "type": "AMD AMF"}
            elif "h264_videotoolbox" in encoders_output:
                return {"h264": "h264_videotoolbox", "hevc": "hevc_videotoolbox", "type": "Apple VideoToolbox"}
            else:
                return {"h264": "libx264", "hevc": "libx265", "type": "CPU (Software x264)"}
        except Exception:
            return {"h264": "libx264", "hevc": "libx265", "type": "CPU (Software x264)"}


class AppConfig(BaseModel):
    app_name: str = "Quiz Studio Professional"
    paths: SystemPaths = Field(default_factory=SystemPaths)
    hardware_info: Dict[str, str] = Field(default_factory=HardwareEncoderDetector.detect_best_encoder)
    max_parallel_renders: int = Field(default_factory=lambda: max(1, os.cpu_count() or 2))
    log_level: str = "INFO"

    def initialize() -> None:
        self.paths.ensure_directories()


# Global Singleton Instance
config = AppConfig()
config.initialize()
