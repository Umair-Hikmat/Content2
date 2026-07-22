"""
Global constants, resolutions, quiz definitions, and system defaults for Quiz Studio.
"""

from typing import Dict, Tuple, List, Any

# Target Resolutions: (Width, Height)
RESOLUTIONS: Dict[str, Tuple[int, int]] = {
    "9:16 Vertical (Shorts/TikTok/Reels)": (1080, 1920),
    "16:9 Landscape (YouTube Desktop)": (1920, 1080),
    "1:1 Square (Instagram Post/FB)": (1080, 1080),
    "4:5 Portrait (FB/Instagram Feed)": (1080, 1350),
    "9:16 HD Vertical": (720, 1280),
    "16:9 HD Landscape": (1280, 720),
}

# FPS Presets
FRAME_RATES: List[int] = [24, 30, 60]

# Render Quality Settings
QUALITY_PRESETS: Dict[str, Dict[str, Any]] = {
    "Draft Mode": {
        "crf": 28,
        "preset": "ultrafast",
        "audio_bitrate": "128k",
        "scale_factor": 0.5,
    },
    "Balanced": {
        "crf": 23,
        "preset": "medium",
        "audio_bitrate": "192k",
        "scale_factor": 1.0,
    },
    "High Quality": {
        "crf": 18,
        "preset": "slow",
        "audio_bitrate": "320k",
        "scale_factor": 1.0,
    },
    "Lossless Master": {
        "crf": 0,
        "preset": "veryslow",
        "audio_bitrate": "320k",
        "scale_factor": 1.0,
    },
}

# Supported Quiz Types
QUIZ_TYPES: List[str] = [
    "General Trivia",
    "Guess the Emoji",
    "Guess the Word",
    "Fill in the Blank",
    "Guess the Logo",
    "Guess the Flag",
    "Guess the Country",
    "Guess the Animal",
    "Guess the Food",
    "Guess the Movie",
    "Guess the Brand",
    "Guess the Celebrity",
    "Guess the Sound",
    "Picture Puzzle",
    "Odd One Out",
    "Memory Challenge",
    "Math Quiz",
    "Kids Learning",
    "Spelling Quiz",
    "Vocabulary Quiz",
    "Science Quiz",
    "History Quiz",
    "Geography Quiz",
]

# Supported Background Types
BACKGROUND_TYPES: List[str] = [
    "Solid Color",
    "Gradient",
    "Image",
    "GIF",
    "Video",
    "Animated Gradient",
    "AI Background",
]

# Supported Audio Providers
TTS_PROVIDERS: List[str] = ["Edge TTS", "Google TTS"]

# Default Color Schemes
DEFAULT_PALETTES: Dict[str, Dict[str, str]] = {
    "Cyberpunk Dark": {
        "background": "#0F0F1B",
        "card_bg": "#1A1A2E",
        "primary_text": "#FFFFFF",
        "accent": "#FF007F",
        "correct": "#00F5D4",
        "wrong": "#FF2E93",
        "timer": "#FFE600",
    },
    "Neon Midnight": {
        "background": "#050505",
        "card_bg": "#121212",
        "primary_text": "#EEEEEE",
        "accent": "#7B2CBF",
        "correct": "#38B000",
        "wrong": "#D90429",
        "timer": "#FF9E00",
    },
    "Vibrant Educational": {
        "background": "#1E1E2E",
        "card_bg": "#2A2A3D",
        "primary_text": "#F8F8F2",
        "accent": "#BD93F9",
        "correct": "#50FA7B",
        "wrong": "#FF5555",
        "timer": "#F1FA8C",
    },
}
