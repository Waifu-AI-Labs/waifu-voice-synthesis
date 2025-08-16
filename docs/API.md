# 📘 Waifu Voice Synthesis API Documentation

Complete API reference for the Waifu Voice Synthesis Pipeline.

## Base URL
```
http://127.0.0.1:5001
```

## Authentication
Currently no authentication required. For production use, implement API key authentication.

## Endpoints

### 🎵 Voice Synthesis

#### POST /synthesize
Synthesize anime-style voice from text input.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "text": "string (required) - Text to synthesize",
    "character": "string (required) - Character voice ID",
    "emotion": "string (optional) - Emotion modifier"
}
```

**Example Request:**
```json
{
    "text": "Konnichiwa! Ara ara~ How wonderful to meet you!",
    "character": "sakura",
    "emotion": "cheerful"
}
```

**Response:**
- **Status Code:** 200 OK
- **Content-Type:** audio/wav
- **Body:** Binary WAV audio data

**Error Responses:**
```json
// 400 Bad Request
{
    "error": "Missing required field: text"
}

// 500 Internal Server Error
{
    "error": "Azure TTS service unavailable"
}
```

---

### 🎭 Character Management

#### GET /characters
Get list of available character voices and their configurations.

**Response:**
```json
{
    "characters": {
        "sakura": {
            "name": "Sakura",
            "voice_name": "en-US-JennyNeural",
            "description": "Sweet & gentle character voice",
            "personality": "Cheerful, caring",
            "pitch": "+20%",
            "rate": "+5%",
            "volume": "+10%"
        },
        "yuki": {
            "name": "Yuki", 
            "voice_name": "en-US-AriaNeural",
            "description": "Cool & elegant character voice",
            "personality": "Calm, sophisticated",
            "pitch": "+15%",
            "rate": "+0%",
            "volume": "+5%"
        },
        "rei": {
            "name": "Rei",
            "voice_name": "en-US-SaraNeural", 
            "description": "Mysterious character voice",
            "personality": "Quiet, thoughtful",
            "pitch": "+10%",
            "rate": "-5%",
            "volume": "+0%"
        },
        "miku": {
            "name": "Miku",
            "voice_name": "en-US-AmberNeural",
            "description": "Energetic character voice", 
            "personality": "Playful, upbeat",
            "pitch": "+25%",
            "rate": "+10%",
            "volume": "+15%"
        }
    }
}
```

---

### ❤️ Health Check

#### GET /health
Check API status and Azure TTS service connectivity.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-08-16T10:30:00Z",
    "azure_tts": "connected",
    "version": "1.0.0"
}
```

**Error Response:**
```json
{
    "status": "unhealthy",
    "timestamp": "2025-08-16T10:30:00Z", 
    "azure_tts": "disconnected",
    "error": "Azure credentials not configured"
}
```

## Character Voice IDs

| Character ID | Name | Personality | Voice Description |
|--------------|------|-------------|-------------------|
| `sakura` | Sakura | Cheerful, caring | Sweet and gentle voice |
| `yuki` | Yuki | Calm, sophisticated | Cool and elegant voice |
| `rei` | Rei | Quiet, thoughtful | Mysterious voice |
| `miku` | Miku | Playful, upbeat | Energetic voice |

## Emotion Modifiers

| Emotion | Effect | Best Used With |
|---------|--------|----------------|
| `cheerful` | Higher pitch, faster rate | Happy expressions |
| `sad` | Lower pitch, slower rate | Melancholy moments |
| `excited` | Much higher pitch, faster rate | Energetic announcements |
| `calm` | Neutral adjustments | Peaceful conversations |

## Anime Expression Handling

The API automatically converts Japanese expressions to phonetic pronunciations for better English TTS:

### Supported Expressions

| Original | Converted | Pronunciation |
|----------|-----------|---------------|
| `ara ara` | `ah-rah ah-rah` | /ɑː.ɹɑː ɑː.ɹɑː/ |
| `ehehe` | `eh-heh-heh` | /ɛ.hɛ.hɛ/ |
| `ufufu` | `oo-foo-foo` | /uː.fuː.fuː/ |
| `kawaii` | `kah-wah-ee` | /kɑː.wɑː.iː/ |
| `sugoi` | `soo-goh-ee` | /suː.ɡoʊ.iː/ |
| `desu` | `dess` | /dɛs/ |
| `nani` | `nah-nee` | /nɑː.niː/ |

### Special Characters & Sounds

| Symbol | Effect | Example |
|--------|--------|---------|
| `♪` | Musical pause | "Hello♪" → "Hello [pause] ♪ [pause]" |
| `~` | Extended sound with pause | "Ara ara~" → "Ara ara~ [pause]" |
| `!` | Emphasis with short pause | "Kawaii!" → "Kawaii [pause]!" |
| `?` | Question intonation with pause | "Really?" → "Really [pause]?" |

## SSML Features

The API uses SSML (Speech Synthesis Markup Language) for enhanced voice control:

### Automatic SSML Generation

