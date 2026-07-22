"""
Data model and business logic representing a Quiz Studio Project lifecycle,
including scene timeline structures, metadata, and JSON persistence.
"""

import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator


class QuizOption(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str = ""
    is_correct: bool = False
    image_path: Optional[str] = None


class TimelineScene(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    scene_type: str = "question"  # intro, question, timer, reveal, explanation, cta, outro
    template_name: str = "General Trivia"
    duration: float = 5.0
    
    # Text Content & Styling
    question_text: str = "Sample Question?"
    question_font_size: int = 48
    options: List[QuizOption] = Field(default_factory=list)
    option_font_size: int = 36
    correct_answer: str = ""
    explanation_text: str = ""
    
    # Voiceover & Audio Speech Settings
    voice_over_text: str = ""
    voice_provider: str = "Edge TTS"  # Edge TTS, ElevenLabs, Custom Clone
    voice_name: str = "en-US-ChristopherNeural"
    voice_clone_id: str = ""
    voice_speed: float = 1.0
    voice_pitch: float = 1.0
    
    # Background Configurations
    background_type: str = "Animated Gradient"  # Solid Color, Animated Gradient, Custom Image
    background_color_1: str = "#0F0F1B"
    background_color_2: str = "#6C5CE7"
    background_image_path: Optional[str] = None
    
    # Audio & SFX Tracks
    background_music: Optional[str] = None
    music_volume: float = 0.3
    sfx_correct: Optional[str] = None
    sfx_wrong: Optional[str] = None
    
    custom_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("options", mode="before")
    @classmethod
    def convert_options(cls, value: Any) -> List[QuizOption]:
        if not value:
            return []
        parsed_options = []
        for opt in value:
            if isinstance(opt, QuizOption):
                parsed_options.append(opt)
            elif isinstance(opt, dict):
                parsed_options.append(QuizOption(**opt))
            elif isinstance(opt, str):
                parsed_options.append(QuizOption(text=opt))
        return parsed_options


class WatermarkSettings(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    enabled: bool = False
    image_path: Optional[str] = None
    text: str = "@MyQuizChannel"
    position: str = "Top Right"  # Top Left, Top Right, Bottom Left, Bottom Right
    opacity: float = 0.8
    scale: float = 0.15  # % of screen width


class ProjectSettings(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    resolution_name: str = "9:16 Vertical (Shorts/TikTok/Reels)"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    quality: str = "High Quality"
    quiz_type: str = "General Trivia"
    theme_name: str = "Cyberpunk Dark"
    watermark: WatermarkSettings = Field(default_factory=WatermarkSettings)


class QuizProject(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Quiz Project"
    created_at: float = Field(default_factory=lambda: time.time())
    updated_at: float = Field(default_factory=lambda: time.time())
    project_dir: Optional[Path] = None
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    scenes: List[TimelineScene] = Field(default_factory=list)

    def add_scene(self, scene_or_type: Optional[Any] = None, **kwargs: Any) -> TimelineScene:
        if isinstance(scene_or_type, TimelineScene):
            scene = scene_or_type
        elif isinstance(scene_or_type, dict):
            scene = TimelineScene(**scene_or_type)
        else:
            scene_type = scene_or_type if isinstance(scene_or_type, str) else "question"
            scene = TimelineScene(scene_type=scene_type, **kwargs)

        self.scenes.append(scene)
        return scene

    def remove_scene(self, scene_id: str) -> bool:
        initial = len(self.scenes)
        self.scenes = [s for s in self.scenes if s.id != scene_id]
        return len(self.scenes) < initial

    def move_scene(self, old_idx: int, new_idx: int) -> None:
        if 0 <= old_idx < len(self.scenes) and 0 <= new_idx < len(self.scenes):
            scene = self.scenes.pop(old_idx)
            self.scenes.insert(new_idx, scene)

    @property
    def total_duration(self) -> float:
        return sum(s.duration for s in self.scenes) or 1.0

    @property
    def resolution(self) -> Tuple[int, int]:
        return (self.settings.width, self.settings.height)

    @property
    def theme_palette(self) -> Dict[str, str]:
        return {
            "background": "#0F0F1B",
            "primary": "#6C5CE7",
            "text": "#FFFFFF",
            "accent": "#00CEC9",
            "correct": "#00B894",
            "wrong": "#FF7675"
        }

    def get_scene_at_time(self, t: float) -> Tuple[Optional[TimelineScene], float]:
        if not self.scenes:
            return None, 0.0
        accumulated = 0.0
        for scene in self.scenes:
            if accumulated <= t < accumulated + scene.duration:
                return scene, t - accumulated
            accumulated += scene.duration
        return self.scenes[-1], self.scenes[-1].duration
