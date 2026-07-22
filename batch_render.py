"""
Batch Processing Engine for Quiz Studio.
Automates bulk queue rendering across multiple Quiz Projects or Excel question banks.
"""

from pathlib import Path
from typing import List, Callable, Optional, Dict
import concurrent.futures

from project import QuizProject
from quiz_import import QuizImporter
from export_video import VideoExporter


class BatchRenderEngine:
    """Manages queue execution for multi-project background video rendering."""

    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.queue: List[Dict[str, Any]] = []

    def add_project_to_queue(self, project: QuizProject, output_path: Path):
        """Appends a QuizProject instance to the rendering queue."""
        self.queue.append({
            "type": "project",
            "project": project,
            "output_path": Path(output_path)
        })

    def add_excel_to_queue(self, excel_path: Path, output_path: Path, template_name: str = "General Trivia"):
        """Imports an Excel question bank and queues it for rendering."""
        self.queue.append({
            "type": "excel",
            "file_path": Path(excel_path),
            "output_path": Path(output_path),
            "template_name": template_name
        })

    def process_queue(self, status_callback: Optional[Callable[[str, int, int], None]] = None) -> List[Path]:
        """
        Executes rendering for all items in the batch queue.
        
        Args:
            status_callback: Called with (current_item_title, completed_count, total_count).
        """
        completed_files: List[Path] = []
        total_items = len(self.queue)

        for index, item in enumerate(self.queue):
            if item["type"] == "project":
                proj = item["project"]
            else:
                proj = QuizImporter.import_from_excel(item["file_path"], item["template_name"])

            if status_callback:
                status_callback(proj.title, index + 1, total_items)

            exporter = VideoExporter(proj)
            out_file = exporter.render_to_file(item["output_path"])
            completed_files.append(out_file)

        # Clear queue after rendering
        self.queue.clear()
        return completed_files
