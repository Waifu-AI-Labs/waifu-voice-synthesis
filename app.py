"""
Waifu Voice Synthesis API Server
Clean Azure Neural TTS implementation for anime voice synthesis
"""

import os
import logging
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv

from waifu_voice.azure_tts import AzureWaifuTTS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'waifu-voice-synthesis-secret')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Enable CORS
CORS(app, origins=['*'])

# Initialize Azure TTS
try:
    azure_tts = AzureWaifuTTS()
    logger.info("Azure TTS initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Azure TTS: {e}")
    azure_tts = None

# API Routes

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Waifu Voice Synthesis API (Azure Neural TTS)',
        'version': '1.0.0',
        'azure_tts_ready': azure_tts is not None and azure_tts.azure_available
    })

@app.route('/synthesize', methods=['POST'])
def synthesize_voice():
    """
    Main voice synthesis endpoint using Azure Neural TTS
    
    Expected JSON payload:
    {
        "text": "Konnichiwa! ♪",
        "character": "sakura",
        "emotion": "cheerful"
    }
    """
    try:
        if not azure_tts or not azure_tts.azure_available:
            return jsonify({'error': 'Azure TTS not available. Please configure AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.'}), 500
        
        # Parse request
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required "text" field'}), 400
        
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Extract synthesis parameters
        character = data.get('character', 'sakura')
        emotion = data.get('emotion', 'cheerful')
        
        logger.info(f"Synthesizing: '{text[:50]}...' for character: {character} ({emotion})")
        
        # Synthesize audio with Azure
        audio_data = azure_tts.synthesize(
            text=text,
            character=character,
            emotion=emotion
        )
        
        # Return audio response
        response = Response(audio_data, mimetype='audio/wav')
        response.headers['Content-Disposition'] = f'attachment; filename="{character}_{emotion}.wav"'
        
        return response
        
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return jsonify({'error': f'Synthesis failed: {str(e)}'}), 500

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voices and characters"""
    try:
        if not azure_tts:
            return jsonify({'error': 'Azure TTS not available'}), 500
        
        voices = azure_tts.get_available_voices()
        
        return jsonify({
            'characters': voices['characters'],
            'emotions': voices['emotions'],
            'azure_available': voices['azure_available'],
            'japanese_expressions': voices['japanese_expressions']
        })
        
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        return jsonify({'error': 'Failed to list voices'}), 500

@app.route('/test', methods=['POST'])
def test_azure():
    """Test Azure connection"""
    try:
        if not azure_tts:
            return jsonify({'error': 'Azure TTS not initialized'}), 500
        
        success = azure_tts.test_connection()
        
        return jsonify({
            'azure_connection': success,
            'message': 'Connection successful' if success else 'Connection failed'
        })
        
    except Exception as e:
        logger.error(f"Azure test error: {e}")
        return jsonify({'error': f'Test failed: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Waifu Voice Synthesis API on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    if not azure_tts or not azure_tts.azure_available:
        logger.warning("⚠️ Azure TTS not configured! Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables.")
        logger.info("Run: python scripts/setup_azure.py to configure Azure credentials.")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
