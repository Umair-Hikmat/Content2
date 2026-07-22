"""
Transition Engine for Quiz Studio.
Compiles FFmpeg xfade transition filter chains and generates frame-level transition blends.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

from logger import logger


class TransitionEngine:
    """Provides video transition effects including FFmpeg xfade mappings and image frame blending."""

    # Standard FFmpeg xfade filter names supported natively
    XFADE_TYPES: List[str] = [
        "fade",
        "wipeleft",
        "wiperight",
        "wipeup",
        "wipedown",
        "slideleft",
        "slideright",
        "slideup",
        "slidedown",
        "circlecrop",
        "rectcrop",
        "distance",
        "fadeblack",
        "fadewhite",
        "radial",
        "smoothleft",
        "smoothright",
    ]

    @classmethod
    def get_supported_transitions(cls) -> List[str]:
        """Returns list of supported transition names."""
        return cls.XFADE_TYPES

    @classmethod
    def build_ffmpeg_xfade_filter(
        cls,
        input_label_a: str,
        input_label_b: str,
        output_label: str,
        transition_type: str = "fade",
        duration: float = 0.5,
        offset: float = 0.0,
    ) -> str:
        """
        Builds an FFmpeg filtergraph snippet for xfade transition between two video streams.
        Example: [v0][v1]xfade=transition=fade:duration=0.5:offset=4.5[v_out]
        """
        t_type = transition_type if transition_type in cls.XFADE_TYPES else "fade"
        filter_str = (
            f"[{input_label_a}][{input_label_b}]"
            f"xfade=transition={t_type}:duration={duration:.3f}:offset={offset:.3f}"
            f"[{output_label}]"
        )
        return filter_str

    @staticmethod
    def blend_frames_crossfade(
        frame_a: Image.Image, frame_b: Image.Image, progress: float
    ) -> Image.Image:
        """
        Blends two PIL Image frames with crossfade progress (0.0 to 1.0).
        Used for in-memory composition and thumbnail generation.
        """
        p = max(0.0, min(1.0, progress))
        if p <= 0.0:
            return frame_a
        if p >= 1.0:
            return frame_b

        arr_a = np.array(frame_a.convert("RGBA"), dtype=np.float32)
        arr_b = np.array(frame_b.convert("RGBA"), dtype=np.float32)

        blended_arr = (arr_a * (1.0 - p) + arr_b * p).astype(np.uint8)
        return Image.fromarray(blended_arr, mode="RGBA")


# Global Transition Engine Singleton
transition_engine = TransitionEngine()
