"""
Quiz Studio - Core Data Models
Defines Pydantic models for quiz options, questions, scenes, themes, and project state.
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    TRIVIA = "trivia"
    EMOJI = "emoji"
    FILL_BLANK = "fill_blank"
    LOGO = "logo"
    FLAG = "flag"


class Option(BaseModel):
    """Represents a single choice/option within a quiz question."""
    id: str = Field(default="A", description="Option identifier e.g., A, B, C, D")
    text: str = Field(..., description="Text content for the option")
    is_correct: bool = Field(default=False, description="Whether this option is the correct answer")
    image_path: Optional[str] = Field(default=None, description="Optional path to option image/asset")

    class Config:
        arbitrary_types_allowed = True


class Question(BaseModel):
    """Represents a complete quiz question entry."""
    id: str = Field(..., description="Unique question ID")
    type: QuestionType = Field(default=QuestionType.TRIVIA, description="Quiz question template type")
    question_text: str = Field(..., description="Main question string")
    options: List[Option] = Field(default_factory=list, description="List of answer choices")
    correct_answer: str = Field(..., description="Correct answer text or option ID")
    explanation: Optional[str] = Field(default=None, description="Optional post-answer explanation")
    time_limit: int = Field(default=5, description="Timer duration in seconds")
    media_path: Optional[str] = Field(default=None, description="Path to background image/video asset")
    audio_path: Optional[str] = Field(default=None, description="Path to generated voiceover")

    class Config:
        arbitrary_types_allowed = True


class ThemeConfig(BaseModel):
    """Styling and visual configuration for video rendering."""
    theme_name: str = "Modern Dark"
    bg_color: str = "#1e1e2e"
    primary_color: str = "#cba6f7"
    accent_color: str = "#f38ba8"
    text_color: str = "#cdd6f4"
    font_family: str = "Montserrat-Bold.ttf"
    font_size_title: int = 48
    font_size_options: int = 36


class TimelineScene(BaseModel):
    """Represents a rendered scene component in the video timeline."""
    scene_id: str
    duration: float
    question_data: Question
    render_status: str = "pending"  # pending, rendering, completed, failed
    output_path: Optional[str] = None


class RenderSettings(BaseModel):
    """Global video export settings."""
    resolution_width: int = 1080
    resolution_height: int = 1920
    fps: int = 30
    video_bitrate: str = "8000k"
    encoder: str = "libx264"
    enable_music: bool = True
    music_volume: float = 0.2
    enable_voiceover: bool = True


__all__ = [
    "QuestionType",
    "Option",
    "Question",
    "ThemeConfig",
    "TimelineScene",
    "RenderSettings",
]
