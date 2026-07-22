"""
AI Prompt Assistant and Generator Integration for Quiz Studio.
Interfaces with LLMs/APIs to generate structured quiz questions, options, and explanations.
"""

import json
from typing import List, Dict, Any, Optional


class AIGenerator:
    """Interfaces with AI LLM services to generate structured quiz question sets."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def build_prompt_for_topic(self, topic: str, count: int = 5, difficulty: str = "Medium") -> str:
        """Constructs a strict JSON-formatted prompt for LLM text generation engines."""
        return f"""
You are an expert quiz content creator. Generate {count} quiz questions on the topic: "{topic}".
Difficulty Level: {difficulty}.

Return ONLY a valid JSON array of objects with the following schema:
[
  {{
    "question_text": "Question prompt here?",
    "correct_answer": "Exact correct answer option text",
    "options": [
      {{"text": "Option A", "is_correct": false}},
      {{"text": "Option B", "is_correct": true}},
      {{"text": "Option C", "is_correct": false}},
      {{"text": "Option D", "is_correct": false}}
    ],
    "explanation_text": "Short 1-sentence explanation of the answer."
  }}
]
Do not include any conversational text outside the JSON code block.
"""

    def parse_ai_response(self, raw_response_text: str) -> List[Dict[str, Any]]:
        """Cleans and parses the raw JSON string response from an LLM service."""
        cleaned_text = raw_response_text.strip()
        
        # Remove markdown code fences if present
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        try:
            questions = json.loads(cleaned_text)
            if not isinstance(questions, list):
                raise ValueError("Expected JSON response to be a list of question objects.")
            return questions
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response into valid JSON: {str(e)}")
