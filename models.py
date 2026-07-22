"""
Data Models for Quiz Studio Pro
Defines data structures for options, timeline scenes, and overall project configuration.
"""

import os
import uuid
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field


class QuizOption(BaseModel):
    text: str = ""
    is_correct: bool = False

    class Config:
        arbitrary_types_allowed = True


class TimelineScene(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    question_text: str = ""
    options: List[QuizOption] = Field(default_factory=list)
    correct_answer: str = ""
    template_name: str = "Standard Trivia"
    duration: float = 7.0
    countdown_sec: float = 5.0
    question_font_size: int = 42
    option_font_size: int = 32
    
    # Template-specific optional fields
    emoji_sequence: Optional[str] = "🍔 👑 🍟"
    flag_code: Optional[str] = "United States"
    blank_text: Optional[str] = "To ___ or not to be"
    logo_bytes: Optional[bytes] = None

    class Config:
        arbitrary_types_allowed = True


class QuizProject(BaseModel):
    title: str = "Automated Quiz Video"
    scenes: List[TimelineScene] = Field(default_factory=list)
    resolution: Tuple[int, int] = (1080, 1920)
    theme_palette: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @property
    def total_duration(self) -> float:
        """Returns the total duration across all timeline scenes."""
        return sum(s.duration for s in self.scenes)

    def add_scene(self, scene: TimelineScene) -> None:
        """Appends a new scene to the timeline."""
        self.scenes.append(scene)

    def remove_scene(self, scene_id: str) -> None:
        """Removes a scene by its unique identifier."""
        self.scenes = [s for s in self.scenes if getattr(s, "id", None) != scene_id]

    def get_scene_at_time(self, time_sec: float) -> Tuple[Optional[TimelineScene], float]:
        """Calculates which scene is active at a given timeline second."""
        if not self.scenes:
            return None, 0.0
            
        accumulated = 0.0
        for s in self.scenes:
            if accumulated <= time_sec < accumulated + s.duration:
                return s, time_sec - accumulated
            accumulated += s.duration
            
        # If scrubber exceeds total time, cap at the last scene
        last_scene = self.scenes[-1]
        return last_scene, last_scene.duration
