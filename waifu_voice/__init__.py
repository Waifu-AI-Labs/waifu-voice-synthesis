"""
Waifu Voice Synthesis Pipeline
Advanced voice synthesis system for anime waifu characters
"""

from .synthesizer import WaifuVoiceSynthesizer
from .emotion_detector import EmotionDetector
from .voice_models import VoiceModelManager
from .japanese_processor import JapaneseTextProcessor
from .audio_processor import AudioProcessor
from .azure_tts import AzureWaifuTTS

__version__ = "1.0.0"
__author__ = "Waifu AI Labs"

__all__ = [
    "WaifuVoiceSynthesizer",
    "EmotionDetector", 
    "VoiceModelManager",
    "JapaneseTextProcessor",
    "AudioProcessor",
    "AzureWaifuTTS"
]
