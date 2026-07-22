"""
Animation Engine for Quiz Studio.
Calculates keyframe values, easing functions, transform offsets, and opacity curves for video elements.
"""

import math
from typing import Tuple, Dict, Any, Callable


class EaseFunctions:
    """Standard cubic bezier easing equations."""

    @staticmethod
    def linear(t: float) -> float:
        return max(0.0, min(1.0, t))

    @staticmethod
    def ease_in_quad(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return t * (2 - t)

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        t = max(0.0, min(1.0, t))
        return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2

    @staticmethod
    def bounce_out(t: float) -> float:
        t = max(0.0, min(1.0, t))
        n1 = 7.5625
        d1 = 2.75

        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375


class AnimationEngine:
    """Calculates position, scale, opacity, and rotation transformations over time."""

    @staticmethod
    def slide_in_bottom(
        current_time: float, start_time: float, duration: float, start_y: float, target_y: float
    ) -> float:
        """Calculates Y coordinate shift sliding in from bottom."""
        if current_time < start_time:
            return start_y
        progress = min(1.0, (current_time - start_time) / max(0.001, duration))
        eased_progress = EaseFunctions.ease_out_quad(progress)
        return start_y + (target_y - start_y) * eased_progress

    @staticmethod
    def fade_in(current_time: float, start_time: float, duration: float) -> float:
        """Calculates alpha value (0.0 to 1.0) fading in over duration."""
        if current_time < start_time:
            return 0.0
        progress = min(1.0, (current_time - start_time) / max(0.001, duration))
        return EaseFunctions.linear(progress)

    @staticmethod
    def pulse_scale(current_time: float, frequency: float = 2.0, min_scale: float = 0.95, max_scale: float = 1.05) -> float:
        """Calculates continuous oscillating scale factor for timers or highlight elements."""
        sine_val = (math.sin(current_time * frequency * math.pi * 2) + 1.0) / 2.0
        return min_scale + sine_val * (max_scale - min_scale)


# Global Animation Engine Singleton
animation_engine = AnimationEngine()
