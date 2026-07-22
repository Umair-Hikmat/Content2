"""
Guess the Logo Quiz Template for Quiz Studio.
Renders masked/blurred brand logo images that unblur or reveal upon answer countdown complete.
"""

from pathlib import Path
from typing import Dict, Tuple
from PIL import Image, ImageDraw, ImageFilter

from project import TimelineScene
from templates import BaseQuizTemplate, TemplateRegistry
from fonts import font_manager
from effects import visual_effects
from utils import resize_image_to_fit


class LogoQuizTemplate(BaseQuizTemplate):
    """Layout engine for Brand Logo identification challenges."""

    @property
    def template_name(self) -> str:
        return "Guess the Logo"

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
        font_answer = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.040))

        draw.text(
            (w // 2, int(h * 0.10)),
            "GUESS THE LOGO",
            fill=palette.get("accent", "#FF007F"),
            font=font_title,
            anchor="mm",
        )

        # Container Box
        img_box = (int(w * 0.12), int(h * 0.18), int(w * 0.88), int(h * 0.55))
        visual_effects.draw_rounded_rectangle_with_shadow(
            canvas,
            img_box,
            radius=24,
            fill_color="#FFFFFF",
            border_color=palette.get("accent", "#7B2CBF"),
            border_width=4,
        )

        timer_duration = max(1.0, scene.duration - 2.0)
        is_reveal = time_sec >= timer_duration

        # Logo Image Processing
        if scene.custom_data.get("logo_path"):
            logo_path = Path(scene.custom_data["logo_path"])
            if logo_path.exists():
                with Image.open(logo_path) as logo_img:
                    logo_img = logo_img.convert("RGBA")
                    target_dim = (int(w * 0.68), int(h * 0.32))
                    fitted_logo = resize_image_to_fit(logo_img, target_dim)

                    if not is_reveal:
                        # Apply blur during countdown
                        blur_amt = max(1, int((1.0 - (time_sec / timer_duration)) * 20))
                        fitted_logo = fitted_logo.filter(ImageFilter.GaussianBlur(blur_amt))

                    canvas.paste(fitted_logo, (int(w * 0.16), int(h * 0.205)), fitted_logo)

        # Timer
        timer_box = (int(w * 0.12), int(h * 0.60), int(w * 0.88), int(h * 0.625))
        remaining_ratio = max(0.0, (timer_duration - time_sec) / timer_duration)
        self.draw_timer_gauge(
            draw,
            timer_box,
            remaining_ratio,
            color=palette.get("timer", "#FFE600"),
        )

        # Answer Title
        if is_reveal:
            draw.text(
                (w // 2, int(h * 0.75)),
                scene.correct_answer.upper(),
                fill=palette.get("correct", "#00F5D4"),
                font=font_answer,
                anchor="mm",
            )

        return canvas


# Register Logo Template
TemplateRegistry.register(LogoQuizTemplate())
