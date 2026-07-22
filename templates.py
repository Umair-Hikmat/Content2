"""
Modular Quiz Layout Renderers with multiple template themes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance


def get_pil_font(font_size: int, font_name: str = "arial.ttf") -> ImageFont.FreeTypeFont:
    """Safely loads PIL font with size fallback."""
    try:
        return ImageFont.truetype(font_name, font_size)
    except IOError:
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except IOError:
            return ImageFont.load_default()


class BaseQuizTemplate(ABC):
    @property
    @abstractmethod
    def template_name(self) -> str:
        pass

    @abstractmethod
    def render_frame(
        self,
        scene: Any,
        time_sec: float,
        resolution: Tuple[int, int],
        palette: Dict[str, str],
    ) -> Image.Image:
        pass

    def draw_timer_bar(
        self,
        draw: ImageDraw.ImageDraw,
        box: Tuple[int, int, int, int],
        remaining_ratio: float,
        fill_color: str = "#FFE600",
        bg_color: str = "#1E1E2E",
    ) -> None:
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=10, fill=bg_color)
        fill_w = max(0, int((x2 - x1) * max(0.0, min(1.0, remaining_ratio))))
        if fill_w > 0:
            draw.rounded_rectangle([(x1, y1), (x1 + fill_w, y2)], radius=10, fill=fill_color)


# ---------------------------------------------------------
# TEMPLATE 1: Neon Cyberpunk (Glows, Gradients & Tech Vibe)
# ---------------------------------------------------------
class NeonCyberpunkTemplate(BaseQuizTemplate):
    @property
    def template_name(self) -> str:
        return "Neon Cyberpunk"

    def render_frame(self, scene: Any, time_sec: float, resolution: Tuple[int, int], palette: Dict[str, str]) -> Image.Image:
        w, h = resolution
        img = Image.new("RGBA", (w, h), (15, 15, 30, 255))
        draw = ImageDraw.Draw(img)

        # Animated Gradient Background
        shift = (math.sin(time_sec * 2.0) + 1.0) / 2.0
        for y in range(0, h, 12):
            r = int(10 + shift * 30)
            g = int(10 + (y / h) * 40)
            b = int(45 + (1.0 - shift) * 80)
            draw.rectangle([(0, y), (w, y + 12)], fill=(r, g, b, 255))

        # Question Box
        q_box = [int(w * 0.08), int(h * 0.12), int(w * 0.92), int(h * 0.35)]
        draw.rounded_rectangle(q_box, radius=20, fill=(25, 20, 50, 230), outline="#00F0FF", width=4)

        # Question Text with DYNAMIC FONT SIZE
        q_font = get_pil_font(scene.question_font_size)
        draw.text((w // 2, int(h * 0.235)), scene.question_text or "Question?", fill="#FFFFFF", font=q_font, anchor="mm")

        # Timer Bar
        remaining = max(0.0, 1.0 - (time_sec / max(0.1, scene.duration)))
        self.draw_timer_bar(draw, (int(w * 0.1), int(h * 0.38), int(w * 0.9), int(h * 0.40)), remaining, fill_color="#FF007F")

        # Options
        opt_font = get_pil_font(scene.option_font_size)
        opt_y = int(h * 0.45)
        opt_h = int(h * 0.09)
        spacing = int(h * 0.02)

        for idx, option in enumerate(scene.options[:4]):
            top = opt_y + idx * (opt_h + spacing)
            box = [int(w * 0.1), top, int(w * 0.9), top + opt_h]
            
            fill = (35, 30, 65, 230)
            border = "#7000FF"
            if remaining < 0.25 and option.text == scene.correct_answer:
                fill = (0, 230, 150, 240)
                border = "#00FF99"

            draw.rounded_rectangle(box, radius=14, fill=fill, outline=border, width=3)
            draw.text((box[0] + 35, top + opt_h // 2), f"{chr(65+idx)}. {option.text}", fill="#FFFFFF", font=opt_font, anchor="lm")

        return img


# ---------------------------------------------------------
# TEMPLATE 2: Classic Game Show (Bright Gold & Blue Stage)
# ---------------------------------------------------------
class GameShowTemplate(BaseQuizTemplate):
    @property
    def template_name(self) -> str:
        return "Classic Game Show"

    def render_frame(self, scene: Any, time_sec: float, resolution: Tuple[int, int], palette: Dict[str, str]) -> Image.Image:
        w, h = resolution
        img = Image.new("RGBA", (w, h), (10, 25, 60, 255))
        draw = ImageDraw.Draw(img)

        # Stage Light Rays
        draw.ellipse([int(-w*0.2), int(-h*0.1), int(w*1.2), int(h*0.5)], fill=(255, 215, 0, 40))

        # Question Header Box
        q_box = [int(w * 0.06), int(h * 0.14), int(w * 0.94), int(h * 0.36)]
        draw.rounded_rectangle(q_box, radius=16, fill=(20, 45, 100, 240), outline="#FFD700", width=5)

        # Dynamic Question Text
        q_font = get_pil_font(scene.question_font_size)
        draw.text((w // 2, int(h * 0.25)), scene.question_text or "Question?", fill="#FFD700", font=q_font, anchor="mm")

        # Timer
        remaining = max(0.0, 1.0 - (time_sec / max(0.1, scene.duration)))
        self.draw_timer_bar(draw, (int(w * 0.1), int(h * 0.39), int(w * 0.9), int(h * 0.41)), remaining, fill_color="#FFD700")

        # Option Buttons
        opt_font = get_pil_font(scene.option_font_size)
        opt_y = int(h * 0.46)
        opt_h = int(h * 0.095)
        spacing = int(h * 0.02)

        for idx, option in enumerate(scene.options[:4]):
            top = opt_y + idx * (opt_h + spacing)
            box = [int(w * 0.08), top, int(w * 0.92), top + opt_h]

            fill = (25, 60, 130, 230)
            if remaining < 0.25 and option.text == scene.correct_answer:
                fill = (0, 180, 80, 250)

            draw.rounded_rectangle(box, radius=12, fill=fill, outline="#FFFFFF", width=2)
            draw.text((box[0] + 40, top + opt_h // 2), f"{chr(65+idx)} :  {option.text}", fill="#FFFFFF", font=opt_font, anchor="lm")

        return img


# ---------------------------------------------------------
# TEMPLATE 3: Minimal Dark (Clean Modern Aesthetics)
# ---------------------------------------------------------
class MinimalDarkTemplate(BaseQuizTemplate):
    @property
    def template_name(self) -> str:
        return "Minimal Dark"

    def render_frame(self, scene: Any, time_sec: float, resolution: Tuple[int, int], palette: Dict[str, str]) -> Image.Image:
        w, h = resolution
        img = Image.new("RGBA", (w, h), (18, 18, 22, 255))
        draw = ImageDraw.Draw(img)

        # Question
        q_font = get_pil_font(scene.question_font_size)
        draw.text((w // 2, int(h * 0.22)), scene.question_text or "Question?", fill="#E2E8F0", font=q_font, anchor="mm")

        # Timer Line
        remaining = max(0.0, 1.0 - (time_sec / max(0.1, scene.duration)))
        draw.line([(int(w*0.1), int(h*0.35)), (int(w*0.1 + w*0.8*remaining), int(h*0.35))], fill="#38BDF8", width=6)

        # Options
        opt_font = get_pil_font(scene.option_font_size)
        opt_y = int(h * 0.42)
        opt_h = int(h * 0.085)
        spacing = int(h * 0.02)

        for idx, option in enumerate(scene.options[:4]):
            top = opt_y + idx * (opt_h + spacing)
            box = [int(w * 0.1), top, int(w * 0.9), top + opt_h]

            fill = (30, 41, 59, 255)
            if remaining < 0.25 and option.text == scene.correct_answer:
                fill = (16, 185, 129, 255)

            draw.rounded_rectangle(box, radius=10, fill=fill)
            draw.text((box[0] + 30, top + opt_h // 2), f"{option.text}", fill="#F8FAFC", font=opt_font, anchor="lm")

        return img


# ---------------------------------------------------------
# REGISTRY MANAGEMENT
# ---------------------------------------------------------
class TemplateRegistry:
    _registry: Dict[str, BaseQuizTemplate] = {}

    @classmethod
    def register(cls, template: BaseQuizTemplate) -> None:
        cls._registry[template.template_name] = template

    @classmethod
    def get_template(cls, template_name: str) -> BaseQuizTemplate:
        return cls._registry.get(template_name, cls._registry.get("Neon Cyberpunk", MinimalDarkTemplate()))

    @classmethod
    def get(cls, template_name: str) -> BaseQuizTemplate:
        return cls.get_template(template_name)

    @classmethod
    def list_templates(cls) -> List[str]:
        return list(cls._registry.keys())


# Register default collection
TemplateRegistry.register(NeonCyberpunkTemplate())
TemplateRegistry.register(GameShowTemplate())
TemplateRegistry.register(MinimalDarkTemplate())


def apply_watermark(img: Image.Image, watermark: Any) -> Image.Image:
    if not watermark.enabled:
        return img
    w, h = img.size
    draw = ImageDraw.Draw(img)
    wm_font = get_pil_font(int(h * 0.025))
    margin = int(w * 0.05)
    
    pos_map = {
        "Top Left": ((margin, margin), "la"),
        "Top Right": ((w - margin, margin), "ra"),
        "Bottom Left": ((margin, h - margin), "ld"),
        "Bottom Right": ((w - margin, h - margin), "rd")
    }
    pos, anchor = pos_map.get(watermark.position, ((w - margin, margin), "ra"))

    if watermark.text:
        draw.text(pos, watermark.text, fill=(255, 255, 255, int(255 * watermark.opacity)), font=wm_font, anchor=anchor)
    return img
