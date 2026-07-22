"""
Quiz Project Import Engine for Quiz Studio.
Imports JSON project files, Excel spreadsheets, and ZIP archive packages.
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, Any, Union

from project import QuizProject, TimelineScene
from excel import ExcelImporter


class QuizImporter:
    """Handles importing full project structures or raw question banks into Quiz Studio."""

    @staticmethod
    def import_project_json(file_path: Path) -> QuizProject:
        """Loads a full QuizProject instance from a .json template file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Project file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return QuizProject.from_dict(data)

    @staticmethod
    def import_from_excel(file_path: Path, template_name: str = "General Trivia") -> QuizProject:
        """Converts an Excel/CSV question bank into a ready-to-render QuizProject."""
        raw_questions = ExcelImporter.load_questions_from_file(file_path)
        
        project = QuizProject(
            title=f"Imported - {Path(file_path).stem}",
            description=f"Auto-generated from {file_path.name}",
        )

        for q_data in raw_questions:
            scene = TimelineScene(
                template_name=template_name,
                duration=7.0,
                question_text=q_data["question_text"],
                correct_answer=q_data["correct_answer"],
                options=q_data["options"],
                explanation_text=q_data.get("explanation_text", "")
            )
            project.add_scene(scene)

        return project

    @staticmethod
    def unpack_zip_package(zip_path: Path, extract_dir: Path) -> Path:
        """Extracts a bundled project archive containing assets and JSON metadata."""
        zip_path = Path(zip_path)
        extract_dir = Path(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as archive:
            archive.extractall(extract_dir)

        json_file = extract_dir / "project.json"
        if not json_file.exists():
            raise FileNotFoundError("Extracted archive does not contain 'project.json'")

        return json_file
