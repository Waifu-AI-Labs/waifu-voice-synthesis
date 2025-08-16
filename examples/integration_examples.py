"""
🎌 Waifu Voice Synthesis - Integration Examples

This file demonstrates various ways to integrate the waifu voice synthesis
API into your MVP applications.
"""

import requests
import base64
import json
import asyncio
import aiohttp
import hashlib
import os
from typing import Optional, Dict, Any
import time

# Configuration
API_BASE_URL = "http://127.0.0.1:5001"
CACHE_DIR = "voice_cache"

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class WaifuVoiceClient:
    """
    Simple client for waifu voice synthesis API.
    Perfect for MVP applications.
    """
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def synthesize(self, text: str, character: str = "sakura", emotion: str = "cheerful") -> Optional[bytes]:
        """
        Synthesize voice from text.
        
        Args:
            text: Text to synthesize
            character: Character voice (sakura, yuki, rei, miku)
            emotion: Emotion modifier (cheerful, sad, excited, calm)
            
        Returns:
            Audio data as bytes, or None if failed
        """
        try:
            response = self.session.post(
                f"{self.base_url}/synthesize",
                json={
                    "text": text,
                    "character": character,
                    "emotion": emotion
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def get_characters(self) -> Dict[str, Any]:
        """Get available character voices."""
        try:
            response = self.session.get(f"{self.base_url}/characters", timeout=self.timeout)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            print(f"Failed to get characters: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


class CachedWaifuVoiceClient(WaifuVoiceClient):
    """
    Enhanced client with caching for MVP performance.
    Cache commonly used phrases to reduce API calls.
    """
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = 10, cache_dir: str = CACHE_DIR):
        super().__init__(base_url, timeout)
        self.cache_dir = cache_dir
    
    def _get_cache_key(self, text: str, character: str, emotion: str) -> str:
        """Generate cache key for given parameters."""
        content = f"{text}_{character}_{emotion}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path."""
        return os.path.join(self.cache_dir, f"{cache_key}.wav")
    
    def synthesize(self, text: str, character: str = "sakura", emotion: str = "cheerful") -> Optional[bytes]:
        """Synthesize with caching."""
        # Check cache first
        cache_key = self._get_cache_key(text, character, emotion)
        cache_path = self._get_cache_path(cache_key)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                return f.read()
        
        # Generate new audio
        audio_data = super().synthesize(text, character, emotion)
        
        # Cache for future use
        if audio_data:
            try:
                with open(cache_path, 'wb') as f:
                    f.write(audio_data)
            except Exception as e:
                print(f"Failed to cache audio: {e}")
        
        return audio_data


class AsyncWaifuVoiceClient:
    """
    Async client for non-blocking voice synthesis.
    Great for web applications and real-time systems.
    """
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = 10):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def synthesize(self, text: str, character: str = "sakura", emotion: str = "cheerful") -> Optional[bytes]:
        """Async voice synthesis."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/synthesize",
                    json={
                        "text": text,
                        "character": character,
                        "emotion": emotion
                    }
                ) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        print(f"API Error: {response.status}")
                        return None
        except Exception as e:
            print(f"Async request failed: {e}")
            return None


# =============================================================================
# MVP INTEGRATION EXAMPLES
# =============================================================================

def example_1_basic_chat_bot():
    """
    Example 1: Basic Chat Bot Integration
    
    Shows how to add voice to a simple chat bot.
    """
    print("🤖 Example 1: Basic Chat Bot")
    
    client = WaifuVoiceClient()
    
    # Simulate chat responses
    responses = [
        "Hello! Welcome to our chat service ♪",
        "How can I help you today?",
        "That's interesting! Tell me more~",
        "Ara ara~ I see what you mean!",
        "Thanks for chatting with me! Have a great day ♪"
    ]
    
    for i, response in enumerate(responses):
        print(f"Bot: {response}")
        
        # Generate voice
        audio = client.synthesize(response, "sakura", "cheerful")
        
        if audio:
            # Save audio file
            filename = f"chat_response_{i+1}.wav"
            with open(filename, 'wb') as f:
                f.write(audio)
            print(f"🎵 Voice saved to: {filename}")
        else:
            print("❌ Voice generation failed")
        
        print("-" * 50)


def example_2_character_personality_showcase():
    """
    Example 2: Character Personality Showcase
    
    Demonstrates different characters saying the same phrase.
    """
    print("🎭 Example 2: Character Personalities")
    
    client = WaifuVoiceClient()
    text = "Welcome to our application! I hope you enjoy your experience here ♪"
    
    characters = ["sakura", "yuki", "rei", "miku"]
    
    for character in characters:
        print(f"{character.title()}: {text}")
        
        audio = client.synthesize(text, character, "cheerful")
        if audio:
            filename = f"personality_{character}.wav"
            with open(filename, 'wb') as f:
                f.write(audio)
            print(f"🎵 {character.title()}'s voice saved to: {filename}")
        
        print("-" * 50)


def example_3_emotional_responses():
    """
    Example 3: Emotional Response System
    
    Shows how to match emotions with appropriate voices.
    """
    print("💖 Example 3: Emotional Responses")
    
    client = WaifuVoiceClient()
    
    scenarios = [
        ("User completed a task", "Sugoi! You did amazing! ♪", "excited"),
        ("User made a mistake", "Ara ara~ Don't worry, everyone makes mistakes!", "calm"),
        ("User is leaving", "Aww, you're leaving already? Take care! ♪", "sad"),
        ("User achieved something", "Congratulations! I'm so proud of you!", "cheerful")
    ]
    
    for scenario, response, emotion in scenarios:
        print(f"Scenario: {scenario}")
        print(f"Response: {response}")
        print(f"Emotion: {emotion}")
        
        audio = client.synthesize(response, "sakura", emotion)
        if audio:
            filename = f"emotion_{emotion}_response.wav"
            with open(filename, 'wb') as f:
                f.write(audio)
            print(f"🎵 Emotional response saved to: {filename}")
        
        print("-" * 50)


def example_4_educational_content():
    """
    Example 4: Educational Content with Voice
    
    Perfect for e-learning platforms and educational apps.
    """
    print("📚 Example 4: Educational Content")
    
    client = WaifuVoiceClient()
    
    lessons = [
        ("Introduction", "Hello students! Welcome to today's lesson. Let's learn something new together ♪"),
        ("Explanation", "This concept is quite important. Let me explain it step by step."),
        ("Example", "Here's a practical example to help you understand better."),
        ("Conclusion", "Great job! You've completed this lesson. I'm proud of your progress!")
    ]
    
    for lesson_type, content in lessons:
        print(f"Lesson Part: {lesson_type}")
        print(f"Content: {content}")
        
        # Use Yuki for educational content (professional voice)
        audio = client.synthesize(content, "yuki", "calm")
        if audio:
            filename = f"lesson_{lesson_type.lower()}.wav"
            with open(filename, 'wb') as f:
                f.write(audio)
            print(f"🎵 Lesson audio saved to: {filename}")
        
        print("-" * 50)


def example_5_gaming_integration():
    """
    Example 5: Gaming Integration
    
    Shows how to add waifu voices to game events.
    """
    print("🎮 Example 5: Gaming Integration")
    
    client = WaifuVoiceClient()
    
    game_events = [
        ("level_up", "Level up! You're getting stronger! ♪", "excited"),
        ("item_found", "Ooh! You found a rare item! Lucky you~", "cheerful"),
        ("boss_defeated", "Incredible! You defeated the boss! Sugoi!", "excited"),
        ("game_over", "Ara ara~ Game over! But don't give up!", "calm"),
        ("achievement", "Achievement unlocked! You're amazing! ♪", "cheerful")
    ]
    
    for event, message, emotion in game_events:
        print(f"Game Event: {event}")
        print(f"Message: {message}")
        
        # Use Miku for gaming (energetic voice)
        audio = client.synthesize(message, "miku", emotion)
        if audio:
            filename = f"game_{event}.wav"
            with open(filename, 'wb') as f:
                f.write(audio)
            print(f"🎵 Game audio saved to: {filename}")
        
        print("-" * 50)


def example_6_customer_service():
    """
    Example 6: Customer Service Integration
    
    Professional yet friendly customer service responses.
    """
    print("📞 Example 6: Customer Service")
    
    client = WaifuVoiceClient()
    
    service_responses = [
        ("greeting", "Hello! Thank you for contacting our support team. How may I assist you today?", "cheerful"),
        ("hold", "Please hold on for just a moment while I look that up for you.", "calm"),
        ("solution", "I found a solution for your issue! Let me walk you through it.", "cheerful"),
        ("apology", "I sincerely apologize for the inconvenience. Let me make this right.", "calm"),
        ("closing", "Is there anything else I can help you with today? Have a wonderful day! ♪", "cheerful")
    ]
    
    for response_type, message, emotion in service_responses:
        print(f"Service Type: {response_type}")
        print(f"Response: {message}")
        
        # Use Sakura for customer service (friendly and caring)
        audio = client.synthesize(message, "sakura", emotion)
        if audio:
            filename = f"service_{response_type}.wav"
            with open(filename, 'wb') as f:
                f.write(audio)
            print(f"🎵 Service audio saved to: {filename}")
        
        print("-" * 50)


async def example_7_async_integration():
    """
    Example 7: Async Integration
    
    Shows how to use async client for better performance.
    """
    print("⚡ Example 7: Async Integration")
    
    client = AsyncWaifuVoiceClient()
    
    # Simulate multiple concurrent requests
    texts = [
        "Hello! Welcome to our async service!",
        "Processing your request in the background~",
        "Multiple operations running simultaneously!",
        "Async programming makes everything faster ♪"
    ]
    
    # Generate all voices concurrently
    start_time = time.time()
    
    tasks = []
    for i, text in enumerate(texts):
        task = client.synthesize(text, "sakura", "cheerful")
        tasks.append((i, task))
    
    # Wait for all to complete
    results = await asyncio.gather(*[task for _, task in tasks])
    
    end_time = time.time()
    print(f"Generated {len(texts)} voices in {end_time - start_time:.2f} seconds")
    
    # Save results
    for i, audio_data in enumerate(results):
        if audio_data:
            filename = f"async_voice_{i+1}.wav"
            with open(filename, 'wb') as f:
                f.write(audio_data)
            print(f"🎵 Async voice saved to: {filename}")


def example_8_caching_performance():
    """
    Example 8: Caching for Performance
    
    Demonstrates caching for common phrases.
    """
    print("🚀 Example 8: Caching Performance")
    
    client = CachedWaifuVoiceClient()
    
    # Common phrases that would benefit from caching
    common_phrases = [
        "Welcome back!",
        "Thank you!",
        "Please wait a moment~",
        "Have a great day! ♪",
        "How can I help you?"
    ]
    
    print("First generation (uncached):")
    start_time = time.time()
    
    for phrase in common_phrases:
        audio = client.synthesize(phrase, "sakura", "cheerful")
        if audio:
            print(f"✅ Generated: {phrase}")
    
    first_time = time.time() - start_time
    print(f"Time taken: {first_time:.2f} seconds")
    
    print("\nSecond generation (cached):")
    start_time = time.time()
    
    for phrase in common_phrases:
        audio = client.synthesize(phrase, "sakura", "cheerful")
        if audio:
            print(f"⚡ Cached: {phrase}")
    
    second_time = time.time() - start_time
    print(f"Time taken: {second_time:.2f} seconds")
    print(f"Speed improvement: {(first_time / second_time):.1f}x faster!")


def example_9_error_handling():
    """
    Example 9: Robust Error Handling
    
    Shows how to handle errors gracefully in MVP applications.
    """
    print("🛡️ Example 9: Error Handling")
    
    client = WaifuVoiceClient()
    
    def safe_voice_synthesis(text: str, character: str = "sakura", fallback_message: str = None) -> tuple:
        """
        Safe voice synthesis with error handling.
        
        Returns:
            (success: bool, audio_data: bytes, message: str)
        """
        try:
            # Check if API is healthy first
            if not client.health_check():
                return False, None, "Voice API is not available"
            
            audio = client.synthesize(text, character, "cheerful")
            
            if audio:
                return True, audio, "Voice generated successfully"
            else:
                return False, None, "Voice generation failed"
                
        except Exception as e:
            error_msg = f"Error during voice synthesis: {e}"
            return False, None, error_msg
    
    # Test with various scenarios
    test_cases = [
        ("Hello! This should work fine.", "sakura"),
        ("Test with unknown character.", "unknown_character"),
        ("", "sakura"),  # Empty text
        ("A" * 1000, "sakura")  # Very long text
    ]
    
    for text, character in test_cases:
        print(f"Testing: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"Character: {character}")
        
        success, audio, message = safe_voice_synthesis(text, character)
        
        if success:
            filename = f"safe_test_{hash(text) % 1000}.wav"
            with open(filename, 'wb') as f:
                f.write(audio)
            print(f"✅ {message} - Saved to: {filename}")
        else:
            print(f"❌ {message}")
        
        print("-" * 50)


def example_10_web_integration():
    """
    Example 10: Web Application Integration
    
    Shows how to integrate with web frameworks like Flask/FastAPI.
    """
    print("🌐 Example 10: Web Integration Helper")
    
    def create_voice_response(text: str, character: str = "sakura") -> dict:
        """
        Create a web-friendly response with voice data.
        
        Returns JSON-serializable response for web APIs.
        """
        client = WaifuVoiceClient()
        
        response = {
            "text": text,
            "character": character,
            "timestamp": time.time(),
            "has_voice": False,
            "audio_base64": None,
            "error": None
        }
        
        try:
            audio = client.synthesize(text, character, "cheerful")
            
            if audio:
                # Convert to base64 for JSON transport
                response["audio_base64"] = base64.b64encode(audio).decode('utf-8')
                response["has_voice"] = True
            else:
                response["error"] = "Voice generation failed"
                
        except Exception as e:
            response["error"] = str(e)
        
        return response
    
    # Example web responses
    web_responses = [
        "Welcome to our website! ♪",
        "Your order has been confirmed!",
        "Thank you for subscribing to our newsletter~",
        "Error: Please check your input and try again."
    ]
    
    for text in web_responses:
        response = create_voice_response(text)
        
        print(f"Text: {text}")
        print(f"Has Voice: {response['has_voice']}")
        if response['error']:
            print(f"Error: {response['error']}")
        
        # Save as JSON for web consumption
        filename = f"web_response_{hash(text) % 1000}.json"
        with open(filename, 'w') as f:
            # Don't save the large base64 audio in the demo file
            demo_response = response.copy()
            if demo_response['audio_base64']:
                demo_response['audio_base64'] = f"<base64_audio_{len(response['audio_base64'])}_chars>"
            
            json.dump(demo_response, f, indent=2)
        print(f"💾 Web response saved to: {filename}")
        print("-" * 50)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run all examples."""
    print("🎌 Waifu Voice Synthesis - Integration Examples")
    print("=" * 60)
    
    # Check if API is available
    client = WaifuVoiceClient()
    if not client.health_check():
        print("❌ API is not available. Please start the voice synthesis server first:")
        print("   python app.py")
        return
    
    print("✅ API is healthy! Running examples...")
    print()
    
    # Run all examples
    examples = [
        example_1_basic_chat_bot,
        example_2_character_personality_showcase,
        example_3_emotional_responses,
        example_4_educational_content,
        example_5_gaming_integration,
        example_6_customer_service,
        # Skip async example in sync context
        example_8_caching_performance,
        example_9_error_handling,
        example_10_web_integration
    ]
    
    for example_func in examples:
        try:
            example_func()
            print("✅ Example completed successfully!")
        except Exception as e:
            print(f"❌ Example failed: {e}")
        
        print("\n" + "=" * 60 + "\n")
    
    print("🎉 All examples completed!")
    print("\nGenerated audio files:")
    wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]
    for wav_file in wav_files:
        print(f"  🎵 {wav_file}")


async def run_async_example():
    """Run the async example separately."""
    print("Running async example...")
    await example_7_async_integration()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "async":
        # Run async example
        asyncio.run(run_async_example())
    else:
        # Run all sync examples
        main()
