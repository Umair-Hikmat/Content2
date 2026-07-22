"""
Core utility functions for file handling, hash generation, time formatting,
system diagnostics, and image manipulation helper routines.
"""

import hashlib
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Tuple, Optional, Any, Dict
import psutil
from PIL import Image

from logger import logger


def generate_md5(file_path: Path) -> str:
    """Computes MD5 hash of a given file path for caching and validation."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_string_hash(text: str) -> str:
    """Computes MD5 hash of an arbitrary string."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def format_seconds_to_timecode(seconds: float) -> str:
    """Converts floating seconds to HH:MM:SS.mmm format."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"


def sanitize_filename(name: str) -> str:
    """Removes non-alphanumeric characters to make safe file names."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")


def get_system_resource_usage() -> Dict[str, Any]:
    """Fetches real-time CPU, RAM, and Disk metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_free_gb": round(shutil.disk_usage(Path.cwd()).free / (1024**3), 2),
    }


def resize_image_to_fit(
    image: Image.Image, target_size: Tuple[int, int], fill_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
) -> Image.Image:
    """Resizes and centers an image inside target dimensions while preserving aspect ratio."""
    target_w, target_h = target_size
    img_w, img_h = image.size

    ratio = min(target_w / img_w, target_h / img_h)
    new_w = max(1, int(img_w * ratio))
    new_h = max(1, int(img_h * ratio))

    resized_img = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (target_w, target_h), fill_color)

    offset_x = (target_w - new_w) // 2
    offset_y = (target_h - new_h) // 2
    canvas.paste(resized_img, (offset_x, offset_y), resized_img if resized_img.mode == "RGBA" else None)

    return canvas


def run_command(cmd: list, timeout: Optional[int] = None) -> Tuple[int, str, str]:
    """Executes a subprocess command safely with log outputs."""
    logger.debug(f"Executing command: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error(f"Command timed out after {timeout} seconds: {' '.join(cmd)}")
        return -1, "", "Command execution timed out."
    except Exception as e:
        logger.error(f"Failed to run command {' '.join(cmd)}: {str(e)}")
        return -1, "", str(e)
