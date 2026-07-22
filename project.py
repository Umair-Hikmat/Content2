"""
Data model and business logic representing a Quiz Studio Project lifecycle,
including scene timeline structures, metadata, and JSON persistence.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from config import config
from logger import logger
from constants import RESOLUTIONS, FRAME_RATES


class QuizOption(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str
    is_correct: bool = False
    image_path: Optional[str] = None


class TimelineScene(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    scene_type: str = "question"  # intro, question, timer, reveal, explanation, cta, outro
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


class ProjectSettings(BaseModel):
    resolution_name: str = "9:16 Vertical (Shorts/TikTok/Reels)"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    quality: str = "High Quality"
    quiz_type: str = "General Trivia"
    theme_name: str = "Cyberpunk Dark"


class QuizProject(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Quiz Project"
    created_at: float = Field(default_factory=lambda: Path.stat(Path.cwd()).st_ctime)
    updated_at: float = Field(default_factory=lambda: Path.stat(Path.cwd()).st_mtime)
    project_dir: Optional[Path] = None
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    scenes: List[TimelineScene] = Field(default_factory=list)

    def set_resolution(self, resolution_name: str) -> None:
        """Sets project dimensions based on constant preset."""
        if resolution_name in RESOLUTIONS:
            w, h = RESOLUTIONS[resolution_name]
            self.settings.resolution_name = resolution_name
            self.settings.width = w
            self.settings.height = h

    def save(self) -> Path:
        """Saves the project data model to disk as project.json."""
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
