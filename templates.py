"""
Template Registry and Base Quiz Layout Engine with full customization support.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, List
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance


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

    def render_background(
        self,
        scene: Any,
        time_sec: float,
        resolution: Tuple[int, int]
    ) -> Image.Image:
        """Renders solid colors, dynamic animated gradients, or loaded custom background images."""
        w, h = resolution
        img = Image.new("RGBA", (w, h), (15, 15, 27, 255))
        draw = ImageDraw.Draw(img)

        if scene.background_type == "Solid Color":
            draw.rectangle([(0, 0), (w, h)], fill=scene.background_color_1)
        elif scene.background_type == "Animated Gradient":
            # Animated shift based on time_sec
            shift = (math.sin(time_sec * 1.5) + 1.0) / 2.0
            for y in range(0, h, 8):
                ratio = (y / h) * 0.7 + (shift * 0.3)
                # Linear blend between color 1 and color 2
                r = int(15 + ratio * 90)
                g = int(15 + ratio * 60)
                b = int(27 + ratio * 150)
                draw.rectangle([(0, y), (w, y + 8)], fill=(r, g, b, 255))
        elif scene.background_type == "Custom Image" and scene.background_image_path:
            try:
                bg = Image.open(scene.background_image_path).convert("RGBA")
                bg = bg.resize((w, h))
                img.paste(bg, (0, 0))
            except Exception:
                draw.rectangle([(0, 0), (w, h)], fill=scene.background_color_1)

        return img

    def draw_timer_gauge(
        self,
        draw: ImageDraw.ImageDraw,
        box: Tuple[int, int, int, int],
        remaining_ratio: float,
        color: str = "#FFE600",
        background_color: str = "#2A2A3D",
    ) -> None:
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=8, fill=background_color)
        fill_width = max(0, int((x2 - x1) * max(0.0, min(1.0, remaining_ratio))))
        if fill_width > 0:
            draw.rounded_rectangle([(x1, y1), (x1 + fill_width, y2)], radius=8, fill=color)


class DefaultTriviaTemplate(BaseQuizTemplate):
    @property
    def template_name(self) -> str:
        return "General Trivia"

    def render_frame(
        self,
        scene: Any,
        time_sec: float,
        resolution: Tuple[int, int],
        palette: Dict[str, str],
    ) -> Image.Image:
        w, h = resolution
        img = self.render_background(scene, time_sec, resolution)
        draw = ImageDraw.Draw(img)

        # 1. Render Question Box
        q_box = [int(w * 0.08), int(h * 0.15), int(w * 0.92), int(h * 0.38)]
        draw.rounded_rectangle(q_box, radius=16, fill=(20, 20, 35, 220), outline=palette.get("accent", "#00CEC9"), width=3)
        
        # Question Text with Custom Font Size
        try:
            font = ImageFont.truetype("arial.ttf", scene.question_font_size)
        except IOError:
            font = ImageFont.load_default()
            
        draw.text((w // 2, int(h * 0.26)), scene.question_text or "Your Question Here", fill="#FFFFFF", font=font, anchor="mm")

        # 2. Render Timer Progress Bar
        remaining = max(0.0, 1.0 - (time_sec / max(0.1, scene.duration)))
        self.draw_timer_gauge(draw, (int(w * 0.1), int(h * 0.40), int(w * 0.9), int(h * 0.42)), remaining)

        # 3. Render Options
        opt_y_start = int(h * 0.46)
        opt_height = int(h * 0.09)
        spacing = int(h * 0.02)

        try:
            opt_font = ImageFont.truetype("arial.ttf", scene.option_font_size)
        except IOError:
            opt_font = ImageFont.load_default()

        for idx, option in enumerate(scene.options[:4]):
            top = opt_y_start + idx * (opt_height + spacing)
            box = [int(w * 0.1), top, int(w * 0.9), top + opt_height]
            
            # Highlight correct answer if time reveals it (e.g. last 30% of duration)
            fill_color = (35, 35, 55, 230)
            if remaining < 0.3 and option.text and option.text == scene.correct_answer:
                fill_color = (0, 184, 148, 240)  # Green correct highlight

            draw.rounded_rectangle(box, radius=12, fill=fill_color)
            draw.text((box[0] + 30, top + opt_height // 2), f"{chr(65+idx)}. {option.text}", fill="#FFFFFF", font=opt_font, anchor="lm")

        return img


class TemplateRegistry:
    _registry: Dict[str, BaseQuizTemplate] = {}

    @classmethod
    def register(cls, template: BaseQuizTemplate) -> None:
        cls._registry[template.template_name] = template

    @classmethod
    def get_template(cls, template_name: str) -> BaseQuizTemplate:
        return cls._registry.get(template_name, cls._registry.get("General Trivia", DefaultTriviaTemplate()))

    @classmethod
    def get(cls, template_name: str) -> BaseQuizTemplate:
        return cls.get_template(template_name)

    @classmethod
    def list_templates(cls) -> List[str]:
        return list(cls._registry.keys()) or ["General Trivia"]


# Register Default Template on import
TemplateRegistry.register(DefaultTriviaTemplate())


def apply_watermark(img: Image.Image, watermark: Any) -> Image.Image:
    """Overlays image logo or text watermark onto the final canvas frame."""
    if not watermark.enabled:
        return img

    w, h = img.size
    draw = ImageDraw.Draw(img)

    try:
        wm_font = ImageFont.truetype("arial.ttf", int(h * 0.025))
    except IOError:
        wm_font = ImageFont.load_default()

    margin = int(w * 0.05)
    
    # Calculate position coordinates
    if watermark.position == "Top Left":
        pos = (margin, margin)
        anchor = "la"
    elif watermark.position == "Top Right":
        pos = (w - margin, margin)
        anchor = "ra"
    elif watermark.position == "Bottom Left":
        pos = (margin, h - margin)
        anchor = "ld"
    else:  # Bottom Right
        pos = (w - margin, h - margin)
        anchor = "rd"

    if watermark.text:
        draw.text(pos, watermark.text, fill=(255, 255, 255, int(255 * watermark.opacity)), font=wm_font, anchor=anchor)

    return img
