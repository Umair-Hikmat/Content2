"""
Font Management and Typography Engine for Quiz Studio.
Handles font discovery, fallbacks, system font loading, and PIL ImageFont compilation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import ImageFont

from config import config
from logger import logger


class FontManager:
    """Manages custom and system fonts for rendering titles, questions, and options."""

    _instance: Optional["FontManager"] = None

    def __init__(self) -> None:
        self.fonts_dir: Path = config.paths.fonts_dir
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        self.registered_fonts: Dict[str, Path] = {}
        self._discover_fonts()

    @classmethod
    def get_instance(cls) -> "FontManager":
        """Singleton instance accessor."""
        if cls._instance is None:
            cls._instance = FontManager()
        return cls._instance

    def _discover_fonts(self) -> None:
        """Scans the local fonts directory and common system font paths."""
        # 1. Scan application bundled fonts
        for font_file in self.fonts_dir.glob("*.[tT][tT][fF]"):
            self.registered_fonts[font_file.stem] = font_file
        for font_file in self.fonts_dir.glob("*.[oO][tT][fF]"):
            self.registered_fonts[font_file.stem] = font_file

        # 2. System font fallback paths
        system_font_paths: List[Path] = [
            Path("C:/Windows/Fonts"),
            Path("/usr/share/fonts"),
            Path("/Library/Fonts"),
            Path("~/Library/Fonts").expanduser(),
        ]

        common_system_fonts = [
            "arial.ttf", "arialbd.ttf", "impact.ttf", "calibri.ttf",
            "segoeui.ttf", "segoeuib.ttf", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
        ]

        for sys_dir in system_font_paths:
            if sys_dir.exists():
                for font_name in common_system_fonts:
                    candidate = sys_dir / font_name
                    if candidate.exists() and candidate.stem not in self.registered_fonts:
                        self.registered_fonts[candidate.stem] = candidate

        logger.info(f"FontManager initialized. Registered {len(self.registered_fonts)} fonts.")

    def get_available_fonts(self) -> List[str]:
        """Returns sorted list of available font family names."""
        return sorted(list(self.registered_fonts.keys()))

    def get_font_path(self, font_name: str) -> Optional[Path]:
        """Retrieves path to a registered font by name."""
        if font_name in self.registered_fonts:
            return self.registered_fonts[font_name]
        
        # Fallback search by case-insensitive name
        for name, path in self.registered_fonts.items():
            if name.lower() == font_name.lower():
                return path
        return None

    def get_pil_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """Loads a PIL ImageFont instance with automatic fallback to default font."""
        font_path = self.get_font_path(font_name)
        if font_path and font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception as e:
                logger.warning(f"Failed to load font '{font_name}' from {font_path}: {e}")

        # Fallback to PIL default
        logger.warning(f"Using default system font for size {size}")
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

    def add_custom_font(self, font_file_path: Path) -> str:
        """Copies a user-uploaded font into the assets directory and registers it."""
        if not font_file_path.exists():
            raise FileNotFoundError(f"Font file does not exist: {font_file_path}")

        dest_path = self.fonts_dir / font_file_path.name
        if dest_path != font_file_path:
            dest_path.write_bytes(font_file_path.read_bytes())

        font_name = dest_path.stem
        self.registered_fonts[font_name] = dest_path
        logger.info(f"Registered custom font: {font_name} from {dest_path}")
        return font_name


# Global Font Manager Singleton
font_manager = FontManager.get_instance()
