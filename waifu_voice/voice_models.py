"""
Voice Model Management
Handles different voice models and character voices
"""

import os
import json
import torch
import torchaudio
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging


class VoiceModelManager:
    """Manages voice models for different waifu characters"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.loaded_models = {}
        self.model_configs = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Default character configurations
        self.character_configs = {
            'sakura': {
                'voice_style': 'cute',
                'base_pitch': 1.2,
                'speaking_rate': 1.0,
                'energy': 1.1,
                'accent': 'japanese_light',
                'personality_traits': ['cheerful', 'supportive', 'gentle']
            },
            'yuki': {
                'voice_style': 'soft',
                'base_pitch': 1.0,
                'speaking_rate': 0.9,
                'energy': 0.9,
                'accent': 'japanese_medium',
                'personality_traits': ['shy', 'sweet', 'thoughtful']
            },
            'rei': {
                'voice_style': 'cool',
                'base_pitch': 0.9,
                'speaking_rate': 0.8,
                'energy': 0.8,
                'accent': 'japanese_subtle',
                'personality_traits': ['calm', 'intelligent', 'mysterious']
            },
            'miku': {
                'voice_style': 'energetic',
                'base_pitch': 1.3,
                'speaking_rate': 1.2,
                'energy': 1.4,
                'accent': 'japanese_strong',
                'personality_traits': ['bubbly', 'excited', 'playful']
            }
        }
        
        self.voice_styles = {
            'cute': {
                'pitch_range': (1.1, 1.4),
                'formant_shift': 0.1,
                'breathiness': 0.3,
                'vibrato': 0.2
            },
            'soft': {
                'pitch_range': (0.9, 1.2),
                'formant_shift': 0.05,
                'breathiness': 0.4,
                'vibrato': 0.1
            },
            'cool': {
                'pitch_range': (0.8, 1.0),
                'formant_shift': -0.05,
                'breathiness': 0.1,
                'vibrato': 0.05
            },
            'energetic': {
                'pitch_range': (1.2, 1.5),
                'formant_shift': 0.15,
                'breathiness': 0.2,
                'vibrato': 0.3
            }
        }
        
        self.logger = logging.getLogger(__name__)
        
    def load_model(self, model_name: str) -> bool:
        """Load a voice synthesis model"""
        try:
            model_path = self.models_dir / f"{model_name}.pt"
            config_path = self.models_dir / f"{model_name}_config.json"
            
            if not model_path.exists():
                self.logger.warning(f"Model {model_name} not found, using default")
                return self._load_default_model(model_name)
            
            # Load model configuration
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.model_configs[model_name] = json.load(f)
            
            # Load the model (placeholder for actual model loading)
            # In a real implementation, this would load specific TTS models
            self.loaded_models[model_name] = {
                'type': 'neural_tts',
                'path': str(model_path),
                'loaded': True,
                'device': self.device
            }
            
            self.logger.info(f"Successfully loaded model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {e}")
            return False
    
    def _load_default_model(self, model_name: str) -> bool:
        """Load a default model configuration"""
        self.loaded_models[model_name] = {
            'type': 'default_tts',
            'path': None,
            'loaded': True,
            'device': self.device
        }
        
        self.model_configs[model_name] = {
            'sample_rate': 22050,
            'hop_length': 256,
            'win_length': 1024,
            'n_mel_channels': 80,
            'n_fft': 1024
        }
        
        return True
    
    def get_character_config(self, character_name: str) -> Dict[str, Any]:
        """Get configuration for a specific character"""
        return self.character_configs.get(character_name, 
                                         self.character_configs['sakura'])
    
    def get_voice_style_config(self, style_name: str) -> Dict[str, Any]:
        """Get configuration for a specific voice style"""
        return self.voice_styles.get(style_name, self.voice_styles['cute'])
    
    def list_available_models(self) -> List[str]:
        """List all available voice models"""
        models = []
        
        # Add loaded models
        models.extend(self.loaded_models.keys())
        
        # Add models found in directory
        for model_file in self.models_dir.glob("*.pt"):
            model_name = model_file.stem
            if model_name not in models:
                models.append(model_name)
        
        return models
    
    def list_characters(self) -> List[str]:
        """List all available character configurations"""
        return list(self.character_configs.keys())
    
    def list_voice_styles(self) -> List[str]:
        """List all available voice styles"""
        return list(self.voice_styles.keys())
    
    def generate_voice_parameters(self, character: str, emotion: str = 'neutral',
                                voice_style: Optional[str] = None) -> Dict[str, Any]:
        """Generate voice parameters for synthesis"""
        character_config = self.get_character_config(character)
        
        # Use character's default style if not specified
        if voice_style is None:
            voice_style = character_config['voice_style']
        
        style_config = self.get_voice_style_config(voice_style)
        
        # Base parameters from character
        parameters = {
            'pitch': character_config['base_pitch'],
            'speaking_rate': character_config['speaking_rate'],
            'energy': character_config['energy'],
            'accent': character_config['accent'],
            'character_name': character
        }
        
        # Apply voice style modifications
        parameters.update({
            'pitch_range': style_config['pitch_range'],
            'formant_shift': style_config['formant_shift'],
            'breathiness': style_config['breathiness'],
            'vibrato': style_config['vibrato']
        })
        
        # Apply emotion modifications
        emotion_modifiers = self._get_emotion_modifiers(emotion)
        for key, modifier in emotion_modifiers.items():
            if key in parameters:
                parameters[key] *= modifier
        
        return parameters
    
    def _get_emotion_modifiers(self, emotion: str) -> Dict[str, float]:
        """Get parameter modifiers for specific emotions"""
        modifiers = {
            'cheerful': {'pitch': 1.1, 'speaking_rate': 1.05, 'energy': 1.2},
            'giggly': {'pitch': 1.2, 'speaking_rate': 0.95, 'energy': 1.3},
            'teasing': {'pitch': 0.95, 'speaking_rate': 0.9, 'energy': 1.1},
            'shy': {'pitch': 1.05, 'speaking_rate': 0.8, 'energy': 0.8},
            'excited': {'pitch': 1.3, 'speaking_rate': 1.2, 'energy': 1.4},
            'sad': {'pitch': 0.85, 'speaking_rate': 0.7, 'energy': 0.6},
            'neutral': {'pitch': 1.0, 'speaking_rate': 1.0, 'energy': 1.0},
            'angry': {'pitch': 1.15, 'speaking_rate': 1.1, 'energy': 1.3},
            'surprised': {'pitch': 1.25, 'speaking_rate': 1.15, 'energy': 1.35}
        }
        
        return modifiers.get(emotion, modifiers['neutral'])
    
    def create_character_voice(self, name: str, config: Dict[str, Any]) -> bool:
        """Create a new character voice configuration"""
        try:
            self.character_configs[name] = config
            
            # Save configuration to file
            config_file = self.models_dir / f"character_{name}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Created character voice: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating character voice {name}: {e}")
            return False
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        if model_name not in self.loaded_models:
            return {'error': f'Model {model_name} not loaded'}
        
        info = {
            'name': model_name,
            'type': self.loaded_models[model_name]['type'],
            'loaded': self.loaded_models[model_name]['loaded'],
            'device': str(self.loaded_models[model_name]['device']),
            'config': self.model_configs.get(model_name, {})
        }
        
        return info
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            if model_name in self.model_configs:
                del self.model_configs[model_name]
            self.logger.info(f"Unloaded model: {model_name}")
            return True
        return False
    
    def optimize_for_character(self, character: str, text: str) -> Dict[str, Any]:
        """Optimize synthesis parameters for a specific character and text"""
        character_config = self.get_character_config(character)
        
        # Analyze text characteristics
        text_length = len(text)
        has_punctuation = any(p in text for p in '!?.')
        has_japanese = any(ord(c) > 127 for c in text)
        
        # Adjust parameters based on text
        parameters = self.generate_voice_parameters(character)
        
        if text_length > 100:
            parameters['speaking_rate'] *= 0.95  # Slower for long text
        
        if has_punctuation:
            parameters['energy'] *= 1.1  # More expressive
        
        if has_japanese:
            parameters['accent'] = character_config['accent']
            parameters['pitch'] *= 1.05  # Slightly higher for Japanese
        
        return parameters
