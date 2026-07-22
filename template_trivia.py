"""
General Trivia Quiz Template for Quiz Studio.
Renders classic multiple-choice questions with dynamic option highlights,
option card animations, correct answer reveals, and timer gauge bars.
"""

from typing import Dict, Tuple
from PIL import Image, ImageDraw

from project import TimelineScene
from templates import BaseQuizTemplate, TemplateRegistry
from fonts import font_manager
from effects import visual_effects
from animations import animation_engine


class TriviaQuizTemplate(BaseQuizTemplate):
    """Layout engine for standard multiple-choice General Trivia questions."""

    @property
    def template_name(self) -> str:
        return "General Trivia"

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

        font_question = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.035))
        font_option = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.028))
        font_timer = font_manager.get_pil_font("DejaVuSans-Bold", int(h * 0.022))

        # 1. Question Card Container
        q_box = (int(w * 0.08), int(h * 0.12), int(w * 0.92), int(h * 0.32))
        visual_effects.draw_rounded_rectangle_with_shadow(
            canvas,
            q_box,
            radius=24,
            fill_color=palette.get("card_bg", "#1A1A2E"),
            border_color=palette.get("accent", "#FF007F"),
            border_width=3,
        )

        # Draw Question Text
        q_text = scene.question_text or "Question Text Missing"
        draw.text(
            (w // 2, int(h * 0.22)),
            q_text,
            fill=palette.get("primary_text", "#FFFFFF"),
            font=font_question,
            anchor="mm",
            align="center",
        )

        # 2. Timer Gauge Rendering
        timer_duration = max(1.0, scene.duration - 2.0)  # Reserve final 2 seconds for reveal
        remaining_ratio = max(0.0, (timer_duration - time_sec) / timer_duration)
        is_reveal = time_sec >= timer_duration

        timer_box = (int(w * 0.10), int(h * 0.35), int(w * 0.90), int(h * 0.37))
        self.draw_timer_gauge(
            draw,
            timer_box,
            remaining_ratio,
            color=palette.get("timer", "#FFE600"),
            background_color="#2A2A3D",
        )

        # 3. Options List Rendering
        options = scene.options or []
        start_y = int(h * 0.42)
        spacing = int(h * 0.11)

        labels = ["A", "B", "C", "D"]
        for idx, option in enumerate(options[:4]):
            opt_y1 = start_y + (idx * spacing)
            opt_y2 = opt_y1 + int(h * 0.09)
            opt_box = (int(w * 0.08), opt_y1, int(w * 0.92), opt_y2)

            # Slide-in animation for options
            slide_delay = idx * 0.15
            current_x_offset = animation_engine.slide_in_bottom(
                time_sec, slide_delay, 0.4, w * 0.5, 0.0
            )

            card_fill = palette.get("card_bg", "#1A1A2E")
            border_col = palette.get("accent", "#7B2CBF")

            # Reveal styling
            if is_reveal:
                if option.is_correct or option.text.strip().lower() == scene.correct_answer.strip().lower():
                    card_fill = palette.get("correct", "#00F5D4")
                    border_col = "#FFFFFF"
                else:
                    card_fill = "#221122"
                    border_col = palette.get("wrong", "#FF2E93")

            visual_effects.draw_rounded_rectangle_with_shadow(
                canvas,
                (
                    int(opt_box[0] + current_x_offset),
                    opt_box[1],
                    int(opt_box[2] + current_x_offset),
                    opt_box[3],
                ),
                radius=18,
                fill_color=card_fill,
                border_color=border_col,
                border_width=2,
            )

            # Option Label & Text
            lbl_text = f"{labels[idx]}: {option.text}"
            text_color = "#000000" if (is_reveal and option.is_correct) else palette.get("primary_text", "#FFFFFF")
            draw.text(
                (int(w * 0.14) + current_x_offset, opt_y1 + int(h * 0.045)),
                lbl_text,
                fill=text_color,
                font=font_option,
                anchor="lm",
            )

        # 4. Explanation / Reveal Footer
        if is_reveal and scene.explanation_text:
            exp_box = (int(w * 0.08), int(h * 0.86), int(w * 0.92), int(h * 0.95))
            visual_effects.draw_rounded_rectangle_with_shadow(
                canvas,
                exp_box,
                radius=14,
                fill_color="#121212",
                border_color=palette.get("correct", "#00F5D4"),
                border_width=2,
            )
            draw.text(
                (w // 2, int(h * 0.905)),
                scene.explanation_text,
                fill="#EEEEEE",
                font=font_timer,
                anchor="mm",
                align="center",
            )

        return canvas


# Register Trivia Template
TemplateRegistry.register(TriviaQuizTemplate())
