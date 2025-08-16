"""
Emotion Detection Module
Analyzes text for emotional context to inform voice synthesis
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import numpy as np
from textblob import TextBlob


class EmotionDetector:
    """Detects emotions and expressions in text for voice synthesis"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.emotion_patterns = self._load_emotion_patterns()
        self.japanese_expressions = self._load_japanese_expressions()
        self.emotion_weights = {
            'cheerful': {'pitch': 1.2, 'speed': 1.1, 'energy': 1.3},
            'giggly': {'pitch': 1.3, 'speed': 0.9, 'energy': 1.4}, 
            'teasing': {'pitch': 0.9, 'speed': 0.8, 'energy': 1.1},
            'shy': {'pitch': 1.1, 'speed': 0.7, 'energy': 0.8},
            'excited': {'pitch': 1.4, 'speed': 1.3, 'energy': 1.5},
            'sad': {'pitch': 0.8, 'speed': 0.6, 'energy': 0.6},
            'neutral': {'pitch': 1.0, 'speed': 1.0, 'energy': 1.0}
        }
    
    def _load_emotion_patterns(self) -> Dict[str, List[str]]:
        """Load emotion detection patterns"""
        return {
            'cheerful': [
                r'!(.*?)!', r'\♪', r'yay', r'awesome', r'great', r'wonderful',
                r'happy', r'joy', r'smile', r'laugh'
            ],
            'giggly': [
                r'ehehe', r'hehe', r'hihi', r'ufufu', r'funny', r'lol',
                r'haha', r'giggle', r'tehe'
            ],
            'teasing': [
                r'ara ara', r'ara~', r'ohh?', r'really\?', r'is that so',
                r'hmm~', r'interesting', r'~$'
            ],
            'shy': [
                r'um+', r'uh+', r'maybe', r'perhaps', r'i think',
                r'sort of', r'kind of', r'blush', r'embarrass'
            ],
            'excited': [
                r'wow!+', r'amazing!+', r'incredible!+', r'fantastic!+',
                r'YES!+', r'OMG', r'can\'t wait'
            ],
            'sad': [
                r'sad', r'cry', r'tears', r'sorry', r'hurt', r'pain',
                r'disappointed', r'upset'
            ]
        }
    
    def _load_japanese_expressions(self) -> Dict[str, str]:
        """Load Japanese expression mappings"""
        return {
            'konnichiwa': {'emotion': 'cheerful', 'pronunciation': 'kon-ni-chi-wa'},
            'ohayo': {'emotion': 'cheerful', 'pronunciation': 'o-ha-yo'},
            'arigatou': {'emotion': 'grateful', 'pronunciation': 'a-ri-ga-to-u'},
            'sumimasen': {'emotion': 'shy', 'pronunciation': 'su-mi-ma-sen'},
            'ara ara': {'emotion': 'teasing', 'pronunciation': 'a-ra a-ra'},
            'ehehe': {'emotion': 'giggly', 'pronunciation': 'e-he-he'},
            'ufufu': {'emotion': 'giggly', 'pronunciation': 'u-fu-fu'},
            'baka': {'emotion': 'teasing', 'pronunciation': 'ba-ka'},
            'kawaii': {'emotion': 'excited', 'pronunciation': 'ka-wa-ii'},
            'sugoi': {'emotion': 'excited', 'pronunciation': 'su-go-i'},
            'onegai': {'emotion': 'pleading', 'pronunciation': 'o-ne-gai'},
            'gomen': {'emotion': 'apologetic', 'pronunciation': 'go-men'}
        }
    
    def detect_emotion(self, text: str) -> Dict[str, any]:
        """
        Detect emotions in text and return synthesis parameters
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing emotion info and voice parameters
        """
        text_lower = text.lower()
        detected_emotions = {}
        
        # Pattern-based emotion detection
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            matches = []
            
            for pattern in patterns:
                pattern_matches = re.findall(pattern, text_lower)
                if pattern_matches:
                    score += len(pattern_matches) * 1.0
                    matches.extend(pattern_matches)
            
            if score > 0:
                detected_emotions[emotion] = {
                    'score': score,
                    'matches': matches
                }
        
        # Japanese expression detection
        japanese_emotions = self._detect_japanese_expressions(text_lower)
        if japanese_emotions:
            detected_emotions.update(japanese_emotions)
        
        # Sentiment analysis fallback
        if not detected_emotions:
            sentiment = TextBlob(text).sentiment
            if sentiment.polarity > 0.3:
                detected_emotions['cheerful'] = {'score': sentiment.polarity, 'matches': []}
            elif sentiment.polarity < -0.3:
                detected_emotions['sad'] = {'score': abs(sentiment.polarity), 'matches': []}
            else:
                detected_emotions['neutral'] = {'score': 1.0, 'matches': []}
        
        # Select primary emotion
        primary_emotion = max(detected_emotions.keys(), 
                            key=lambda x: detected_emotions[x]['score'])
        
        # Generate voice parameters
        voice_params = self._generate_voice_parameters(primary_emotion, detected_emotions)
        
        return {
            'primary_emotion': primary_emotion,
            'all_emotions': detected_emotions,
            'voice_parameters': voice_params,
            'confidence': detected_emotions[primary_emotion]['score']
        }
    
    def _detect_japanese_expressions(self, text: str) -> Dict[str, any]:
        """Detect Japanese expressions and their emotions"""
        japanese_emotions = {}
        
        for expression, info in self.japanese_expressions.items():
            if expression in text:
                emotion = info['emotion']
                if emotion not in japanese_emotions:
                    japanese_emotions[emotion] = {
                        'score': 2.0,  # Higher weight for Japanese expressions
                        'matches': []
                    }
                japanese_emotions[emotion]['matches'].append(expression)
                japanese_emotions[emotion]['score'] += 1.0
        
        return japanese_emotions
    
    def _generate_voice_parameters(self, primary_emotion: str, 
                                 all_emotions: Dict) -> Dict[str, float]:
        """Generate voice synthesis parameters based on detected emotions"""
        base_params = self.emotion_weights.get(primary_emotion, 
                                             self.emotion_weights['neutral'])
        
        # Blend multiple emotions if present
        if len(all_emotions) > 1:
            total_score = sum(emotion['score'] for emotion in all_emotions.values())
            blended_params = {'pitch': 0, 'speed': 0, 'energy': 0}
            
            for emotion_name, emotion_data in all_emotions.items():
                weight = emotion_data['score'] / total_score
                emotion_params = self.emotion_weights.get(emotion_name, 
                                                        self.emotion_weights['neutral'])
                
                for param in blended_params:
                    blended_params[param] += emotion_params[param] * weight
            
            return blended_params
        
        return base_params.copy()
    
    def get_pronunciation_guide(self, text: str) -> List[Tuple[str, str]]:
        """Get pronunciation guides for Japanese expressions"""
        pronunciation_guides = []
        
        for expression, info in self.japanese_expressions.items():
            if expression in text.lower():
                pronunciation_guides.append((expression, info['pronunciation']))
        
        return pronunciation_guides
    
    def analyze_speech_patterns(self, text: str) -> Dict[str, any]:
        """Analyze speech patterns for voice synthesis"""
        analysis = {
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'ellipsis_count': text.count('...'),
            'tilde_count': text.count('~'),
            'has_japanese': bool(re.search(r'[ひらがなカタカナ漢字]', text)),
            'average_word_length': len(text.split()) / max(1, len(text.split())),
            'emoticon_count': len(re.findall(r'[(\[<]?[>:;=8xX][\-o\*\']?[\)\]\>DdPp\(\(\)\[\]\{\}<>oO0\|\\\/]', text))
        }
        
        # Speech rhythm indicators
        if analysis['exclamation_count'] > 1:
            analysis['speech_rhythm'] = 'energetic'
        elif analysis['ellipsis_count'] > 0:
            analysis['speech_rhythm'] = 'thoughtful'
        elif analysis['question_count'] > 0:
            analysis['speech_rhythm'] = 'curious'
        else:
            analysis['speech_rhythm'] = 'normal'
            
        return analysis
