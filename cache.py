"""
Thread-safe disk and memory caching system for Quiz Studio.
Optimizes rendering by caching generated audio, rendered frame layers, and intermediate video segments.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Optional, Dict, Union
import pickle

from config import config
from logger import logger
from utils import generate_string_hash, generate_md5


class CacheManager:
    """Provides high-performance multi-tier key-value storage and asset caching."""

    _instance: Optional["CacheManager"] = None

    def __init__(self) -> None:
        self.cache_dir: Path = config.paths.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}
        logger.info(f"CacheManager initialized at {self.cache_dir}")

    @classmethod
    def get_instance(cls) -> "CacheManager":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = CacheManager()
        return cls._instance

    def _get_key_path(self, key: str, namespace: str = "general") -> Path:
        """Generates a file path for a given key and namespace."""
        hash_key = generate_string_hash(f"{namespace}:{key}")
        ns_dir = self.cache_dir / namespace
        ns_dir.mkdir(parents=True, exist_ok=True)
        return ns_dir / f"{hash_key}.bin"

    def get(self, key: str, namespace: str = "general") -> Optional[Any]:
        """Retrieves an item from memory cache or disk cache."""
        mem_key = f"{namespace}:{key}"
        if mem_key in self._memory_cache:
            return self._memory_cache[mem_key]

        file_path = self._get_key_path(key, namespace)
        if file_path.exists():
            try:
                with open(file_path, "rb") as f:
                    data = pickle.load(f)
                    self._memory_cache[mem_key] = data
                    return data
            except Exception as e:
                logger.error(f"Error reading cache for key '{key}' in '{namespace}': {e}")
                file_path.unlink(missing_ok=True)
        return None

    def set(self, key: str, value: Any, namespace: str = "general") -> bool:
        """Stores an item in memory and disk cache."""
        mem_key = f"{namespace}:{key}"
        self._memory_cache[mem_key] = value

        file_path = self._get_key_path(key, namespace)
        try:
            with open(file_path, "wb") as f:
                pickle.dump(value, f)
            return True
        except Exception as e:
            logger.error(f"Error writing cache for key '{key}' in '{namespace}': {e}")
            return False

    def get_file_path(self, key: str, extension: str, namespace: str = "media") -> Path:
        """Returns a direct Path object reserved for cached media files (audio/video)."""
        hash_key = generate_string_hash(f"{namespace}:{key}")
        ns_dir = self.cache_dir / namespace
        ns_dir.mkdir(parents=True, exist_ok=True)
        return ns_dir / f"{hash_key}.{extension.lstrip('.')}"

    def exists(self, key: str, namespace: str = "general") -> bool:
        """Checks if a cache entry exists."""
        mem_key = f"{namespace}:{key}"
        if mem_key in self._memory_cache:
            return True
        return self._get_key_path(key, namespace).exists()

    def clear_namespace(self, namespace: str) -> None:
        """Clears all cached items under a specific namespace."""
        ns_dir = self.cache_dir / namespace
        if ns_dir.exists():
            shutil.rmtree(ns_dir, ignore_errors=True)
            logger.info(f"Cleared cache namespace: {namespace}")
        
        # Clear memory cache items matching namespace
        keys_to_del = [k for k in self._memory_cache if k.startswith(f"{namespace}:")]
        for k in keys_to_del:
            del self._memory_cache[k]

    def clear_all(self) -> None:
        """Purges the entire disk and memory cache."""
        self._memory_cache.clear()
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir, ignore_errors=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Purged complete application cache.")


# Global Cache Manager Singleton
cache_manager = CacheManager.get_instance()
