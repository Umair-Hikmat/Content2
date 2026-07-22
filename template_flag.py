"""
Guess the Flag Quiz Template for Quiz Studio.
Renders national flag identification challenges with multi-choice or direct reveal cards.
"""

from pathlib import Path
from typing import Dict, Tuple
from PIL import Image, ImageDraw

from project import TimelineScene
from templates import BaseQuizTemplate, TemplateRegistry
from fonts import font_manager
from effects import visual_effects
from utils import resize_image_to_fit


class FlagQuizTemplate(BaseQuizTemplate):
    """Layout engine for Country Flag geography challenges."""

    @property
    def template_name(self) -> str:
        return "Guess the Flag"

    def render_frame(
        self,
        scene: TimelineScene,
        time_sec: float,
        resolution: Tuple[int, int],
        palette: Dict[str, str],
    ) -> Image.Image:
        w, h = resolution
        canvas = Image.new("RGBA", resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        font_title = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.035))
        font_country = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.042))

        # Title
        draw.text(
            (w // 2, int(h * 0.10)),
            "WHICH COUNTRY'S FLAG IS THIS?",
            fill=palette.get("accent", "#FF007F"),
            font=font_title,
            anchor="mm",
        )

        # Flag Image Card
        flag_box = (int(w * 0.10), int(h * 0.18), int(w * 0.90), int(h * 0.52))
        visual_effects.draw_rounded_rectangle_with_shadow(
            canvas,
            flag_box,
            radius=20,
            fill_color="#1A1A2E",
            border_color="#FFFFFF",
            border_width=3,
        )

        if scene.custom_data.get("flag_path"):
            flag_path = Path(scene.custom_data["flag_path"])
            if flag_path.exists():
                with Image.open(flag_path) as flag_img:
                    flag_img = flag_img.convert("RGBA")
                    target_dim = (int(w * 0.74), int(h * 0.30))
                    fitted_flag = resize_image_to_fit(flag_img, target_dim)
                    canvas.paste(fitted_flag, (int(w * 0.13), int(h * 0.20)), fitted_flag)

        # Timer Bar
        timer_duration = max(1.0, scene.duration - 2.0)
        is_reveal = time_sec >= timer_duration

        timer_box = (int(w * 0.10), int(h * 0.56), int(w * 0.90), int(h * 0.585))
        remaining_ratio = max(0.0, (timer_duration - time_sec) / timer_duration)
        self.draw_timer_gauge(
            draw,
            timer_box,
            remaining_ratio,
            color=palette.get("timer", "#FFE600"),
        )

        # Reveal Country Name
        if is_reveal:
            res_box = (int(w * 0.10), int(h * 0.68), int(w * 0.90), int(h * 0.82))
            visual_effects.draw_rounded_rectangle_with_shadow(
                canvas,
                res_box,
                radius=20,
                fill_color=palette.get("correct", "#00F5D4"),
                border_color="#FFFFFF",
                border_width=3,
            )
            draw.text(
                (w // 2, int(h * 0.75)),
                scene.correct_answer.upper(),
                fill="#000000",
                font=font_country,
                anchor="mm",
            )

        return canvas


# Register Flag Template
TemplateRegistry.register(FlagQuizTemplate())
