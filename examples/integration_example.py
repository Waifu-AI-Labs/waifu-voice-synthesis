"""
Integration example with waifu-chat-ollama
Shows how to connect the voice synthesis with your existing chat system
"""

import requests
import json
from pathlib import Path
import sys

# Add the parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

class WaifuChatVoiceIntegration:
    """Integration bridge between waifu-chat-ollama and voice synthesis"""
    
    def __init__(self, chat_api_url="http://localhost:5000", 
                 voice_api_url="http://localhost:5001"):
        self.chat_api_url = chat_api_url
        self.voice_api_url = voice_api_url
        
    def get_chat_response(self, message: str) -> dict:
        """Get response from waifu-chat-ollama"""
        try:
            response = requests.post(f"{self.chat_api_url}/chat", json={
                "message": message,
                "character": "Sakura"
            })
            return response.json()
        except Exception as e:
            print(f"Chat API error: {e}")
            return {"response": "Sorry, I couldn't process that.", "error": True}
    
    def synthesize_response(self, text: str, character="sakura") -> bytes:
        """Convert text response to voice"""
        try:
            response = requests.post(f"{self.voice_api_url}/synthesize", json={
                "text": text,
                "character": character,
                "emotion": "auto",
                "voice_style": "cute"
            })
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Voice synthesis error: {response.status_code}")
                return b""
                
        except Exception as e:
            print(f"Voice API error: {e}")
            return b""
    
    def chat_with_voice(self, user_message: str) -> tuple:
        """Complete chat interaction with voice output"""
        print(f"User: {user_message}")
        
        # Get chat response
        chat_response = self.get_chat_response(user_message)
        
        if "error" in chat_response:
            return chat_response.get("response", "Error"), b""
        
        sakura_text = chat_response.get("response", "")
        print(f"Sakura: {sakura_text}")
        
        # Convert to voice
        voice_data = self.synthesize_response(sakura_text)
        
        return sakura_text, voice_data

def integration_example():
    """Example of integrated chat with voice"""
    print("🌸 Waifu Chat + Voice Integration Example")
    print("=" * 50)
    
    integration = WaifuChatVoiceIntegration()
    
    # Example conversation
    conversation = [
        "Hello Sakura! How are you today?",
        "What's your favorite thing to do?", 
        "Can you tell me a joke?",
        "Thank you, you're so sweet!",
        "Bye Sakura!"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n--- Turn {i} ---")
        
        text_response, voice_data = integration.chat_with_voice(message)
        
        if voice_data:
            # Save voice response
            voice_file = f"sakura_response_{i}.wav"
            with open(voice_file, 'wb') as f:
                f.write(voice_data)
            print(f"🎵 Voice saved: {voice_file}")
        
        print("-" * 30)

def api_workflow_example():
    """Example workflow for API integration"""
    print("\n🔗 API Integration Workflow")
    
    workflow_steps = [
        {
            "step": 1,
            "description": "User sends message to chat API",
            "api_call": "POST /chat",
            "payload": {"message": "Hello!", "character": "Sakura"}
        },
        {
            "step": 2,
            "description": "Chat API returns response text", 
            "response": {"response": "Konnichiwa! ♪ I'm so happy to see you!"}
        },
        {
            "step": 3,
            "description": "Send response to voice synthesis API",
            "api_call": "POST /synthesize",
            "payload": {
                "text": "Konnichiwa! ♪ I'm so happy to see you!",
                "character": "sakura",
                "emotion": "auto"
            }
        },
        {
            "step": 4,
            "description": "Voice API returns audio data",
            "response": "Audio WAV file (binary data)"
        },
        {
            "step": 5,
            "description": "Play audio to user",
            "action": "Stream or play audio file"
        }
    ]
    
    for step in workflow_steps:
        print(f"\nStep {step['step']}: {step['description']}")
        if 'api_call' in step:
            print(f"  API: {step['api_call']}")
        if 'payload' in step:
            print(f"  Payload: {json.dumps(step['payload'], indent=4)}")
        if 'response' in step:
            print(f"  Response: {step['response']}")
        if 'action' in step:
            print(f"  Action: {step['action']}")

def web_interface_example():
    """Example of web interface integration"""
    html_example = '''
<!DOCTYPE html>
<html>
<head>
    <title>Waifu Chat with Voice</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <div id="chat-container">
        <div id="messages"></div>
        <input type="text" id="user-input" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <script>
        const socket = io('http://localhost:5001'); // Voice API WebSocket
        
        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value;
            
            // Send to chat API first
            fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message, character: 'Sakura'})
            })
            .then(response => response.json())
            .then(data => {
                displayMessage('User', message);
                displayMessage('Sakura', data.response);
                
                // Now synthesize voice
                socket.emit('synthesize_realtime', {
                    text: data.response,
                    character: 'sakura',
                    emotion: 'auto'
                });
            });
            
            input.value = '';
        }
        
        socket.on('audio_chunk', function(data) {
            // Play audio chunk
            const audio = new Audio();
            const blob = new Blob([new Uint8Array(data.data.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))], {type: 'audio/wav'});
            audio.src = URL.createObjectURL(blob);
            audio.play();
        });
        
        function displayMessage(sender, text) {
            const messages = document.getElementById('messages');
            messages.innerHTML += `<p><strong>${sender}:</strong> ${text}</p>`;
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
    '''
    
    print("\n🌐 Web Interface Integration Example")
    print("HTML/JavaScript example for real-time chat with voice:")
    print(html_example)

def main():
    """Run integration examples"""
    print("🎌 Waifu Chat + Voice Integration Examples")
    print("=" * 60)
    
    try:
        integration_example()
        api_workflow_example()
        web_interface_example()
        
        print("\n🎉 Integration examples completed!")
        print("\nTo use this integration:")
        print("1. Start your waifu-chat-ollama server on port 5000")
        print("2. Start the voice synthesis API on port 5001")
        print("3. Use the provided code to bridge between them")
        
    except Exception as e:
        print(f"❌ Integration example failed: {e}")

if __name__ == '__main__':
    main()
