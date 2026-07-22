"""
Quiz Project Export Engine for Quiz Studio.
Handles project JSON serializations, asset bundling, and ZIP package creation.
"""

import json
import zipfile
from pathlib import Path
from typing import Optional

from project import QuizProject


class QuizExporter:
    """Serializes and packages Quiz Studio projects for distribution or rendering pipelines."""

    @staticmethod
    def export_to_json(project: QuizProject, output_path: Path) -> Path:
        """Saves project metadata and timeline structure to a single JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = project.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path

    @staticmethod
    def create_bundle_package(project: QuizProject, output_zip_path: Path) -> Path:
        """
        Creates a standalone .zip package containing project.json and all linked local assets
        (e.g., logo images, custom background music, audio clips).
        """
        zip_path = Path(output_zip_path)
        zip_path.parent.mkdir(parents=True, exist_ok=True)

        project_dict = project.to_dict()

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            # Bundle custom asset files referenced in scenes
            for idx, scene in enumerate(project.scenes):
                for key, val in list(scene.custom_data.items()):
                    if isinstance(val, str) and Path(val).exists():
                        asset_file = Path(val)
                        arc_name = f"assets/scene_{idx}_{asset_file.name}"
                        archive.write(asset_file, arcname=arc_name)
                        # Update path reference inside project JSON
                        project_dict["scenes"][idx]["custom_data"][key] = arc_name

            # Write updated project JSON to archive
            json_bytes = json.dumps(project_dict, indent=2).encode("utf-8")
            archive.writestr("project.json", json_bytes)

        return zip_path
