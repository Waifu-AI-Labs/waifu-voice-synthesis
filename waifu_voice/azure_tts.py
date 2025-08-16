"""
Azure Text-to-Speech Integration for Waifu Voice Synthesis
Provides high-quality TTS with anime-style voice processing
"""

import os
import io
import logging
from typing import Dict, List, Optional, Any, Union
import azure.cognitiveservices.speech as speechsdk
from pathlib import Path

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available for audio processing")


class AzureWaifuTTS:
    """Azure-powered Text-to-Speech with anime voice characteristics"""
    
    def __init__(self, subscription_key: Optional[str] = None, region: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Azure configuration
        self.subscription_key = subscription_key or os.environ.get('AZURE_SPEECH_KEY')
        self.region = region or os.environ.get('AZURE_SPEECH_REGION', 'eastus')
        
        if not self.subscription_key:
            self.logger.warning("Azure Speech key not found. Set AZURE_SPEECH_KEY environment variable.")
            self.azure_available = False
        else:
            self.azure_available = True
            self._initialize_azure()
        
        # Waifu character voice mappings (English voices with anime-style adjustments)
        self.character_voices = {
            'sakura': {
                'voice': 'en-US-JennyNeural',   # Sweet, young-sounding English voice
                'style': 'cheerful',
                'pitch': '+20%',                # Higher pitch for anime effect
                'rate': '+8%'
            },
            'yuki': {
                'voice': 'en-US-AriaNeural',    # Soft, gentle English voice
                'style': 'chat',
                'pitch': '+15%',                # Moderately high pitch
                'rate': '-8%'                   # Slower for shy character
            },
            'rei': {
                'voice': 'en-US-SaraNeural',    # Cool, mature English voice
                'style': 'chat',
                'pitch': '+8%',                 # Slightly higher than normal
                'rate': '-12%'                  # Slower, more mysterious
            },
            'miku': {
                'voice': 'en-US-MichelleNeural', # Energetic English voice
                'style': 'excited',
                'pitch': '+25%',                # Very high pitch for bubbly character
                'rate': '+15%'                  # Faster, more energetic
            }
        }
        
        # Emotion-based voice styles
        self.emotion_styles = {
            'cheerful': {'style': 'cheerful', 'pitch_mod': '+8%', 'rate_mod': '+3%'},
            'giggly': {'style': 'excited', 'pitch_mod': '+12%', 'rate_mod': '+5%'},
            'teasing': {'style': 'chat', 'pitch_mod': '+2%', 'rate_mod': '-8%'},
            'shy': {'style': 'gentle', 'pitch_mod': '+6%', 'rate_mod': '-15%'},
            'excited': {'style': 'excited', 'pitch_mod': '+15%', 'rate_mod': '+12%'},
            'sad': {'style': 'sad', 'pitch_mod': '-10%', 'rate_mod': '-20%'},
            'neutral': {'style': 'chat', 'pitch_mod': '0%', 'rate_mod': '0%'},
            'angry': {'style': 'angry', 'pitch_mod': '+5%', 'rate_mod': '+8%'},
            'surprised': {'style': 'excited', 'pitch_mod': '+18%', 'rate_mod': '+15%'}
        }
        
        # Japanese expressions with special pronunciation
        self.japanese_expressions = {
            'konnichiwa': 'こんにちは',
            'ohayo': 'おはよう',
            'arigatou': 'ありがとう',
            'ara ara': 'あらあら',
            'ehehe': 'えへへ',
            'ufufu': 'うふふ',
            'kawaii': 'かわいい',
            'sugoi': 'すごい',
            'baka': 'ばか',
            'onegai': 'お願い',
            'gomen': 'ごめん',
            'kyaa': 'きゃー',
            'yatta': 'やった',
            'dame': 'だめ'
        }
    
    def _initialize_azure(self):
        """Initialize Azure Speech configuration"""
        try:
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key, 
                region=self.region
            )
            
            # Set default output format to high quality
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Riff44100Hz16BitMonoPcm
            )
            
            self.logger.info(f"Azure Speech initialized for region: {self.region}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Speech: {e}")
            self.azure_available = False
    
    def synthesize(self, text: str, character: str = 'sakura', 
                  emotion: str = 'cheerful', **kwargs) -> bytes:
        """
        Synthesize speech using Azure TTS with waifu characteristics
        
        Args:
            text: Text to synthesize
            character: Character name (sakura, yuki, rei, miku)
            emotion: Emotion style
            **kwargs: Additional parameters
            
        Returns:
            Audio data as bytes
        """
        if not self.azure_available:
            return self._fallback_synthesis(text)
        
        try:
            # Get character configuration
            char_config = self.character_voices.get(character, self.character_voices['sakura'])
            emotion_config = self.emotion_styles.get(emotion, self.emotion_styles['neutral'])
            
            # Process text for Japanese expressions
            processed_text = self._process_japanese_text(text)
            
            # Create SSML with waifu voice styling
            ssml = self._create_waifu_ssml(
                processed_text, 
                char_config, 
                emotion_config,
                **kwargs
            )
            
            self.logger.info(f"Synthesizing with Azure TTS: {character} ({emotion})")
            
            # Synthesize with Azure
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                
                # Apply post-processing for anime effects
                processed_audio = self._apply_anime_effects(audio_data, character, emotion)
                return processed_audio
                
            else:
                self.logger.error(f"Azure TTS failed: {result.reason}")
                return self._fallback_synthesis(text)
                
        except Exception as e:
            self.logger.error(f"Azure synthesis failed: {e}")
            return self._fallback_synthesis(text)
    
    def _process_japanese_text(self, text: str) -> str:
        """Process text to handle Japanese expressions in English context"""
        processed = text
        
        # Keep Japanese expressions as romanized for English TTS
        japanese_pronunciations = {
            'konnichiwa': 'koh-nee-chee-wah',
            'ohayo': 'oh-hah-yoh',
            'arigatou': 'ah-ree-gah-toh',
            'ara ara': 'ah-rah ah-rah',
            'ehehe': 'eh-heh-heh',
            'ufufu': 'oo-foo-foo',
            'kawaii': 'kah-wah-ee',
            'sugoi': 'soo-goh-ee',
            'baka': 'bah-kah',
            'onegai': 'oh-neh-gah-ee',
            'gomen': 'goh-men',
            'kyaa': 'kyah',
            'yatta': 'yah-ttah'
        }
        
        # Replace with pronunciation-friendly versions for English TTS
        for original, pronunciation in japanese_pronunciations.items():
            if original.lower() in processed.lower():
                import re
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                processed = pattern.sub(pronunciation, processed)
        
        return processed
    
    def _create_waifu_ssml(self, text: str, char_config: Dict, 
                          emotion_config: Dict, **kwargs) -> str:
        """Create SSML with waifu voice characteristics"""
        
        voice_name = char_config['voice']
        base_style = emotion_config['style']
        
        # Calculate final pitch and rate
        base_pitch = char_config.get('pitch', '0%')
        emotion_pitch = emotion_config.get('pitch_mod', '0%')
        final_pitch = kwargs.get('pitch', self._combine_percentages(base_pitch, emotion_pitch))
        
        base_rate = char_config.get('rate', '0%')
        emotion_rate = emotion_config.get('rate_mod', '0%')
        final_rate = kwargs.get('rate', self._combine_percentages(base_rate, emotion_rate))
        
        # Create SSML
        ssml = f'''
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice_name}">
                <mstts:express-as style="{base_style}" styledegree="1.5">
                    <prosody pitch="{final_pitch}" rate="{final_rate}" volume="+15%">
                        {self._add_expression_breaks(text)}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        '''
        
        return ssml.strip()
    
    def _add_expression_breaks(self, text: str) -> str:
        """Add natural breaks and emphasis to text for anime-like speech in English"""
        # Add pauses and emphasis for anime expressions
        text = text.replace('♪', '<break time="300ms"/>♪<break time="200ms"/>')
        text = text.replace('~', '~<break time="250ms"/>')
        
        # Emphasize common anime expressions
        text = text.replace('ah-rah ah-rah', '<emphasis level="strong">ah-rah ah-rah</emphasis><break time="400ms"/>')
        text = text.replace('eh-heh-heh', '<emphasis level="moderate">eh-heh-heh</emphasis><break time="300ms"/>')
        text = text.replace('oo-foo-foo', '<emphasis level="moderate">oo-foo-foo</emphasis><break time="300ms"/>')
        text = text.replace('kah-wah-ee', '<emphasis level="strong">kah-wah-ee</emphasis><break time="200ms"/>')
        text = text.replace('soo-goh-ee', '<emphasis level="strong">soo-goh-ee</emphasis><break time="200ms"/>')
        
        # Add natural pauses
        text = text.replace('!', '<break time="200ms"/>!')
        text = text.replace('?', '<break time="300ms"/>?')
        text = text.replace('...', '<break time="500ms"/>...')
        
        return text
    
    def _combine_percentages(self, base: str, modifier: str) -> str:
        """Combine percentage values (e.g., '+10%' + '+5%' = '+15%')"""
        try:
            base_val = int(base.replace('%', '').replace('+', ''))
            mod_val = int(modifier.replace('%', '').replace('+', ''))
            result = base_val + mod_val
            return f"+{result}%" if result >= 0 else f"{result}%"
        except:
            return base
    
    def _apply_anime_effects(self, audio_data: bytes, character: str, emotion: str) -> bytes:
        """Apply post-processing effects to make voice more anime-like"""
        try:
            if not NUMPY_AVAILABLE:
                return audio_data
            
            # Convert bytes to numpy array for processing
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Apply character-specific effects
            if character == 'miku':
                # Add slight pitch variation for energetic character
                audio_array = self._add_pitch_variation(audio_array, 0.02)
            elif character == 'yuki':
                # Add breathiness for shy character
                audio_array = self._add_breathiness(audio_array, 0.15)
            elif character == 'rei':
                # Add slight reverb for mysterious character
                audio_array = self._add_simple_reverb(audio_array, 0.1)
            
            # Apply emotion-specific effects
            if emotion in ['giggly', 'excited']:
                audio_array = self._add_pitch_variation(audio_array, 0.03)
            elif emotion == 'shy':
                audio_array *= 0.8  # Reduce volume slightly
            
            # Convert back to bytes
            audio_int16 = (audio_array * 32767).astype(np.int16)
            return audio_int16.tobytes()
            
        except Exception as e:
            self.logger.warning(f"Audio effects failed: {e}")
            return audio_data
    
    def _add_pitch_variation(self, audio: np.ndarray, intensity: float) -> np.ndarray:
        """Add subtle pitch variation for more expressive speech"""
        # Simple pitch variation using vibrato effect
        variation = np.sin(np.arange(len(audio)) * 0.01) * intensity
        return audio * (1 + variation)
    
    def _add_breathiness(self, audio: np.ndarray, intensity: float) -> np.ndarray:
        """Add breathiness effect"""
        noise = np.random.normal(0, 0.01 * intensity, len(audio))
        return audio + noise * (1 - np.abs(audio))  # More noise in quiet parts
    
    def _add_simple_reverb(self, audio: np.ndarray, intensity: float) -> np.ndarray:
        """Add simple reverb effect"""
        delay_samples = int(0.05 * 44100)  # 50ms delay
        if len(audio) > delay_samples:
            delayed = np.zeros_like(audio)
            delayed[delay_samples:] = audio[:-delay_samples]
            return audio + delayed * intensity
        return audio
    
    def _fallback_synthesis(self, text: str) -> bytes:
        """Fallback synthesis when Azure is not available"""
        self.logger.warning("Using fallback synthesis")
        
        # Create a simple WAV header with silence
        duration = len(text) * 0.08  # Rough estimate
        sample_rate = 44100
        samples = int(sample_rate * duration)
        
        # WAV header for 44.1kHz, 16-bit, mono
        header = bytearray([
            0x52, 0x49, 0x46, 0x46,  # 'RIFF'
            0x00, 0x00, 0x00, 0x00,  # File size (placeholder)
            0x57, 0x41, 0x56, 0x45,  # 'WAVE'
            0x66, 0x6D, 0x74, 0x20,  # 'fmt '
            0x10, 0x00, 0x00, 0x00,  # PCM header size
            0x01, 0x00,              # Audio format (PCM)
            0x01, 0x00,              # Channels (mono)
            0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
            0x88, 0x58, 0x01, 0x00,  # Byte rate
            0x02, 0x00,              # Block align
            0x10, 0x00,              # Bits per sample
            0x64, 0x61, 0x74, 0x61,  # 'data'
            0x00, 0x00, 0x00, 0x00   # Data size (placeholder)
        ])
        
        # Add silence data
        silence_data = bytes(samples * 2)  # 16-bit = 2 bytes per sample
        
        # Update sizes in header
        file_size = len(header) + len(silence_data) - 8
        data_size = len(silence_data)
        
        header[4:8] = file_size.to_bytes(4, 'little')
        header[-4:] = data_size.to_bytes(4, 'little')
        
        return bytes(header) + silence_data
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get available character voices and their configurations"""
        return {
            'characters': list(self.character_voices.keys()),
            'emotions': list(self.emotion_styles.keys()),
            'azure_available': self.azure_available,
            'japanese_expressions': list(self.japanese_expressions.keys())
        }
    
    def test_connection(self) -> bool:
        """Test Azure Speech service connection"""
        if not self.azure_available:
            return False
            
        try:
            test_ssml = '''
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ja-JP">
                <voice name="ja-JP-NanamiNeural">
                    <prosody pitch="+10%" rate="+5%">
                        テスト
                    </prosody>
                </voice>
            </speak>
            '''
            
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            result = synthesizer.speak_ssml_async(test_ssml).get()
            
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
            
        except Exception as e:
            self.logger.error(f"Azure connection test failed: {e}")
            return False
