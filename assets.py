"""
Asset Manager for cataloging, caching, uploading, and managing media files
(Images, Videos, Audio, Fonts, GIFs, Logos).
"""

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

from config import config
from logger import logger
from utils import generate_md5, sanitize_filename
from validators import DataValidator


class AssetManager:
    """Provides complete management over media assets used across Quiz Studio projects."""

    def __init__(self) -> None:
        self.assets_dir = config.paths.assets_dir
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self._init_subdirectories()

    def _init_subdirectories(self) -> None:
        """Initializes standard asset folders."""
        for folder in ["images", "videos", "audio", "sfx", "music", "fonts", "logos"]:
            (self.assets_dir / folder).mkdir(parents=True, exist_ok=True)

    def import_asset(self, source_path: Path, category: str) -> Path:
        """Copies an external file into the managed assets hierarchy."""
        if not source_path.exists():
            raise FileNotFoundError(f"Source asset missing: {source_path}")

        target_dir = self.assets_dir / category
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_name = sanitize_filename(source_path.name)
        target_path = target_dir / safe_name

        # Prevent overwriting identical files
        if target_path.exists():
            if generate_md5(source_path) == generate_md5(target_path):
                logger.info(f"Asset '{safe_name}' already exists with identical checksum.")
                return target_path
            else:
                # Append unique hash prefix on name collision
                file_hash = generate_md5(source_path)[:6]
                target_path = target_dir / f"{source_path.stem}_{file_hash}{source_path.suffix}"

        shutil.copy2(source_path, target_path)
        logger.info(f"Successfully imported asset into category '{category}': {target_path}")
        return target_path

    def list_assets(self, category: str) -> List[Path]:
        """Lists all files under a specific asset category."""
        category_dir = self.assets_dir / category
        if not category_dir.exists():
            return []
        return [f for f in category_dir.glob("*") if f.is_file() and not f.name.startswith(".")]

    def get_asset_metadata(self, asset_path: Path) -> Dict[str, Any]:
        """Extracts technical metadata from an image or audio asset."""
        meta: Dict[str, Any] = {
            "name": asset_path.name,
            "size_bytes": asset_path.stat().st_size,
            "category": asset_path.parent.name,
            "extension": asset_path.suffix.lower(),
        }

        ext = asset_path.suffix.lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            try:
                with Image.open(asset_path) as img:
                    meta["width"] = img.width
                    meta["height"] = img.height
                    meta["format"] = img.format
            except Exception as e:
                logger.warning(f"Could not read image metadata for {asset_path}: {e}")

        return meta

    def delete_asset(self, asset_path: Path) -> bool:
        """Deletes a managed asset from disk."""
        try:
            if asset_path.exists() and self.assets_dir in asset_path.parents:
                asset_path.unlink()
                logger.info(f"Deleted asset: {asset_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete asset {asset_path}: {e}")
        return False


# Global Asset Manager Singleton
asset_manager = AssetManager()
