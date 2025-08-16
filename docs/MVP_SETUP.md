# 🚀 MVP Setup Guide - Waifu Voice Synthesis

Quick setup guide for integrating waifu voice synthesis into your MVP application.

## ⚡ 5-Minute Setup

Perfect for MVP developers who need anime voice synthesis up and running quickly.

### Step 1: Prerequisites ✅
- Python 3.11+
- Azure account with Speech Services
- 5 minutes of your time

### Step 2: Get Azure Credentials 🔑

1. Go to [Azure Portal](https://portal.azure.com)
2. Create "Speech Services" resource
3. Copy your **Key** and **Region**
4. That's it! No complex setup needed.

### Step 3: Quick Install 📦

```bash
# Clone the repository
git clone <your-repo-url>
cd waifu-voice-synthesis

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies (takes ~2 minutes)
pip install -r requirements.txt

# Set up Azure credentials
python scripts/setup_azure.py
# Just paste your Azure key and region when prompted
```

### Step 4: Start Your Voice API 🎵

```bash
# Start the server
python app.py

# ✅ Done! API running on http://127.0.0.1:5001
```

### Step 5: Test Your Setup 🧪

```bash
# Quick test
curl -X POST http://127.0.0.1:5001/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello! I am your waifu assistant!", "character": "sakura"}' \
  --output test.wav

# Play the audio file to hear your waifu voice!
```

## 🔌 MVP Integration Examples

### Option 1: Python Integration (Recommended)

Perfect if your MVP is in Python:

```python
import requests

def add_voice_to_response(text, character="sakura"):
    """Add voice to any text response in your MVP."""
    response = requests.post('http://127.0.0.1:5001/synthesize', 
                           json={
                               'text': text,
                               'character': character,
                               'emotion': 'cheerful'
                           })
    return response.content  # Audio data

# Use in your MVP
user_message = "How are you today?"
bot_response = "I'm doing great! Thanks for asking ♪"
voice_audio = add_voice_to_response(bot_response)

# Save or stream the audio
with open('response.wav', 'wb') as f:
    f.write(voice_audio)
```

### Option 2: REST API Integration

For any programming language:

```javascript
// JavaScript/Node.js example
async function addWaifuVoice(text) {
    const response = await fetch('http://127.0.0.1:5001/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            character: 'sakura',
            emotion: 'cheerful'
        })
    });
    
    return await response.arrayBuffer();
}

// Usage in your MVP
const voiceData = await addWaifuVoice("Welcome to my application!");
```

### Option 3: Command Line Integration

For any system that can run shell commands:

```bash
# Create a simple voice generation script
echo '#!/bin/bash
curl -s -X POST http://127.0.0.1:5001/synthesize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$1\", \"character\": \"sakura\"}" \
  --output "$2"' > generate_voice.sh

# Use it anywhere
./generate_voice.sh "Hello user!" greeting.wav
```

## 🎭 Character Selection for Your MVP

Choose the right character for your use case:

### **Sakura** 🌸 (Recommended for most MVPs)
- **Personality**: Friendly, caring
- **Best for**: Customer service, general assistance
- **Voice**: Sweet and gentle
- **Example**: "Welcome! How can I help you today?"

### **Yuki** ❄️ (Professional MVPs)
- **Personality**: Calm, sophisticated  
- **Best for**: Business apps, formal responses
- **Voice**: Cool and elegant
- **Example**: "Your report has been generated successfully."

### **Miku** 🎵 (Fun/Gaming MVPs)
- **Personality**: Energetic, playful
- **Best for**: Games, entertainment apps
- **Voice**: Upbeat and exciting
- **Example**: "Congratulations! You've unlocked a new feature!"

### **Rei** 🌙 (Unique/Artsy MVPs)
- **Personality**: Mysterious, thoughtful
- **Best for**: Creative apps, philosophical content
- **Voice**: Quiet and contemplative
- **Example**: "Interesting... let me think about that."

## 💡 MVP Use Cases

### Chat Applications
```python
# Add voice to chat responses
def send_message_with_voice(text):
    # Generate voice
    voice = add_voice_to_response(text, "sakura")
    
    # Send both text and voice to user
    return {
        "text": text,
        "audio": base64.encode(voice),
        "character": "sakura"
    }
```

### Educational Apps
```python
# Voice explanations
def explain_concept(concept, explanation):
    voice_explanation = add_voice_to_response(
        f"Let me explain {concept}. {explanation}", 
        "yuki"  # Professional voice for education
    )
    return voice_explanation
```

### Gaming/Entertainment
```python
# Character interactions
def game_response(action, result):
    responses = {
        "win": "Sugoi! You did amazing! ♪",
        "lose": "Ara ara~ Better luck next time!",
        "level_up": "Congratulations! You leveled up!"
    }
    
    text = responses.get(result, "Keep going!")
    return add_voice_to_response(text, "miku")  # Energetic voice
```

### Customer Service
```python
# Friendly assistance
def customer_greeting():
    greetings = [
        "Hello! Welcome to our service ♪",
        "Good day! How can I assist you today?",
        "Welcome! I'm here to help you~"
    ]
    
    text = random.choice(greetings)
    return add_voice_to_response(text, "sakura")
```

## 🔧 Configuration for MVPs

### Minimal Configuration

Create a simple config file for your MVP:

```python
# config.py
WAIFU_VOICE_CONFIG = {
    "api_url": "http://127.0.0.1:5001",
    "default_character": "sakura",
    "default_emotion": "cheerful",
    "timeout": 10,  # seconds
    "retry_attempts": 3
}

# Helper function
def get_voice(text, character=None):
    import requests
    
    character = character or WAIFU_VOICE_CONFIG["default_character"]
    
    try:
        response = requests.post(
            f"{WAIFU_VOICE_CONFIG['api_url']}/synthesize",
            json={
                "text": text,
                "character": character,
                "emotion": WAIFU_VOICE_CONFIG["default_emotion"]
            },
            timeout=WAIFU_VOICE_CONFIG["timeout"]
        )
        return response.content if response.status_code == 200 else None
    except:
        return None  # Graceful fallback for MVP
```

### Error Handling for MVP

```python
def robust_voice_synthesis(text, character="sakura"):
    """MVP-friendly voice synthesis with fallbacks."""
    try:
        # Try to get voice
        voice_data = get_voice(text, character)
        if voice_data:
            return voice_data
    except:
        pass
    
    # Fallback: Return None, let your MVP handle text-only
    print(f"Voice synthesis failed for: {text}")
    return None

# Usage in your MVP
def send_response(text):
    voice = robust_voice_synthesis(text)
    
    response = {"text": text}
    if voice:
        response["audio"] = base64.b64encode(voice).decode()
        response["has_voice"] = True
    else:
        response["has_voice"] = False
    
    return response
```

## 📊 Performance Considerations for MVP

### Caching Strategy
```python
import hashlib
import os

CACHE_DIR = "voice_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached_voice(text, character):
    """Cache voices for common phrases in your MVP."""
    # Create cache key
    cache_key = hashlib.md5(f"{text}_{character}".encode()).hexdigest()
    cache_file = f"{CACHE_DIR}/{cache_key}.wav"
    
    # Return cached if exists
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return f.read()
    
    # Generate and cache
    voice_data = get_voice(text, character)
    if voice_data:
        with open(cache_file, 'wb') as f:
            f.write(voice_data)
    
    return voice_data
```

### Async Processing for Better UX
```python
import asyncio
import aiohttp

async def async_voice_synthesis(text, character="sakura"):
    """Non-blocking voice synthesis for your MVP."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://127.0.0.1:5001/synthesize",
            json={"text": text, "character": character}
        ) as response:
            if response.status == 200:
                return await response.read()
            return None

# Usage
async def handle_user_message(message):
    # Process message immediately
    text_response = generate_response(message)
    
    # Start voice generation in background
    voice_task = asyncio.create_task(
        async_voice_synthesis(text_response)
    )
    
    # Send text response immediately
    send_text_response(text_response)
    
    # Add voice when ready
    voice_data = await voice_task
    if voice_data:
        send_voice_response(voice_data)
```

## 🚀 Production Readiness

When your MVP is ready to scale:

### 1. Environment Variables
```bash
# .env for production
AZURE_SPEECH_KEY=your_production_key
AZURE_SPEECH_REGION=your_region
FLASK_ENV=production
VOICE_API_URL=https://your-domain.com/voice
```

### 2. Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["python", "app.py"]
```

### 3. Load Balancing
```yaml
# docker-compose.yml for scaling
version: '3.8'
services:
  voice-api:
    build: .
    ports:
      - "5001-5003:5001"
    environment:
      - AZURE_SPEECH_KEY=${AZURE_SPEECH_KEY}
      - AZURE_SPEECH_REGION=${AZURE_SPEECH_REGION}
    deploy:
      replicas: 3
```

## 📝 MVP Checklist

- [ ] ✅ Azure credentials configured
- [ ] ✅ API server running locally  
- [ ] ✅ Basic voice synthesis working
- [ ] ✅ Character voices tested
- [ ] ✅ Integration code written
- [ ] ✅ Error handling implemented
- [ ] ✅ Caching for common phrases
- [ ] 🔄 Performance optimization
- [ ] 🔄 Production deployment plan

## 🆘 Quick Troubleshooting

**API not responding?**
```bash
# Check if server is running
curl http://127.0.0.1:5001/health
```

**Azure authentication issues?**
```bash
# Re-run setup script
python scripts/setup_azure.py
```

**Voice quality issues?**
```python
# Try different characters
voice = get_voice("Hello!", "yuki")  # More formal
voice = get_voice("Hello!", "miku")  # More energetic
```

**Integration not working?**
```python
# Test with minimal example
import requests
response = requests.post("http://127.0.0.1:5001/synthesize", 
                        json={"text": "test", "character": "sakura"})
print(response.status_code, len(response.content))
```

## 📞 Support

Need help with your MVP integration?

1. **Check the API docs**: `/docs/API.md`
2. **Test with curl**: Verify basic functionality
3. **Review examples**: Use the provided code snippets
4. **Start simple**: Get basic synthesis working first

---

*Happy building! Your waifu-powered MVP awaits! 🎌✨*
