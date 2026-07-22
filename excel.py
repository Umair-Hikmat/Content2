"""
Excel and CSV ingestion module for Quiz Studio.
Parses external question banks into standardized Quiz Project structures.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import openpyxl
import pandas as pd

from models import Option


class ExcelImporter:
    """Parser for Excel (.xlsx) and CSV (.csv) question bank files."""

    REQUIRED_COLUMNS = ["question", "correct_answer"]

    @classmethod
    def load_questions_from_file(cls, file_path: Path) -> List[Dict[str, Any]]:
        """
        Reads a spreadsheet or CSV and converts rows into standardized question dicts.
        
        Expected structure:
        - Question / Prompt
        - Correct Answer
        - Option A, Option B, Option C, Option D (Optional for Trivia)
        - Explanation (Optional)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Source file missing: {path}")

        if path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        elif path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Normalize column names (lowercase & stripped)
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

        # Check required columns
        for req in cls.REQUIRED_COLUMNS:
            if req not in df.columns:
                raise ValueError(f"Missing required column: '{req}' in file.")

        questions = []
        for idx, row in df.iterrows():
            q_text = str(row["question"]).strip()
            correct_ans = str(row["correct_answer"]).strip()

            if not q_text or pd.isna(row["question"]):
                continue

            options = []
            # Extract options if present
            for opt_key in ["option_a", "option_b", "option_c", "option_d", "opt_a", "opt_b", "opt_c", "opt_d"]:
                if opt_key in df.columns and not pd.isna(row[opt_key]):
                    opt_str = str(row[opt_key]).strip()
                    is_correct = (opt_str.lower() == correct_ans.lower())
                    options.append(Option(text=opt_str, is_correct=is_correct))

            explanation = str(row.get("explanation", "")).strip() if "explanation" in df.columns else ""

            questions.append({
                "question_text": q_text,
                "correct_answer": correct_ans,
                "options": options,
                "explanation_text": explanation,
                "row_index": idx + 1
            })

        return questions
