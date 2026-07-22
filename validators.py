"""
Validation rules and assertion helpers for user inputs, media formats, and import structures.
"""

from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import pandas as pd

from constants import RESOLUTIONS, FRAME_RATES, QUIZ_TYPES


class ValidationResult:
    """Encapsulates validation outcome with detailed error messages."""

    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, message: str) -> None:
        self.is_valid = False
        self.errors.append(message)


class DataValidator:
    """Validates project parameters, spreadsheet imports, and media assets."""

    @staticmethod
    def validate_resolution(width: int, height: int) -> ValidationResult:
        result = ValidationResult()
        if width <= 0 or height <= 0:
            result.add_error(f"Invalid dimensions: {width}x{height}. Must be greater than 0.")
        if width % 2 != 0 or height % 2 != 0:
            result.add_error(f"Dimensions ({width}x{height}) must be even numbers for FFmpeg encoding.")
        return result

    @staticmethod
    def validate_fps(fps: int) -> ValidationResult:
        result = ValidationResult()
        if fps not in FRAME_RATES:
            result.add_error(f"FPS {fps} is not standard. Recommended presets: {FRAME_RATES}")
        return result

    @staticmethod
    def validate_quiz_excel_df(df: pd.DataFrame) -> ValidationResult:
        """Validates structure of imported quiz spreadsheets."""
        result = ValidationResult()
        required_columns = ["Question", "Option A", "Option B", "Answer"]

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            result.add_error(f"Missing required columns in spreadsheet: {', '.join(missing_cols)}")
            return result

        if df.empty:
            result.add_error("Spreadsheet contains no data rows.")
            return result

        for idx, row in df.iterrows():
            if pd.isna(row["Question"]) or str(row["Question"]).strip() == "":
                result.add_error(f"Row {idx + 2}: Question text cannot be empty.")
            if pd.isna(row["Answer"]) or str(row["Answer"]).strip() == "":
                result.add_error(f"Row {idx + 2}: Correct Answer cannot be empty.")

        return result

    @staticmethod
    def validate_media_file(file_path: Path, allowed_extensions: List[str]) -> ValidationResult:
        """Validates media asset presence and extension."""
        result = ValidationResult()
        if not file_path.exists():
            result.add_error(f"File does not exist: {file_path}")
            return result

        ext = file_path.suffix.lower().lstrip(".")
        allowed_clean = [e.lower().lstrip(".") for e in allowed_extensions]
        if ext not in allowed_clean:
            result.add_error(f"Unsupported extension '.{ext}'. Expected one of: {allowed_clean}")

        return result
