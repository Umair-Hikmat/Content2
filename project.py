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

from config import config
from logger import logger
from constants import RESOLUTIONS, FRAME_RATES


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
    template_name: str = "trivia"
    duration: float = 5.0
    question_text: str = ""
    options: List[QuizOption] = Field(default_factory=list)
    correct_answer: str = ""
    explanation_text: str = ""
    voice_over_text: str = ""
    voice_provider: str = "Edge TTS"
    voice_name: str = "en-US-ChristopherNeural"
    voice_speed: float = 1.0
    voice_pitch: float = 1.0
    background_type: str = "Solid Color"
    background_value: str = "#0F0F1B"  # Hex, file path, or gradient config
    background_music: Optional[str] = None
    music_volume: float = 0.3
    sfx_correct: Optional[str] = None
    sfx_wrong: Optional[str] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("options", mode="before")
    @classmethod
    def convert_options(cls, value: Any) -> List[QuizOption]:
        """Ensures raw strings, dicts, or QuizOption objects are safely converted."""
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


class ProjectSettings(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    resolution_name: str = "9:16 Vertical (Shorts/TikTok/Reels)"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    quality: str = "High Quality"
    quiz_type: str = "General Trivia"
    theme_name: str = "Cyberpunk Dark"


class QuizProject(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Quiz Project"
    created_at: float = Field(default_factory=lambda: time.time())
    updated_at: float = Field(default_factory=lambda: time.time())
    project_dir: Optional[Path] = None
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    scenes: List[TimelineScene] = Field(default_factory=list)
    audio_track_path: Optional[str] = None

    # --- Flexible Scene Management Helpers ---

    def add_scene(
        self,
        scene_or_type: Optional[Any] = None,
        duration: float = 5.0,
        question_text: str = "",
        options: Optional[List[Any]] = None,
        correct_answer: str = "",
        explanation_text: str = "",
        **kwargs: Any
    ) -> TimelineScene:
        """
        Flexibly appends a TimelineScene to the project.
        Supports passing a TimelineScene object directly OR keyword parameters.
        """
        if isinstance(scene_or_type, TimelineScene):
            scene = scene_or_type
        elif isinstance(scene_or_type, dict):
            scene = TimelineScene(**scene_or_type)
        else:
            scene_type = scene_or_type if isinstance(scene_or_type, str) else "question"
            scene = TimelineScene(
                scene_type=scene_type,
                duration=duration,
                question_text=question_text,
                options=options or [],
                correct_answer=correct_answer,
                explanation_text=explanation_text,
                **kwargs
            )

        self.scenes.append(scene)
        return scene

    def remove_scene(self, scene_id: str) -> bool:
        """Removes a scene by its unique scene ID."""
        initial_length = len(self.scenes)
        self.scenes = [s for s in self.scenes if s.id != scene_id]
        return len(self.scenes) < initial_length

    def move_scene(self, old_index: int, new_index: int) -> None:
        """Reorders scenes in the timeline list."""
        if 0 <= old_index < len(self.scenes) and 0 <= new_index < len(self.scenes):
            scene = self.scenes.pop(old_index)
            self.scenes.insert(new_index, scene)

    # --- Properties required by VideoExporter & App ---

    @property
    def total_duration(self) -> float:
        """Calculates the cumulative duration of all scenes in seconds."""
        return sum(scene.duration for scene in self.scenes)

    @property
    def resolution(self) -> Tuple[int, int]:
        """Returns resolution width and height as a tuple."""
        return (self.settings.width, self.settings.height)

    @property
    def fps(self) -> int:
        """Returns current frame rate setting."""
        return self.settings.fps

    @property
    def theme_palette(self) -> Dict[str, str]:
        """Provides default theme color values for template frame rendering."""
        return {
            "background": "#0F0F1B",
            "primary": "#6C5CE7",
            "secondary": "#A29BFE",
            "text": "#FFFFFF",
            "accent": "#00CEC9",
            "correct": "#00B894",
            "wrong": "#FF7675"
        }

    def get_scene_at_time(self, t: float) -> Tuple[Optional[TimelineScene], float]:
        """
        Calculates which scene is active at timeline timestamp t.
        Returns a tuple of (scene, scene_local_time).
        """
        if not self.scenes:
            return None, 0.0

        accumulated = 0.0
        for scene in self.scenes:
            if accumulated <= t < accumulated + scene.duration:
                return scene, t - accumulated
            accumulated += scene.duration

        if t >= accumulated and self.scenes:
            return self.scenes[-1], self.scenes[-1].duration

        return None, 0.0

    def set_resolution(self, resolution_name: str) -> None:
        """Sets project dimensions based on constant preset."""
        if resolution_name in RESOLUTIONS:
            w, h = RESOLUTIONS[resolution_name]
            self.settings.resolution_name = resolution_name
            self.settings.width = w
            self.settings.height = h

    def save(self) -> Path:
        """Saves the project data model to disk as project.json."""
        self.updated_at = time.time()
        if not self.project_dir:
            safe_name = self.title.lower().replace(" ", "_")
            self.project_dir = config.paths.projects_dir / f"{safe_name}_{self.project_id[:8]}"

        self.project_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.project_dir / "project.json"

        data = self.model_dump(mode="json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=str)

        logger.info(f"Project '{self.title}' successfully saved to {file_path}")
        return file_path

    @classmethod
    def load(cls, project_dir: Path) -> "QuizProject":
        """Loads a QuizProject from a folder containing project.json."""
        json_path = project_dir / "project.json" if project_dir.is_dir() else project_dir
        if not json_path.exists():
            raise FileNotFoundError(f"No project file found at {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        project = cls(**data)
        project.project_dir = json_path.parent
        logger.info(f"Loaded project '{project.title}' from disk.")
        return project
