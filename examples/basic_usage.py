"""
Example usage of the Waifu Voice Synthesis system
"""

import sys
import json
from pathlib import Path

# Add the parent directory to the path to import waifu_voice
sys.path.append(str(Path(__file__).parent.parent))

from waifu_voice import WaifuVoiceSynthesizer

def basic_synthesis_example():
    """Basic synthesis example"""
    print("🌸 Basic Waifu Voice Synthesis Example")
    
    # Initialize synthesizer
    synthesizer = WaifuVoiceSynthesizer()
    
    # Example texts with different emotions
    examples = [
        {
            "text": "Konnichiwa! ♪ I'm so happy to meet you!",
            "character": "sakura",
            "emotion": "cheerful"
        },
        {
            "text": "Ehehe, that's really funny!",
            "character": "miku", 
            "emotion": "giggly"
        },
        {
            "text": "Ara ara~ You're quite interesting...",
            "character": "rei",
            "emotion": "teasing"
        },
        {
            "text": "Um... I'm a bit shy, but thank you...",
            "character": "yuki",
            "emotion": "shy"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n--- Example {i} ---")
        print(f"Text: {example['text']}")
        print(f"Character: {example['character']}")
        print(f"Emotion: {example['emotion']}")
        
        try:
            # Synthesize audio
            audio_data = synthesizer.synthesize(**example)
            
            # Save to file
            output_file = f"output_example_{i}.wav"
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            
            print(f"✅ Audio saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Synthesis failed: {e}")

def emotion_analysis_example():
    """Emotion analysis example"""
    print("\n🎭 Emotion Analysis Example")
    
    synthesizer = WaifuVoiceSynthesizer()
    
    texts = [
        "Wow! This is absolutely amazing! ♪",
        "Ara ara~ Someone is being quite bold today...",
        "Um... I don't know if I can do this...",
        "Ehehe! You're so funny, I can't stop giggling!",
        "I'm feeling a bit sad today..."
    ]
    
    for text in texts:
        print(f"\nText: '{text}'")
        
        try:
            analysis = synthesizer.analyze_text(text)
            
            print(f"Primary emotion: {analysis['emotions']['primary_emotion']}")
            print(f"Confidence: {analysis['emotions']['confidence']:.2f}")
            print(f"Recommended character: {analysis['recommended_character']}")
            print(f"Contains Japanese: {analysis['japanese_processing']['contains_japanese']}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")

def streaming_synthesis_example():
    """Streaming synthesis example"""
    print("\n🌊 Streaming Synthesis Example")
    
    synthesizer = WaifuVoiceSynthesizer()
    
    long_text = """
    Konnichiwa! Welcome to the world of waifu voice synthesis! 
    I'm Sakura, and I'm here to demonstrate how amazing this technology is. 
    Ehehe! Isn't it wonderful how we can generate cute anime voices? 
    Ara ara~ I hope you're enjoying this demonstration!
    """
    
    try:
        print("Generating streaming audio chunks...")
        chunk_count = 0
        
        for audio_chunk in synthesizer.synthesize_streaming(
            long_text, 
            character="sakura",
            emotion="auto"
        ):
            chunk_count += 1
            chunk_file = f"stream_chunk_{chunk_count}.wav"
            
            with open(chunk_file, 'wb') as f:
                f.write(audio_chunk)
            
            print(f"📦 Chunk {chunk_count} saved: {chunk_file}")
        
        print(f"✅ Streaming complete! Generated {chunk_count} chunks")
        
    except Exception as e:
        print(f"❌ Streaming failed: {e}")

def character_customization_example():
    """Character customization example"""
    print("\n👤 Character Customization Example")
    
    synthesizer = WaifuVoiceSynthesizer()
    
    # Create a custom character
    custom_character = {
        'name': 'Akane',
        'description': 'Fierce and determined waifu',
        'voice_style': 'energetic',
        'base_pitch': 1.1,
        'speaking_rate': 1.15,
        'energy': 1.3,
        'accent': 'japanese_medium',
        'personality_traits': ['determined', 'fierce', 'loyal']
    }
    
    try:
        # Register the custom character
        success = synthesizer.set_character_config('akane', custom_character)
        
        if success:
            print("✅ Custom character 'Akane' created successfully!")
            
            # Test the custom character
            audio_data = synthesizer.synthesize(
                "I won't give up! I'll keep fighting no matter what!",
                character="akane",
                emotion="determined"
            )
            
            with open("custom_character_example.wav", 'wb') as f:
                f.write(audio_data)
            
            print("🎵 Custom character audio saved: custom_character_example.wav")
            
        else:
            print("❌ Failed to create custom character")
            
    except Exception as e:
        print(f"❌ Character customization failed: {e}")

def api_integration_example():
    """Example of how to integrate with the API"""
    print("\n🌐 API Integration Example")
    
    # This would be used with the Flask API
    api_request_examples = [
        {
            "endpoint": "POST /synthesize",
            "payload": {
                "text": "Konnichiwa! ♪",
                "character": "sakura",
                "emotion": "cheerful",
                "voice_style": "cute",
                "output_format": "wav"
            }
        },
        {
            "endpoint": "POST /analyze",
            "payload": {
                "text": "Ara ara~ You're quite interesting..."
            }
        },
        {
            "endpoint": "GET /voices",
            "payload": {}
        }
    ]
    
    print("Example API requests:")
    for example in api_request_examples:
        print(f"\n{example['endpoint']}")
        if example['payload']:
            print(json.dumps(example['payload'], indent=2))

def main():
    """Run all examples"""
    print("🎌 Waifu Voice Synthesis Examples")
    print("=" * 40)
    
    try:
        basic_synthesis_example()
        emotion_analysis_example()
        streaming_synthesis_example()
        character_customization_example()
        api_integration_example()
        
        print("\n🎉 All examples completed!")
        print("\nNote: Audio files have been generated in the current directory.")
        print("In a production environment, these would contain actual synthesized audio.")
        
    except Exception as e:
        print(f"❌ Example execution failed: {e}")

if __name__ == '__main__':
    main()
