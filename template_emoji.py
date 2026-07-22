"""
Guess the Emoji Quiz Template for Quiz Studio.
Renders enlarged emoji sequence puzzles with answer cards and count-down timers.
"""

from typing import Dict, Tuple
from PIL import Image, ImageDraw

from project import TimelineScene
from templates import BaseQuizTemplate, TemplateRegistry
from fonts import font_manager
from effects import visual_effects


class EmojiQuizTemplate(BaseQuizTemplate):
    """Layout engine for 'Guess the Emoji' challenge scenes."""

    @property
    def template_name(self) -> str:
        return "Guess the Emoji"

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

        font_emoji = font_manager.get_pil_font("Segoe UI Emoji", int(h * 0.08))
        font_title = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.032))
        font_answer = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.045))

        # Title Banner
        draw.text(
            (w // 2, int(h * 0.10)),
            "GUESS THE MOVIE BY EMOJI",
            fill=palette.get("accent", "#FF007F"),
            font=font_title,
            anchor="mm",
        )

        # Emoji Container Card
        emoji_box = (int(w * 0.08), int(h * 0.18), int(w * 0.92), int(h * 0.45))
        visual_effects.draw_rounded_rectangle_with_shadow(
            canvas,
            emoji_box,
            radius=30,
            fill_color=palette.get("card_bg", "#1A1A2E"),
            border_color=palette.get("correct", "#00F5D4"),
            border_width=4,
        )

        # Render Emoji String
        emoji_str = scene.question_text or "🍿 🎬 🍿"
        draw.text(
            (w // 2, int(h * 0.315)),
            emoji_str,
            fill="#FFFFFF",
            font=font_emoji,
            anchor="mm",
        )

        # Timer Bar
        timer_duration = max(1.0, scene.duration - 2.0)
        remaining_ratio = max(0.0, (timer_duration - time_sec) / timer_duration)
        is_reveal = time_sec >= timer_duration

        timer_box = (int(w * 0.12), int(h * 0.50), int(w * 0.88), int(h * 0.525))
        self.draw_timer_gauge(
            draw,
            timer_box,
            remaining_ratio,
            color=palette.get("timer", "#FFE600"),
        )

        # Answer Reveal Card
        ans_box = (int(w * 0.08), int(h * 0.62), int(w * 0.92), int(h * 0.82))
        if is_reveal:
            visual_effects.draw_rounded_rectangle_with_shadow(
                canvas,
                ans_box,
                radius=24,
                fill_color=palette.get("correct", "#00F5D4"),
                border_color="#FFFFFF",
                border_width=3,
            )
            draw.text(
                (w // 2, int(h * 0.72)),
                scene.correct_answer.upper() or "REVEALED ANSWER",
                fill="#000000",
                font=font_answer,
                anchor="mm",
            )
        else:
            visual_effects.draw_rounded_rectangle_with_shadow(
                canvas,
                ans_box,
                radius=24,
                fill_color="#111122",
                border_color="#333355",
                border_width=2,
            )
            draw.text(
                (w // 2, int(h * 0.72)),
                "?????????",
                fill="#555577",
                font=font_answer,
                anchor="mm",
            )

        return canvas


# Register Emoji Template
TemplateRegistry.register(EmojiQuizTemplate())
