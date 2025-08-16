"""
Japanese Text Processor
Handles Japanese text processing, romanization, and pronunciation
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional
import logging

try:
    import jaconv
    JACONV_AVAILABLE = True
except ImportError:
    JACONV_AVAILABLE = False
    logging.warning("jaconv not available, limited Japanese processing")


class JapaneseTextProcessor:
    """Processes Japanese text for voice synthesis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common Japanese expressions and their romanizations
        self.expression_dict = {
            'こんにちは': 'konnichiwa',
            'おはよう': 'ohayou',
            'ありがとう': 'arigatou',
            'すみません': 'sumimasen',
            'あらあら': 'ara ara',
            'えへへ': 'ehehe',
            'うふふ': 'ufufu',
            'ばか': 'baka',
            'かわいい': 'kawaii',
            'すごい': 'sugoi',
            'おねがい': 'onegai',
            'ごめん': 'gomen',
            'はい': 'hai',
            'いいえ': 'iie',
            'だめ': 'dame',
            'やった': 'yatta',
            'きゃー': 'kyaa',
            'えー': 'ee',
            'うん': 'un',
            'ううん': 'uun',
            'そうですね': 'sou desu ne',
            'なるほど': 'naruhodo',
            'おいしい': 'oishii',
            'たのしい': 'tanoshii',
            'きれい': 'kirei',
            'すてき': 'suteki',
            'だいすき': 'daisuki',
            'がんばって': 'ganbatte'
        }
        
        # Romanization mapping for individual characters
        self.hiragana_to_romaji = {
            'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
            'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
            'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
            'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
            'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
            'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
            'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
            'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
            'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
            'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
            'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
            'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
            'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
            'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
            'わ': 'wa', 'ゐ': 'wi', 'ゑ': 'we', 'を': 'wo', 'ん': 'n',
            'ー': '-', '〜': '~', '！': '!', '？': '?', '。': '.', '、': ','
        }
        
        # Katakana to hiragana mapping for processing
        self.katakana_to_hiragana = str.maketrans(
            'アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデド'
            'ナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨラリルレロワヲン'
            'ァィゥェォッャュョー',
            'あいうえおかきくけこがぎぐげごさしすせそざじずぜぞたちつてとだぢづでど'
            'なにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよらりるれろわをん'
            'ぁぃぅぇぉっゃゅょー'
        )
        
        # Common Japanese particles and their pronunciation
        self.particles = {
            'は': 'wa',  # topic marker
            'を': 'o',   # object marker
            'へ': 'e'    # direction marker
        }
        
        # Accent patterns for common words
        self.accent_patterns = {
            'konnichiwa': [0, 3, 0, 0, 0],  # pitch accent pattern
            'arigatou': [0, 0, 3, 0, 0],
            'ohayou': [0, 3, 0, 0],
            'kawaii': [0, 3, 0, 0],
            'sugoi': [0, 3, 0]
        }
    
    def contains_japanese(self, text: str) -> bool:
        """Check if text contains Japanese characters"""
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs
            (0xFF65, 0xFF9F),  # Half-width Katakana
        ]
        
        for char in text:
            code = ord(char)
            for start, end in japanese_ranges:
                if start <= code <= end:
                    return True
        return False
    
    def extract_japanese_text(self, text: str) -> List[str]:
        """Extract Japanese text segments from mixed text"""
        japanese_pattern = r'[ひらがなカタカナ漢字々〆〤ヶ]+'
        matches = re.findall(japanese_pattern, text)
        return matches
    
    def romanize_text(self, text: str) -> str:
        """Convert Japanese text to romanized form"""
        if not self.contains_japanese(text):
            return text
        
        # First check for complete expressions
        for japanese, romaji in self.expression_dict.items():
            if japanese in text:
                text = text.replace(japanese, romaji)
        
        # Convert katakana to hiragana for processing
        if JACONV_AVAILABLE:
            text = jaconv.kata2hira(text)
        else:
            text = text.translate(self.katakana_to_hiragana)
        
        # Romanize remaining characters
        result = ""
        i = 0
        while i < len(text):
            char = text[i]
            
            # Handle particles specially
            if char in self.particles:
                result += self.particles[char]
            elif char in self.hiragana_to_romaji:
                result += self.hiragana_to_romaji[char]
            else:
                result += char
            i += 1
        
        return result
    
    def add_pronunciation_marks(self, text: str) -> str:
        """Add pronunciation marks for better TTS"""
        # Add pauses after particles
        text = re.sub(r'(wa|ga|o|ni|de|to|kara)\s', r'\1, ', text)
        
        # Add emphasis markers
        text = re.sub(r'(ara ara|ehehe|kawaii|sugoi)', r'<emphasis>\1</emphasis>', text)
        
        # Add breathing pauses
        text = re.sub(r'([.!?])\s*', r'\1<break time="0.5s"/>', text)
        
        return text
    
    def generate_ssml(self, text: str, voice_params: Dict) -> str:
        """Generate SSML markup for Japanese text"""
        # Start with basic SSML structure
        ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ja-JP">'
        
        # Add voice selection if specified
        if 'voice_name' in voice_params:
            ssml += f'<voice name="{voice_params["voice_name"]}">'
        
        # Add prosody controls
        prosody_attrs = []
        if 'pitch' in voice_params:
            pitch_val = f"{voice_params['pitch']:+.0%}"
            prosody_attrs.append(f'pitch="{pitch_val}"')
        if 'speaking_rate' in voice_params:
            rate_val = f"{voice_params['speaking_rate']:.1f}"
            prosody_attrs.append(f'rate="{rate_val}"')
        if 'energy' in voice_params:
            volume_val = f"{voice_params['energy']:+.0%}"
            prosody_attrs.append(f'volume="{volume_val}"')
        
        if prosody_attrs:
            ssml += f'<prosody {" ".join(prosody_attrs)}>'
        
        # Process text for pronunciation
        processed_text = self.add_pronunciation_marks(text)
        
        # Handle Japanese expressions specially
        for expression, romaji in self.expression_dict.items():
            if expression in processed_text:
                # Add phoneme information
                phoneme_markup = f'<phoneme alphabet="x-sampa" ph="{self._get_sampa(romaji)}">{expression}</phoneme>'
                processed_text = processed_text.replace(expression, phoneme_markup)
        
        ssml += processed_text
        
        # Close tags
        if prosody_attrs:
            ssml += '</prosody>'
        if 'voice_name' in voice_params:
            ssml += '</voice>'
        ssml += '</speak>'
        
        return ssml
    
    def _get_sampa(self, romaji: str) -> str:
        """Convert romaji to X-SAMPA phonemes (simplified)"""
        sampa_mapping = {
            'a': 'a', 'i': 'i', 'u': 'M', 'e': 'e', 'o': 'o',
            'ka': 'ka', 'ki': 'ki', 'ku': 'kM', 'ke': 'ke', 'ko': 'ko',
            'sa': 'sa', 'shi': 'Si', 'su': 'sM', 'se': 'se', 'so': 'so',
            'ta': 'ta', 'chi': 'tSi', 'tsu': 'tsM', 'te': 'te', 'to': 'to',
            'na': 'na', 'ni': 'ni', 'nu': 'nM', 'ne': 'ne', 'no': 'no',
            'ha': 'ha', 'hi': 'Ci', 'fu': 'FM', 'he': 'he', 'ho': 'ho',
            'ma': 'ma', 'mi': 'mi', 'mu': 'mM', 'me': 'me', 'mo': 'mo',
            'ya': 'ja', 'yu': 'jM', 'yo': 'jo',
            'ra': 'ra', 'ri': 'ri', 'ru': 'rM', 're': 're', 'ro': 'ro',
            'wa': 'wa', 'wo': 'wo', 'n': 'N'
        }
        
        # Simple conversion - in real implementation would be more sophisticated
        result = ""
        for syllable in romaji.split():
            if syllable in sampa_mapping:
                result += sampa_mapping[syllable] + " "
            else:
                result += syllable + " "
        
        return result.strip()
    
    def analyze_accent_pattern(self, text: str) -> List[int]:
        """Analyze pitch accent patterns for Japanese text"""
        words = text.split()
        accent_pattern = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in self.accent_patterns:
                accent_pattern.extend(self.accent_patterns[word_lower])
            else:
                # Default pattern: high-low for most words
                pattern = [0] + [3] + [0] * (len(word) - 2)
                accent_pattern.extend(pattern)
        
        return accent_pattern
    
    def preprocess_for_tts(self, text: str, target_language: str = 'ja') -> Dict[str, any]:
        """Preprocess text for TTS synthesis"""
        result = {
            'original_text': text,
            'contains_japanese': self.contains_japanese(text),
            'romanized_text': '',
            'pronunciation_guide': [],
            'accent_pattern': [],
            'ssml_ready': False
        }
        
        if result['contains_japanese']:
            result['romanized_text'] = self.romanize_text(text)
            result['pronunciation_guide'] = self._get_pronunciation_guide(text)
            result['accent_pattern'] = self.analyze_accent_pattern(result['romanized_text'])
        else:
            result['romanized_text'] = text
            result['accent_pattern'] = [0] * len(text.split())
        
        return result
    
    def _get_pronunciation_guide(self, text: str) -> List[Dict[str, str]]:
        """Get detailed pronunciation guide for Japanese text"""
        guide = []
        
        for expression, romaji in self.expression_dict.items():
            if expression in text:
                guide.append({
                    'japanese': expression,
                    'romaji': romaji,
                    'ipa': self._romaji_to_ipa(romaji),
                    'meaning': self._get_meaning(expression)
                })
        
        return guide
    
    def _romaji_to_ipa(self, romaji: str) -> str:
        """Convert romaji to IPA notation (simplified)"""
        ipa_mapping = {
            'a': 'a', 'i': 'i', 'u': 'ɯ', 'e': 'e', 'o': 'o',
            'ka': 'ka', 'ki': 'ki', 'ku': 'kɯ', 'ke': 'ke', 'ko': 'ko',
            'ga': 'ɡa', 'gi': 'ɡi', 'gu': 'ɡɯ', 'ge': 'ɡe', 'go': 'ɡo',
            'sa': 'sa', 'shi': 'ʃi', 'su': 'sɯ', 'se': 'se', 'so': 'so',
            'ta': 'ta', 'chi': 'tʃi', 'tsu': 'tsɯ', 'te': 'te', 'to': 'to',
            'na': 'na', 'ni': 'ni', 'nu': 'nɯ', 'ne': 'ne', 'no': 'no',
            'ha': 'ha', 'hi': 'çi', 'fu': 'ɸɯ', 'he': 'he', 'ho': 'ho',
            'ma': 'ma', 'mi': 'mi', 'mu': 'mɯ', 'me': 'me', 'mo': 'mo',
            'ya': 'ja', 'yu': 'jɯ', 'yo': 'jo',
            'ra': 'ɾa', 'ri': 'ɾi', 'ru': 'ɾɯ', 're': 'ɾe', 'ro': 'ɾo',
            'wa': 'wa', 'wo': 'wo', 'n': 'n'
        }
        
        result = ""
        for char in romaji:
            if char in ipa_mapping:
                result += ipa_mapping[char]
            else:
                result += char
        
        return result
    
    def _get_meaning(self, expression: str) -> str:
        """Get English meaning of Japanese expression"""
        meanings = {
            'こんにちは': 'hello',
            'おはよう': 'good morning',
            'ありがとう': 'thank you',
            'あらあら': 'oh my',
            'えへへ': 'giggle',
            'かわいい': 'cute',
            'すごい': 'amazing'
        }
        return meanings.get(expression, 'unknown')
