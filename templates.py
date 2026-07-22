"""
Template Registry and Base Quiz Layout Engine.
Serves as abstract framework for modular quiz layout handlers (Trivia, Emojis, Logos, Flags, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw

from project import TimelineScene
from fonts import font_manager
from effects import visual_effects


class BaseQuizTemplate(ABC):
    """Abstract Base Class for all specialized Quiz Studio layout renderers."""

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Unique identifier name for template."""
        pass

    @abstractmethod
    def render_frame(
        self,
        scene: TimelineScene,
        time_sec: float,
        resolution: Tuple[int, int],
        palette: Dict[str, str],
    ) -> Image.Image:
        """
        Renders a single video frame for a scene at given elapsed time in seconds.
        """
        pass

    def draw_timer_gauge(
        self,
        draw: ImageDraw.ImageDraw,
        box: Tuple[int, int, int, int],
        remaining_ratio: float,
        color: str = "#FFE600",
        background_color: str = "#2A2A3D",
    ) -> None:
        """Helper to render a horizontal progress bar or countdown timer gauge."""
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(
            [(x1, y1), (x2, y2)], radius=8, fill=background_color
        )

        fill_width = max(0, int((x2 - x1) * max(0.0, min(1.0, remaining_ratio))))
        if fill_width > 0:
            draw.rounded_rectangle(
                [(x1, y1), (x1 + fill_width, y2)], radius=8, fill=color
            )


class TemplateRegistry:
    """Central registry mapping quiz types to specialized template implementations."""

    _registry: Dict[str, BaseQuizTemplate] = {}

    @classmethod
    def register(cls, template: BaseQuizTemplate) -> None:
        """Registers a template implementation instance."""
        cls._registry[template.template_name] = template

    @classmethod
    def get_template(cls, template_name: str) -> Optional[BaseQuizTemplate]:
        """Retrieves a registered template engine by name."""
        return cls._registry.get(template_name, cls._registry.get("General Trivia"))

    @classmethod
    def list_templates(self) -> List[str]:
        """Returns registered template names."""
        return list(self._registry.keys())
