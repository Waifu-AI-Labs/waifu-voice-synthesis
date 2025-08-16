"""
Minimal Waifu Voice Synthesizer using only Azure Neural TTS
Clean implementation focused on high-quality anime voice synthesis
"""

import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .azure_tts import AzureWaifuTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WaifuVoiceSynthesizer:
    """Minimal waifu voice synthesizer using Azure Neural TTS"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Azure TTS (the only component we need)
        self.azure_tts = AzureWaifuTTS()
        
        if not self.azure_tts.azure_available:
            self.logger.warning("Azure Speech Service not configured. Run scripts/setup_azure.py")
        
        self.logger.info("Minimal WaifuVoiceSynthesizer initialized with Azure Neural TTS")
    
    def synthesize(self, text: str, character: str = 'sakura', 
                  emotion: str = 'cheerful', **kwargs) -> bytes:
        """
        Synthesize waifu voice using Azure Neural TTS
        
        Args:
            text: Text to synthesize
            character: Character name (sakura, yuki, rei, miku)
            emotion: Emotion style (cheerful, giggly, teasing, shy, etc.)
            **kwargs: Additional Azure TTS parameters
            
        Returns:
            Audio data as bytes (WAV format)
        """
        try:
            self.logger.info(f"Synthesizing: '{text[:50]}...' as {character} ({emotion})")
            
            # Direct Azure synthesis - no unnecessary processing
            audio_data = self.azure_tts.synthesize(
                text=text,
                character=character,
                emotion=emotion,
                **kwargs
            )
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Synthesis failed: {e}")
            raise
    
    def synthesize_streaming(self, text: str, **kwargs):
        """
        Stream synthesis for real-time applications
        Simply splits text into chunks for Azure TTS
        """
        # Split text into sentences for streaming
        import re
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                yield self.synthesize(sentence, **kwargs)
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get available character voices"""
        return self.azure_tts.get_available_voices()
    
    def test_azure_connection(self) -> bool:
        """Test Azure Speech service connection"""
        return self.azure_tts.test_connection()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Simple text analysis for emotion detection"""
        # Simple emotion detection based on text patterns
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['!', 'yay', 'amazing', 'wonderful', '♪']):
            emotion = 'cheerful'
        elif any(word in text_lower for word in ['ehehe', 'hehe', 'funny', 'giggle']):
            emotion = 'giggly'  
        elif any(word in text_lower for word in ['ara ara', 'interesting', '~']):
            emotion = 'teasing'
        elif any(word in text_lower for word in ['um', 'maybe', 'shy', 'embarrass']):
            emotion = 'shy'
        elif any(word in text_lower for word in ['wow', 'excited', 'can\'t wait']):
            emotion = 'excited'
        else:
            emotion = 'neutral'
        
        # Recommend character based on emotion
        character_map = {
            'cheerful': 'sakura',
            'giggly': 'miku', 
            'teasing': 'rei',
            'shy': 'yuki',
            'excited': 'miku'
        }
        
        return {
            'detected_emotion': emotion,
            'recommended_character': character_map.get(emotion, 'sakura'),
            'text_length': len(text),
            'estimated_duration': len(text) * 0.08
        }
