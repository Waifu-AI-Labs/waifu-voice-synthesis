# 🎌 Waifu Voice Synthesis Pipeline

An advanced anime-style voice synthesis system using **Azure Neural TTS**, designed to generate high-quality waifu character voices with emotional expressions and Japanese accent support for your MVP applications.

## ✨ Features

� **Character-Specific Voices**
- Multiple anime character personalities (Sakura, Yuki, Rei, Miku)
- Unique voice characteristics and pitch adjustments
- Emotion-based voice modulation

💖 **Anime Expression Handling**
- Proper phonetic pronunciation of Japanese expressions
- Support for common anime phrases (ara ara~, ehehe, konnichiwa)
- Natural pauses and emphasis with SSML

⚡ **Azure Neural TTS Integration**
- High-quality neural voice synthesis
- English voices optimized for anime expressions
- Real-time audio generation

🔄 **RESTful API**
- Easy integration with existing chat systems
- JSON-based requests and responses
- Health monitoring and character management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Azure Cognitive Services Speech subscription
- Windows/Linux/macOS

### Installation
```bash
# Clone and navigate to the project
git clone <your-repo-url>
cd waifu-voice-synthesis

# Set up virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# source .venv/bin/activate    # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure Azure credentials
python scripts/setup_azure.py

```

The API will be available at `http://127.0.0.1:5001`

## 📚 API Documentation

### 🎵 Synthesize Voice
**POST** `/synthesize`

Generate anime-style voice audio from text.

```json
{
    "text": "Konnichiwa! Ara ara~ How are you today?",
    "character": "sakura",
    "emotion": "cheerful"
}
```

**Parameters:**
- `text` (string): Text to synthesize
- `character` (string): Character voice (`sakura`, `yuki`, `rei`, `miku`)
- `emotion` (string, optional): Emotion modifier (`cheerful`, `sad`, `excited`, `calm`)

**Response:** Audio file (WAV format)

### 🎭 Available Characters
**GET** `/characters`

Returns list of available character voices and their configurations.

### ❤️ Health Check  
**GET** `/health`

Returns API status and Azure TTS connectivity.

## 🎭 Character Voices

| Character | Voice Style | Personality | Best For |
|-----------|-------------|-------------|----------|
| **Sakura** | Sweet & Gentle | Cheerful, caring | Friendly conversations |
| **Yuki** | Cool & Elegant | Calm, sophisticated | Formal interactions |
| **Rei** | Mysterious | Quiet, thoughtful | Introspective moments |
| **Miku** | Energetic | Playful, upbeat | Exciting announcements |

## 🔧 Configuration

### Environment Setup
Create a `.env` file in the project root:

```env
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
FLASK_ENV=development
```

### Character Customization
Modify character voices in `waifu_voice/azure_tts.py`:

```python
character_voices = {
    'your_character': {
        'voice_name': 'en-US-AriaNeural',
        'pitch': '+15%',
        'rate': '+5%',
        'volume': '+10%'
    }
}
```

## 🎵 Anime Expression Support

The system automatically handles common anime expressions:

| Expression | Phonetic | Example Usage |
|------------|----------|---------------|
| `ara ara` | `ah-rah ah-rah` | "Ara ara~ What do we have here?" |
| `ehehe` | `eh-heh-heh` | "Ehehe, that's so funny!" |
| `ufufu` | `oo-foo-foo` | "Ufufu~ I have a secret!" |
| `kawaii` | `kah-wah-ee` | "That's so kawaii!" |
| `sugoi` | `soo-goh-ee` | "Sugoi! Amazing!" |

## 🔗 Integration Examples

### Python Client
```python
import requests

def synthesize_waifu_voice(text, character='sakura'):
    response = requests.post('http://127.0.0.1:5001/synthesize', 
                           json={
                               'text': text,
                               'character': character,
                               'emotion': 'cheerful'
                           })
    
    with open(f'{character}_voice.wav', 'wb') as f:
        f.write(response.content)

# Usage
synthesize_waifu_voice("Konnichiwa! ♪", "sakura")
```

### cURL Example
```bash
curl -X POST http://127.0.0.1:5001/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello! Nice to meet you!", "character": "sakura"}' \
  --output voice.wav
```

### JavaScript/Node.js
```javascript
const axios = require('axios');
const fs = require('fs');

async function synthesizeVoice(text, character = 'sakura') {
    const response = await axios.post('http://127.0.0.1:5001/synthesize', {
        text: text,
        character: character,
        emotion: 'cheerful'
    }, {
        responseType: 'arraybuffer'
    });
    
    fs.writeFileSync(`${character}_voice.wav`, response.data);
}
```

## 🛠️ Development

### Project Structure
```
waifu-voice-synthesis/
├── app.py                 # Flask API server
├── waifu_voice/
│   ├── __init__.py
│   ├── azure_tts.py      # Azure TTS integration  
│   └── synthesizer.py    # Main synthesis engine
├── scripts/
│   └── setup_azure.py    # Azure setup script
├── examples/
│   └── test_synthesis.py # Usage examples
├── requirements.txt      # Dependencies
├── .env.example         # Environment template
└── README.md           # This documentation
```

### Adding New Characters
1. Update `character_voices` in `azure_tts.py`
2. Add voice configuration parameters
3. Test with sample expressions
4. Update documentation

### Running Tests
```bash
python examples/test_synthesis.py
```

## 📋 Requirements

Core dependencies for your MVP:
- `azure-cognitiveservices-speech>=1.34.0`
- `flask>=2.3.3`
- `flask-cors>=4.0.0`
- `python-dotenv>=1.0.0`

## 🔍 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'azure'"**
- Run: `pip install azure-cognitiveservices-speech`

**"Invalid subscription key or region"**
- Verify your Azure credentials in `.env`
- Check Azure Speech Service region

**"Japanese voices sound bad for English text"**
- ✅ **Fixed**: System uses English Neural voices with anime-style pitch adjustments
- Japanese expressions are converted to phonetic pronunciations

### Debug Mode
Enable debug logging in your code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 MVP Integration

Perfect for integrating with your MVP applications:

- **waifu-chat-ollama**: Add voice responses to your waifu chat system
- **Discord bots**: Voice synthesis for anime character bots  
- **VTuber applications**: Real-time voice generation
- **Visual novels**: Character voice acting
- **AI assistants**: Anime-style voice responses

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Azure Cognitive Services for Neural TTS
- The anime community for inspiration
- Open source contributors

---

*Made with ❤️ for your MVP and the waifu community*

MIT License - Feel free to use in your waifu projects! 🌸
