"""
Audio Processing Module
Handles audio effects, post-processing, and output formatting
"""

import io
import wave
import struct
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging

try:
    import librosa
    import soundfile as sf
    from pydub import AudioSegment
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning("Audio libraries not available, limited processing capabilities")


class AudioProcessor:
    """Processes and enhances synthesized audio"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        
        # Audio effect presets
        self.effect_presets = {
            'cute': {
                'pitch_shift': 0.2,
                'formant_shift': 0.15,
                'brightness': 0.3,
                'reverb_room_size': 0.2,
                'chorus_depth': 0.1
            },
            'soft': {
                'pitch_shift': 0.1,
                'formant_shift': 0.05,
                'brightness': -0.1,
                'reverb_room_size': 0.3,
                'chorus_depth': 0.05
            },
            'energetic': {
                'pitch_shift': 0.3,
                'formant_shift': 0.2,
                'brightness': 0.4,
                'reverb_room_size': 0.1,
                'chorus_depth': 0.2
            },
            'teasing': {
                'pitch_shift': -0.1,
                'formant_shift': -0.05,
                'brightness': 0.2,
                'reverb_room_size': 0.25,
                'chorus_depth': 0.15
            }
        }
        
        # Emotion-specific audio effects
        self.emotion_effects = {
            'cheerful': {'brightness': 0.2, 'energy_boost': 0.1},
            'giggly': {'pitch_variation': 0.15, 'tempo_variation': 0.1},
            'teasing': {'pitch_bend': 0.1, 'sultry_effect': 0.2},
            'shy': {'volume_reduction': 0.2, 'breathiness': 0.3},
            'excited': {'energy_boost': 0.3, 'pitch_variation': 0.2},
            'sad': {'pitch_lower': 0.2, 'reverb_increase': 0.3}
        }
        
    def process_audio(self, audio_data: Union[np.ndarray, bytes], 
                     effects: Dict[str, float] = None,
                     output_format: str = 'wav') -> bytes:
        """Apply audio processing effects to synthesized audio"""
        if not AUDIO_LIBS_AVAILABLE:
            self.logger.warning("Audio libraries not available, returning original audio")
            return audio_data if isinstance(audio_data, bytes) else audio_data.tobytes()
        
        try:
            # Convert input to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_array = self._bytes_to_array(audio_data)
            else:
                audio_array = audio_data.astype(np.float32)
            
            # Apply effects
            if effects:
                audio_array = self._apply_effects(audio_array, effects)
            
            # Normalize audio
            audio_array = self._normalize_audio(audio_array)
            
            # Convert to desired output format
            return self._array_to_bytes(audio_array, output_format)
            
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
            return audio_data if isinstance(audio_data, bytes) else audio_data.tobytes()
    
    def _bytes_to_array(self, audio_bytes: bytes) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        # Assume 16-bit PCM for now
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        return audio_array.astype(np.float32) / 32768.0
    
    def _array_to_bytes(self, audio_array: np.ndarray, format: str = 'wav') -> bytes:
        """Convert numpy array to audio bytes"""
        # Ensure array is in correct range
        audio_array = np.clip(audio_array, -1.0, 1.0)
        
        if format == 'wav':
            # Convert to 16-bit PCM
            audio_int16 = (audio_array * 32767).astype(np.int16)
            
            # Create WAV file in memory
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            return buffer.getvalue()
        else:
            # Return raw PCM
            audio_int16 = (audio_array * 32767).astype(np.int16)
            return audio_int16.tobytes()
    
    def _apply_effects(self, audio: np.ndarray, effects: Dict[str, float]) -> np.ndarray:
        """Apply audio effects to the audio signal"""
        processed_audio = audio.copy()
        
        # Pitch shifting
        if 'pitch_shift' in effects and AUDIO_LIBS_AVAILABLE:
            shift_steps = effects['pitch_shift'] * 12  # Convert to semitones
            processed_audio = librosa.effects.pitch_shift(
                processed_audio, 
                sr=self.sample_rate, 
                n_steps=shift_steps
            )
        
        # Brightness adjustment (simple high-frequency emphasis)
        if 'brightness' in effects:
            processed_audio = self._adjust_brightness(processed_audio, effects['brightness'])
        
        # Energy boost
        if 'energy_boost' in effects:
            processed_audio = self._apply_energy_boost(processed_audio, effects['energy_boost'])
        
        # Pitch variation for expressiveness
        if 'pitch_variation' in effects:
            processed_audio = self._apply_pitch_variation(processed_audio, effects['pitch_variation'])
        
        # Volume adjustments
        if 'volume_reduction' in effects:
            processed_audio *= (1.0 - effects['volume_reduction'])
        
        # Breathiness effect
        if 'breathiness' in effects:
            processed_audio = self._add_breathiness(processed_audio, effects['breathiness'])
        
        return processed_audio
    
    def _adjust_brightness(self, audio: np.ndarray, brightness: float) -> np.ndarray:
        """Adjust brightness by emphasizing/de-emphasizing high frequencies"""
        if not AUDIO_LIBS_AVAILABLE:
            return audio
            
        # Simple high-frequency emphasis using differentiation
        if brightness > 0:
            # Emphasize high frequencies
            diff = np.diff(audio, prepend=audio[0])
            return audio + brightness * diff * 0.5
        else:
            # De-emphasize high frequencies with simple low-pass
            alpha = 0.8 + brightness * 0.2
            filtered = np.zeros_like(audio)
            filtered[0] = audio[0]
            for i in range(1, len(audio)):
                filtered[i] = alpha * filtered[i-1] + (1 - alpha) * audio[i]
            return filtered
    
    def _apply_energy_boost(self, audio: np.ndarray, boost: float) -> np.ndarray:
        """Apply energy boost to make voice more lively"""
        # Simple dynamic range expansion
        threshold = 0.1
        ratio = 1.0 + boost
        
        boosted = np.where(
            np.abs(audio) > threshold,
            np.sign(audio) * (threshold + (np.abs(audio) - threshold) * ratio),
            audio
        )
        
        return boosted
    
    def _apply_pitch_variation(self, audio: np.ndarray, variation: float) -> np.ndarray:
        """Apply subtle pitch variations for more natural speech"""
        if not AUDIO_LIBS_AVAILABLE:
            return audio
            
        # Create a subtle vibrato effect
        vibrato_rate = 4.0  # Hz
        vibrato_depth = variation * 0.5  # semitones
        
        t = np.arange(len(audio)) / self.sample_rate
        vibrato = np.sin(2 * np.pi * vibrato_rate * t) * vibrato_depth
        
        # Apply pitch modulation (simplified)
        modulated = audio.copy()
        for i in range(1, len(audio)):
            pitch_factor = 2 ** (vibrato[i] / 12)
            # Simple time-domain pitch modification
            if pitch_factor != 1.0:
                modulated[i] = audio[int(i / pitch_factor)] if int(i / pitch_factor) < len(audio) else audio[i]
        
        return modulated
    
    def _add_breathiness(self, audio: np.ndarray, breathiness: float) -> np.ndarray:
        """Add breathiness effect to voice"""
        # Add subtle noise to simulate breath
        noise = np.random.normal(0, 0.02 * breathiness, len(audio))
        
        # Mix with original audio, more prominent in quiet sections
        audio_energy = np.abs(audio)
        noise_mask = 1.0 - np.clip(audio_energy * 10, 0, 1)
        
        return audio + noise * noise_mask
    
    def _normalize_audio(self, audio: np.ndarray, target_level: float = -3.0) -> np.ndarray:
        """Normalize audio to target level in dB"""
        # Calculate RMS level
        rms = np.sqrt(np.mean(audio**2))
        if rms == 0:
            return audio
        
        # Target level in linear scale
        target_linear = 10**(target_level / 20)
        
        # Apply normalization
        normalized = audio * (target_linear / rms)
        
        # Apply soft limiting to prevent clipping
        return self._soft_limit(normalized)
    
    def _soft_limit(self, audio: np.ndarray, threshold: float = 0.95) -> np.ndarray:
        """Apply soft limiting to prevent harsh clipping"""
        def soft_clip(x):
            if abs(x) <= threshold:
                return x
            else:
                return threshold * np.tanh(x / threshold)
        
        return np.vectorize(soft_clip)(audio)
    
    def apply_character_effects(self, audio: np.ndarray, character: str, 
                              emotion: str = 'neutral') -> np.ndarray:
        """Apply character-specific and emotion-specific effects"""
        # Get character preset
        if character in ['sakura', 'cute']:
            preset = self.effect_presets['cute']
        elif character in ['yuki', 'soft']:
            preset = self.effect_presets['soft']
        elif character in ['miku', 'energetic']:
            preset = self.effect_presets['energetic']
        else:
            preset = self.effect_presets['cute']
        
        # Combine with emotion effects
        combined_effects = preset.copy()
        if emotion in self.emotion_effects:
            combined_effects.update(self.emotion_effects[emotion])
        
        return self._apply_effects(audio, combined_effects)
    
    def create_audio_variations(self, audio: np.ndarray, 
                              num_variations: int = 3) -> List[np.ndarray]:
        """Create variations of the same audio for different takes"""
        variations = []
        
        for i in range(num_variations):
            # Apply subtle random variations
            effects = {
                'pitch_shift': np.random.uniform(-0.05, 0.05),
                'brightness': np.random.uniform(-0.1, 0.1),
                'tempo_variation': np.random.uniform(0.95, 1.05)
            }
            
            varied_audio = self._apply_effects(audio, effects)
            variations.append(varied_audio)
        
        return variations
    
    def mix_with_background(self, voice_audio: np.ndarray, 
                          background_audio: np.ndarray = None,
                          voice_level: float = 0.8) -> np.ndarray:
        """Mix voice with background audio (music, ambience)"""
        if background_audio is None:
            return voice_audio
        
        # Ensure same length
        min_length = min(len(voice_audio), len(background_audio))
        voice_trimmed = voice_audio[:min_length]
        bg_trimmed = background_audio[:min_length]
        
        # Mix with specified levels
        mixed = voice_trimmed * voice_level + bg_trimmed * (1 - voice_level)
        
        return self._normalize_audio(mixed)
    
    def export_audio(self, audio: np.ndarray, filename: str, 
                    format: str = 'wav') -> bool:
        """Export audio to file"""
        try:
            if AUDIO_LIBS_AVAILABLE:
                sf.write(filename, audio, self.sample_rate)
            else:
                # Fallback: write as WAV
                audio_bytes = self._array_to_bytes(audio, 'wav')
                with open(filename, 'wb') as f:
                    f.write(audio_bytes)
            
            self.logger.info(f"Audio exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting audio: {e}")
            return False
    
    def get_audio_info(self, audio: np.ndarray) -> Dict[str, any]:
        """Get information about audio signal"""
        info = {
            'duration': len(audio) / self.sample_rate,
            'sample_rate': self.sample_rate,
            'samples': len(audio),
            'rms_level': np.sqrt(np.mean(audio**2)),
            'peak_level': np.max(np.abs(audio)),
            'dynamic_range': np.max(np.abs(audio)) - np.min(np.abs(audio))
        }
        
        # Add frequency analysis if librosa is available
        if AUDIO_LIBS_AVAILABLE:
            try:
                spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
                info['spectral_centroid_mean'] = np.mean(spectral_centroid)
                info['spectral_centroid_std'] = np.std(spectral_centroid)
            except:
                pass
        
        return info
