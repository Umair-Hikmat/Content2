"""
Video Export Engine for Quiz Studio.
Renders QuizProject instances into high-definition MP4/MOV video files
using MoviePy and PIL frame composite pipelines.
"""

from pathlib import Path
from typing import Callable, Optional, Tuple
import numpy as np
from PIL import Image

# Robust fallback import supporting both MoviePy v1.x and v2.x
try:
    from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
    MOVIEPY_V2 = False
except ImportError:
    from moviepy.video.VideoClip import VideoClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.audio.AudioClip import CompositeAudioClip
    MOVIEPY_V2 = True

from project import QuizProject
from templates import TemplateRegistry


class VideoExporter:
    """Renders composite frame-by-frame animation timelines to exported video files."""

    def __init__(self, project: QuizProject):
        self.project = project

    def render_to_file(
        self,
        output_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Path:
        """
        Renders the full timeline sequence to an MP4 video file.
        
        Args:
            output_path: Path where the output video will be saved.
            progress_callback: Optional callback receiving progress percentage (0.0 to 1.0).
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        total_duration = self.project.total_duration
        res = self.project.resolution
        fps = self.project.fps

        def make_frame(t: float) -> np.ndarray:
            """Generates an RGB numpy array frame for MoviePy at timestamp t."""
            scene, scene_time = self.project.get_scene_at_time(t)
            
            if scene is None:
                # Render blank frame if out of bounds
                canvas = Image.new("RGB", res, (0, 0, 0))
            else:
                # Retrieve template renderer from global registry
                template = TemplateRegistry.get(scene.template_name)
                
                # Render scene frame with current theme palette
                rgba_frame = template.render_frame(
                    scene=scene,
                    time_sec=scene_time,
                    resolution=res,
                    palette=self.project.theme_palette
                )
                
                # Convert RGBA to RGB composite over background
                bg_color = self.project.theme_palette.get("background", "#0F0F1A")
                canvas = Image.new("RGB", res, bg_color)
                canvas.paste(rgba_frame, (0, 0), mask=rgba_frame)

            if progress_callback and total_duration > 0:
                progress_callback(min(1.0, t / total_duration))

            return np.array(canvas)

        # Build MoviePy VideoClip instance
        video_clip = VideoClip(make_frame, duration=total_duration)
        
        # Attach background music track if configured
        if self.project.audio_track_path and Path(self.project.audio_track_path).exists():
            try:
                bg_audio = AudioFileClip(self.project.audio_track_path)
                
                # Handle audio processing across MoviePy versions
                if MOVIEPY_V2:
                    from moviepy.audio.fx.loop import loop
                    from moviepy.audio.fx.multiply_volume import multiply_volume
                    
                    if bg_audio.duration < total_duration:
                        bg_audio = loop(bg_audio, duration=total_duration)
                    else:
                        bg_audio = bg_audio.subclipped(0, total_duration)
                        
                    bg_audio = multiply_volume(bg_audio, 0.2)
                    video_clip = video_clip.with_audio(bg_audio)
                else:
                    if bg_audio.duration < total_duration:
                        bg_audio = bg_audio.loop(duration=total_duration)
                    else:
                        bg_audio = bg_audio.subclip(0, total_duration)
                        
                    bg_audio = bg_audio.volumex(0.2)
                    video_clip = video_clip.set_audio(bg_audio)
                    
            except Exception as e:
                print(f"[Warning] Failed to attach audio track: {e}")

        # Render MP4 file using ffmpeg
        video_clip.write_videofile(
            str(out_file),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            bitrate="8000k",
            logger=None
        )

        return out_file