```xml
<!-- Input: "Ara ara~ That's so kawaii!" -->
<!-- Generated SSML: -->
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="en-US-JennyNeural">
        <prosody pitch="+20%" rate="+5%" volume="+10%">
            <emphasis level="strong">ah-rah ah-rah</emphasis>
            <break time="400ms"/>~ That's so 
            <emphasis level="strong">kah-wah-ee</emphasis>
            <break time="200ms"/>!
        </prosody>
    </voice>
</speak>
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful, audio returned |
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Server Error | Azure TTS or server error |
| 503 | Service Unavailable | Azure TTS service down |

### Error Response Format

```json
{
    "error": "string - Error description",
    "code": "string - Error code (optional)",
    "timestamp": "string - ISO 8601 timestamp"
}
```

## Rate Limiting

Currently no rate limiting implemented. For production:
- Recommended: 100 requests per minute per IP
- Consider implementing API key-based quotas

## Audio Format Specifications

### Output Format
- **Format:** WAV (Waveform Audio File Format)
- **Sample Rate:** 24kHz
- **Bit Depth:** 16-bit
- **Channels:** Mono
- **Codec:** PCM

### File Size Estimates
- Short phrase (5-10 words): ~50-100KB
- Medium text (20-30 words): ~150-300KB  
- Long text (50+ words): ~400KB+

## SDK Examples

### Python SDK Usage

```python
import requests
import io
from pydub import AudioSegment

class WaifuVoiceClient:
    def __init__(self, base_url="http://127.0.0.1:5001"):
        self.base_url = base_url
    
    def synthesize(self, text, character="sakura", emotion="cheerful"):
        """Synthesize voice and return audio data."""
        response = requests.post(
            f"{self.base_url}/synthesize",
            json={
                "text": text,
                "character": character,
                "emotion": emotion
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def get_characters(self):
        """Get available characters."""
        response = requests.get(f"{self.base_url}/characters")
        return response.json()
    
    def save_audio(self, audio_data, filename):
        """Save audio data to file."""
        with open(filename, 'wb') as f:
            f.write(audio_data)

# Usage example
client = WaifuVoiceClient()
audio = client.synthesize("Konnichiwa! Nice to meet you!", "sakura", "cheerful")
client.save_audio(audio, "greeting.wav")
```

### Node.js SDK Usage

```javascript
const axios = require('axios');
const fs = require('fs');

class WaifuVoiceClient {
    constructor(baseUrl = 'http://127.0.0.1:5001') {
        this.baseUrl = baseUrl;
    }
    
    async synthesize(text, character = 'sakura', emotion = 'cheerful') {
        try {
            const response = await axios.post(`${this.baseUrl}/synthesize`, {
                text: text,
                character: character,
                emotion: emotion
            }, {
                responseType: 'arraybuffer',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            return response.data;
        } catch (error) {
            throw new Error(`API Error: ${error.response?.status} - ${error.message}`);
        }
    }
    
    async getCharacters() {
        const response = await axios.get(`${this.baseUrl}/characters`);
        return response.data;
    }
    
    saveAudio(audioData, filename) {
        fs.writeFileSync(filename, audioData);
    }
}

// Usage example
const client = new WaifuVoiceClient();

(async () => {
    const audio = await client.synthesize("Ara ara~ How are you?", "sakura", "cheerful");
    client.saveAudio(audio, "greeting.wav");
})();
```

## Best Practices

### Text Input Optimization

1. **Keep text concise**: 50-200 characters work best
2. **Use anime expressions**: "Ara ara~", "Ehehe!", "Kawaii!"
3. **Include emotional indicators**: "♪", "~", "!", "?"
4. **Mix English and romanized Japanese**: Natural for anime characters

### Character Selection

- **Sakura**: Friendly greetings, caring responses
- **Yuki**: Formal announcements, sophisticated dialogue  
- **Rei**: Mysterious comments, thoughtful responses
- **Miku**: Excited announcements, playful interactions

### Performance Optimization

- **Cache audio files**: Save frequently used phrases
- **Batch requests**: Group multiple synthesis calls
- **Monitor Azure quotas**: Track usage and costs
- **Implement retry logic**: Handle temporary service issues

## Troubleshooting

### Common Integration Issues

**Audio not playing:**
```javascript
// Ensure proper audio format handling
const audio = new Audio();
audio.src = URL.createObjectURL(new Blob([audioData], { type: 'audio/wav' }));
audio.play();
```

**CORS issues in browser:**
```javascript
// API includes CORS headers, but verify:
headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}
```

**Large file handling:**
```python
# For long text, split into chunks:
def synthesize_long_text(text, chunk_size=100):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    audio_files = []
    
    for chunk in chunks:
        audio = client.synthesize(chunk)
        audio_files.append(audio)
    
    # Combine audio files using pydub or similar
    return combine_audio(audio_files)
```

## Support

For technical support:
1. Check the troubleshooting section
2. Review error logs in the API server
3. Verify Azure TTS service status
4. Test with minimal example requests

---

*API Version: 1.0.0 | Last Updated: August 16, 2025*
