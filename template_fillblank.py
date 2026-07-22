"""
Fill in the Blank Quiz Template for Quiz Studio.
Renders incomplete sentence cards with masked slots and animated letter/word reveals.
"""

from typing import Dict, Tuple
from PIL import Image, ImageDraw

from project import TimelineScene
from templates import BaseQuizTemplate, TemplateRegistry
from fonts import font_manager
from effects import visual_effects


class FillBlankQuizTemplate(BaseQuizTemplate):
    """Layout engine for 'Fill in the Blank' sentence completion quizzes."""

    @property
    def template_name(self) -> str:
        return "Fill in the Blank"

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

        font_sentence = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.036))
        font_title = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.028))

        # Title
        draw.text(
            (w // 2, int(h * 0.12)),
            "FILL IN THE BLANK",
            fill=palette.get("accent", "#FF007F"),
            font=font_title,
            anchor="mm",
        )

        # Sentence Box
        box = (int(w * 0.08), int(h * 0.20), int(w * 0.92), int(h * 0.50))
        visual_effects.draw_rounded_rectangle_with_shadow(
            canvas,
            box,
            radius=20,
            fill_color=palette.get("card_bg", "#1A1A2E"),
            border_color=palette.get("accent", "#7B2CBF"),
            border_width=3,
        )

        timer_duration = max(1.0, scene.duration - 2.0)
        is_reveal = time_sec >= timer_duration

        # Sentence Rendering
        sentence = scene.question_text or "The capital of France is ______."
        if is_reveal:
            sentence = sentence.replace("______", f"[{scene.correct_answer.upper()}]")

        draw.text(
            (w // 2, int(h * 0.35)),
            sentence,
            fill=palette.get("correct", "#00F5D4") if is_reveal else palette.get("primary_text", "#FFFFFF"),
            font=font_sentence,
            anchor="mm",
            align="center",
        )

        # Progress Timer
        timer_box = (int(w * 0.10), int(h * 0.55), int(w * 0.90), int(h * 0.575))
        remaining_ratio = max(0.0, (timer_duration - time_sec) / timer_duration)
        self.draw_timer_gauge(
            draw,
            timer_box,
            remaining_ratio,
            color=palette.get("timer", "#FFE600"),
        )

        return canvas


# Register Fill Blank Template
TemplateRegistry.register(FillBlankQuizTemplate())
