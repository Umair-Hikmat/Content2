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
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve())
    assets_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / "assets")
    projects_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / "projects")
    output_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / "output")
    cache_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / ".cache")
    temp_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / "temp")
    music_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / "assets" / "music")
    sfx_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / "assets" / "sfx")
    fonts_dir: Path = Field(default_factory=lambda: Path(__file__).parent.resolve() / "assets" / "fonts")

    class Config:
        arbitrary_types_allowed = True

    def ensure_directories(self) -> None:
        """Create all runtime directories if they do not exist."""
        for path in self.__dict__.values():
            if isinstance(path, Path):
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"[Warning] Could not create directory {path}: {e}")


class HardwareEncoderDetector:
    """Detects available GPU/Hardware encoders via FFmpeg."""

    @staticmethod
    def get_ffmpeg_path() -> Optional[str]:
        """Safely locate FFmpeg executable without throwing unhandled exceptions."""
        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin:
            return ffmpeg_bin
        
        # Cloud environment fallbacks
        for fallback in ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
            if os.path.exists(fallback) and os.access(fallback, os.X_OK):
                return fallback
                
        return None

    @classmethod
    def detect_best_encoder(cls) -> Dict[str, str]:
        """Detect available hardware encoders or fall back safely to libx264."""
        default_cpu = {"h264": "libx264", "hevc": "libx265", "type": "CPU (Software x264)"}
        
        ffmpeg_bin = cls.get_ffmpeg_path()
        if not ffmpeg_bin:
            return default_cpu

        try:
            result = subprocess.run(
                [ffmpeg_bin, "-encoders"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
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
                return default_cpu
        except Exception:
            return default_cpu


class AppConfig(BaseModel):
    app_name: str = "Quiz Studio Professional"
    paths: SystemPaths = Field(default_factory=SystemPaths)
    hardware_info: Dict[str, str] = Field(default_factory=HardwareEncoderDetector.detect_best_encoder)
    max_parallel_renders: int = Field(default_factory=lambda: max(1, os.cpu_count() or 2))
    log_level: str = "INFO"

    class Config:
        arbitrary_types_allowed = True

    def initialize(self) -> None:
        """Initialize directory paths safely."""
        self.paths.ensure_directories()


# Global Singleton Instance
config = AppConfig()
config.initialize()
