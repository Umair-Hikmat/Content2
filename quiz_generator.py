"""
Automatic Quiz Sequence Assembly Generator.
Builds full quiz video timelines from predefined templates, rules, and question sets.
"""

from typing import List, Dict, Any, Optional
from project import QuizProject, TimelineScene
from models import Option


class QuizGenerator:
    """High-level builder for programmatically structuring full-length short-form video projects."""

    def __init__(self, default_resolution: tuple = (1080, 1920), fps: int = 30):
        self.resolution = default_resolution
        self.fps = fps

    def build_quiz_project(
        self,
        title: str,
        question_data_list: List[Dict[str, Any]],
        template_name: str = "General Trivia",
        scene_duration: float = 7.0,
        intro_scene: bool = True,
        outro_scene: bool = True
    ) -> QuizProject:
        """
        Constructs a complete QuizProject timeline from question objects.
        Automatically attaches intro hooks, standard countdown scenes, and call-to-action outros.
        """
        project = QuizProject(
            title=title,
            resolution=self.resolution,
            fps=self.fps
        )

        # 1. Add Intro Hook Scene
        if intro_scene:
            intro = TimelineScene(
                template_name="General Trivia",
                duration=3.0,
                question_text=f"🔥 {title.upper()} CHALLENGE! 🔥\nCan you get 5/5?",
                correct_answer="",
                options=[]
            )
            project.add_scene(intro)

        # 2. Add Quiz Question Scenes
        for q_dict in question_data_list:
            options = [
                Option(text=opt["text"], is_correct=opt.get("is_correct", False))
                for opt in q_dict.get("options", [])
            ]

            scene = TimelineScene(
                template_name=template_name,
                duration=scene_duration,
                question_text=q_dict.get("question_text", ""),
                correct_answer=q_dict.get("correct_answer", ""),
                options=options,
                explanation_text=q_dict.get("explanation_text", ""),
                custom_data=q_dict.get("custom_data", {})
            )
            project.add_scene(scene)

        # 3. Add Outro Call to Action
        if outro_scene:
            outro = TimelineScene(
                template_name="General Trivia",
                duration=4.0,
                question_text="How many did you get right?\nCOMMENT YOUR SCORE BELOW! 👇",
                correct_answer="",
                options=[]
            )
            project.add_scene(outro)

        return project
