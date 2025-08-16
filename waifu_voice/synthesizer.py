"""
Main Voice Synthesizer
Core synthesis engine that combines all components
"""

import io
import json
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

from .emotion_detector import EmotionDetector
from .voice_models import VoiceModelManager
from .japanese_processor import JapaneseTextProcessor
from .audio_processor import AudioProcessor
from .azure_tts import AzureWaifuTTS

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available, limited functionality")


class WaifuVoiceSynthesizer:
    """Main voice synthesis engine for waifu characters"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.emotion_detector = EmotionDetector()
        self.voice_models = VoiceModelManager()
        self.japanese_processor = JapaneseTextProcessor()
        self.audio_processor = AudioProcessor()
        self.azure_tts = AzureWaifuTTS()
        
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Default synthesis parameters
        self.default_params = {
            'character': 'sakura',
            'voice_style': 'cute',
            'language': 'mixed',  # English/Japanese mixed
            'emotion': 'auto',    # Auto-detect from text
            'speed': 1.0,
            'pitch': 1.0,
            'energy': 1.0,
            'output_format': 'wav',
            'quality': 'high'
        }
        
        # Synthesis cache for performance
        self.cache = {}
        self.cache_enabled = True
        self.max_cache_size = 100
        
        self.logger.info("WaifuVoiceSynthesizer initialized")
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load synthesis configuration"""
        default_config = {
            'sample_rate': 22050,
            'hop_length': 256,
            'win_length': 1024,
            'n_fft': 1024,
            'enable_gpu': True,
            'cache_enabled': True,
            'default_character': 'sakura',
            'supported_languages': ['en', 'ja', 'mixed'],
            'quality_presets': {
                'low': {'sample_rate': 16000, 'quality_factor': 0.6},
                'medium': {'sample_rate': 22050, 'quality_factor': 0.8},
                'high': {'sample_rate': 44100, 'quality_factor': 1.0}
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config file {config_file}: {e}")
        
        return default_config
    
    def synthesize(self, text: str, **kwargs) -> bytes:
        """
        Main synthesis method
        
        Args:
            text: Text to synthesize
            **kwargs: Synthesis parameters (character, emotion, voice_style, etc.)
            
        Returns:
            Audio data as bytes
        """
        try:
            # Merge parameters
            params = self.default_params.copy()
            params.update(kwargs)
            
            # Check cache first
            cache_key = self._generate_cache_key(text, params)
            if self.cache_enabled and cache_key in self.cache:
                self.logger.debug(f"Cache hit for text: {text[:50]}...")
                return self.cache[cache_key]
            
            # Process text and detect emotions
            processed_text, synthesis_params = self._prepare_synthesis(text, params)
            
            # Generate audio
            audio_data = self._generate_audio(processed_text, synthesis_params)
            
            # Apply post-processing effects
            final_audio = self._apply_post_processing(audio_data, synthesis_params)
            
            # Convert to output format
            output_bytes = self._format_output(final_audio, params['output_format'])
            
            # Cache result
            if self.cache_enabled:
                self._update_cache(cache_key, output_bytes)
            
            self.logger.info(f"Successfully synthesized audio for text: {text[:50]}...")
            return output_bytes
            
        except Exception as e:
            self.logger.error(f"Synthesis failed for text '{text}': {e}")
            # Return silence as fallback
            return self._generate_silence(1.0)
    
    def synthesize_streaming(self, text: str, **kwargs):
        """
        Stream synthesis for real-time applications
        
        Args:
            text: Text to synthesize
            **kwargs: Synthesis parameters
            
        Yields:
            Audio chunks as bytes
        """
        try:
            # Split text into chunks for streaming
            chunks = self._split_text_for_streaming(text)
            
            for chunk in chunks:
                if chunk.strip():
                    audio_chunk = self.synthesize(chunk, **kwargs)
                    yield audio_chunk
                    
        except Exception as e:
            self.logger.error(f"Streaming synthesis failed: {e}")
            yield self._generate_silence(0.5)
    
    def _prepare_synthesis(self, text: str, params: Dict[str, Any]) -> tuple:
        """Prepare text and parameters for synthesis"""
        # Detect emotions if auto mode
        if params['emotion'] == 'auto':
            emotion_analysis = self.emotion_detector.detect_emotion(text)
            detected_emotion = emotion_analysis['primary_emotion']
            emotion_params = emotion_analysis['voice_parameters']
        else:
            detected_emotion = params['emotion']
            emotion_params = {'pitch': 1.0, 'speed': 1.0, 'energy': 1.0}
        
        # Process Japanese text
        japanese_analysis = self.japanese_processor.preprocess_for_tts(text)
        
        # Get character-specific parameters
        character_params = self.voice_models.generate_voice_parameters(
            params['character'], 
            detected_emotion,
            params.get('voice_style')
        )
        
        # Combine all parameters
        synthesis_params = {
            'text': text,
            'processed_text': japanese_analysis['romanized_text'],
            'character': params['character'],
            'emotion': detected_emotion,
            'voice_style': params.get('voice_style', 'cute'),
            'language': params['language'],
            'pronunciation_guide': japanese_analysis['pronunciation_guide'],
            'accent_pattern': japanese_analysis['accent_pattern'],
            'output_format': params['output_format'],
            'quality': params['quality']
        }
        
        # Merge parameter sets
        for key, value in emotion_params.items():
            synthesis_params[f'emotion_{key}'] = value
        
        for key, value in character_params.items():
            synthesis_params[f'character_{key}'] = value
        
        # Apply user overrides
        for key in ['speed', 'pitch', 'energy']:
            if key in params:
                synthesis_params[key] = params[key]
        
        return japanese_analysis['romanized_text'], synthesis_params
    
    def _generate_audio(self, text: str, params: Dict[str, Any]) -> Union[bytes, 'np.ndarray']:
        """Generate raw audio from processed text"""
        # Use Azure TTS for high-quality synthesis
        try:
            audio_data = self.azure_tts.synthesize(
                text=text,
                character=params['character'],
                emotion=params['emotion'],
                pitch=params.get('character_pitch', 1.0),
                rate=params.get('character_speaking_rate', 1.0)
            )
            
            self.logger.info(f"Generated audio using Azure TTS for: {text[:50]}...")
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Azure TTS failed, using fallback: {e}")
            return self._generate_fallback_audio(text, params)
    
    def _generate_fallback_audio(self, text: str, params: Dict[str, Any]) -> bytes:
        """Fallback audio generation when Azure TTS is not available"""
        self.logger.warning("Using fallback audio generation")
        
        # Generate silence with proper WAV format
        duration = len(text) * 0.08  # Rough estimate
        return self._generate_silence(duration)
    
    def _apply_post_processing(self, audio_data: Union[bytes, 'np.ndarray'], 
                             params: Dict[str, Any]) -> Union[bytes, 'np.ndarray']:
        """Apply audio effects and post-processing"""
        if not NUMPY_AVAILABLE:
            return audio_data
        
        # Apply character and emotion effects
        processed_audio = self.audio_processor.apply_character_effects(
            audio_data,
            params['character'],
            params['emotion']
        )
        
        # Apply any additional effects
        effects = {}
        if 'character_pitch' in params:
            effects['pitch_shift'] = (params['character_pitch'] - 1.0) * 0.5
        if 'character_energy' in params:
            effects['energy_boost'] = (params['character_energy'] - 1.0) * 0.3
        
        if effects:
            processed_audio = self.audio_processor.process_audio(processed_audio, effects)
        
        return processed_audio
    
    def _format_output(self, audio_data: Union[bytes, 'np.ndarray'], 
                      output_format: str) -> bytes:
        """Format audio data for output"""
        if isinstance(audio_data, bytes):
            return audio_data
        
        if NUMPY_AVAILABLE and hasattr(audio_data, 'dtype'):
            return self.audio_processor.process_audio(audio_data, output_format=output_format)
        
        # Fallback
        return b''
    
    def _generate_cache_key(self, text: str, params: Dict[str, Any]) -> str:
        """Generate cache key for synthesis parameters"""
        key_params = {
            'text': text,
            'character': params.get('character'),
            'emotion': params.get('emotion'),
            'voice_style': params.get('voice_style'),
            'speed': params.get('speed'),
            'pitch': params.get('pitch'),
            'energy': params.get('energy')
        }
        
        return json.dumps(key_params, sort_keys=True)
    
    def _update_cache(self, key: str, data: bytes):
        """Update synthesis cache"""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = data
    
    def _split_text_for_streaming(self, text: str) -> List[str]:
        """Split text into chunks suitable for streaming"""
        # Simple sentence-based splitting
        import re
        
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) > 100:  # Chunk size limit
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    chunks.append(sentence)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _generate_silence(self, duration: float) -> bytes:
        """Generate silence of specified duration"""
        if NUMPY_AVAILABLE:
            import numpy as np
            
            sample_rate = self.config['sample_rate']
            samples = int(sample_rate * duration)
            silence = np.zeros(samples, dtype=np.float32)
            
            return self.audio_processor.process_audio(silence, output_format='wav')
        else:
            # Return minimal WAV file
            return b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    def get_available_voices(self) -> Dict[str, List[str]]:
        """Get list of available voices and characters"""
        return {
            'characters': self.voice_models.list_characters(),
            'voice_styles': self.voice_models.list_voice_styles(),
            'emotions': list(self.emotion_detector.emotion_weights.keys())
        }
    
    def set_character_config(self, character: str, config: Dict[str, Any]) -> bool:
        """Set custom configuration for a character"""
        return self.voice_models.create_character_voice(character, config)
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for synthesis planning"""
        emotion_analysis = self.emotion_detector.detect_emotion(text)
        japanese_analysis = self.japanese_processor.preprocess_for_tts(text)
        speech_patterns = self.emotion_detector.analyze_speech_patterns(text)
        
        return {
            'emotions': emotion_analysis,
            'japanese_processing': japanese_analysis,
            'speech_patterns': speech_patterns,
            'recommended_character': self._recommend_character(emotion_analysis),
            'estimated_duration': len(text) * 0.08  # Rough estimate
        }
    
    def _recommend_character(self, emotion_analysis: Dict[str, Any]) -> str:
        """Recommend best character for given emotional context"""
        primary_emotion = emotion_analysis['primary_emotion']
        
        recommendations = {
            'cheerful': 'sakura',
            'giggly': 'miku',
            'teasing': 'rei',
            'shy': 'yuki',
            'excited': 'miku',
            'sad': 'yuki',
            'neutral': 'sakura'
        }
        
        return recommendations.get(primary_emotion, 'sakura')
    
    def clear_cache(self):
        """Clear synthesis cache"""
        self.cache.clear()
        self.logger.info("Synthesis cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get synthesizer statistics"""
        return {
            'cache_size': len(self.cache),
            'cache_enabled': self.cache_enabled,
            'available_characters': len(self.voice_models.list_characters()),
            'loaded_models': len(self.voice_models.loaded_models),
            'config': self.config
        }
