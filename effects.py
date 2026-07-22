"""
Visual Effects Module for Quiz Studio.
Provides image filter processing including dropshadows, glassmorphism card backgrounds,
particle overlays, and highlight glow effects.
"""

from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from logger import logger


class VisualEffects:
    """Renders PIL graphical effects and card UI elements for quiz scenes."""

    @staticmethod
    def draw_rounded_rectangle_with_shadow(
        canvas: Image.Image,
        box: Tuple[int, int, int, int],
        radius: int = 20,
        fill_color: str = "#1A1A2E",
        border_color: Optional[str] = "#FF007F",
        border_width: int = 3,
        shadow_blur: int = 15,
        shadow_offset: Tuple[int, int] = (0, 8),
        shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 120),
    ) -> Image.Image:
        """
        Renders a card UI container with rounded corners, drop shadow, and stroke.
        """
        x1, y1, x2, y2 = box
        w, h = canvas.size

        # 1. Shadow layer
        shadow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)

        sx1 = x1 + shadow_offset[0]
        sy1 = y1 + shadow_offset[1]
        sx2 = x2 + shadow_offset[0]
        sy2 = y2 + shadow_offset[1]

        shadow_draw.rounded_rectangle(
            [(sx1, sy1), (sx2, sy2)], radius=radius, fill=shadow_color
        )
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur))

        # Composite shadow onto canvas
        canvas.alpha_composite(shadow_img)

        # 2. Main Card Body
        card_draw = ImageDraw.Draw(canvas)
        card_draw.rounded_rectangle(
            [(x1, y1), (x2, y2)],
            radius=radius,
            fill=fill_color,
            outline=border_color if border_width > 0 else None,
            width=border_width,
        )

        return canvas

    @staticmethod
    def apply_glow_effect(
        image: Image.Image, glow_color: str = "#00F5D4", blur_radius: int = 20
    ) -> Image.Image:
        """
        Generates an outer glow around an image's alpha mask (e.g. correct answer highlights).
        """
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        alpha = image.split()[-1]
        glow_mask = alpha.filter(ImageFilter.GaussianBlur(blur_radius))

        glow_colored = Image.new("RGBA", image.size, glow_color)
        glow_colored.putalpha(glow_mask)

        # Composite original image over glow
        final_canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))
        final_canvas.alpha_composite(glow_colored)
        final_canvas.alpha_composite(image)

        return final_canvas


# Global Visual Effects Singleton
visual_effects = VisualEffects()
