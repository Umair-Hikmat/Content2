"""
Background Generation Engine for Quiz Studio.
Generates solid colors, linear/radial gradients, animated background frames, or formats background media.
"""

import math
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image, ImageDraw

from logger import logger
from utils import resize_image_to_fit


class BackgroundEngine:
    """Generates and processes background graphics and video frames for quiz scenes."""

    @staticmethod
    def create_solid_background(resolution: Tuple[int, int], color_hex: str) -> Image.Image:
        """Creates a static solid color image background."""
        return Image.new("RGBA", resolution, color_hex)

    @staticmethod
    def create_gradient_background(
        resolution: Tuple[int, int], color_start: str, color_end: str, direction: str = "vertical"
    ) -> Image.Image:
        """Renders a smooth two-color linear gradient."""
        w, h = resolution
        base = Image.new("RGBA", (w, h))
        draw = ImageDraw.Draw(base)

        def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
            hex_clean = hex_str.lstrip("#")
            return tuple(int(hex_clean[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore

        r1, g1, b1 = hex_to_rgb(color_start)
        r2, g2, b2 = hex_to_rgb(color_end)

        if direction == "vertical":
            for y in range(h):
                ratio = y / max(1, h - 1)
                r = int(r1 + ratio * (r2 - r1))
                g = int(g1 + ratio * (g2 - g1))
                b = int(b1 + ratio * (b2 - b1))
                draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        else:  # Horizontal
            for x in range(w):
                ratio = x / max(1, w - 1)
                r = int(r1 + ratio * (r2 - r1))
                g = int(g1 + ratio * (g2 - g1))
                b = int(b1 + ratio * (b2 - b1))
                draw.line([(x, 0), (x, h)], fill=(r, g, b, 255))

        return base

    @classmethod
    def create_animated_gradient_frame(
        cls, resolution: Tuple[int, int], color_start: str, color_end: str, time_sec: float
    ) -> Image.Image:
        """Renders a dynamic pulsating gradient frame based on elapsed time."""
        w, h = resolution
        # Modulate direction and mix ratio using sine wave oscillation
        shift = (math.sin(time_sec * 1.5) + 1.0) / 2.0
        
        # Interpolate starting angle/blend
        draw_dir = "vertical" if int(time_sec) % 2 == 0 else "horizontal"
        return cls.create_gradient_background(resolution, color_start, color_end, direction=draw_dir)

    @staticmethod
    def process_image_background(resolution: Tuple[int, int], image_path: Path, blur: bool = True) -> Image.Image:
        """Loads and formats a background image to fit output resolution."""
        if not image_path.exists():
            return Image.new("RGBA", resolution, "#0F0F1B")

        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            resized = resize_image_to_fit(img, resolution)
            return resized


# Global Background Engine Singleton
background_engine = BackgroundEngine()
