"""
Azure Speech Service Setup Script
Helps configure Azure credentials and test the connection
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from waifu_voice.azure_tts import AzureWaifuTTS

def setup_azure_credentials():
    """Interactive setup for Azure Speech credentials"""
    print("🌸 Azure Speech Service Setup for Waifu Voice Synthesis")
    print("=" * 60)
    
    print("\n📋 You'll need:")
    print("1. Azure Speech Service subscription key")
    print("2. Azure region (e.g., eastus, westus2, etc.)")
    print("\n🔗 Get these from: https://portal.azure.com -> Cognitive Services -> Speech")
    
    # Get credentials
    subscription_key = input("\n🔑 Enter your Azure Speech subscription key: ").strip()
    if not subscription_key:
        print("❌ Subscription key is required!")
        return False
    
    region = input("🌍 Enter your Azure region (default: eastus): ").strip()
    if not region:
        region = "eastus"
    
    # Test the connection
    print(f"\n🧪 Testing connection to Azure Speech Service in {region}...")
    
    azure_tts = AzureWaifuTTS(subscription_key=subscription_key, region=region)
    
    if azure_tts.test_connection():
        print("✅ Connection successful!")
        
        # Save to environment file
        env_file = Path(__file__).parent.parent / ".env"
        
        env_content = f"""# Azure Speech Service Configuration
AZURE_SPEECH_KEY={subscription_key}
AZURE_SPEECH_REGION={region}

# Flask Configuration
FLASK_PORT=5001
FLASK_DEBUG=False

# Voice Synthesis Configuration
DEFAULT_CHARACTER=sakura
ENABLE_AZURE_TTS=True
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"💾 Configuration saved to: {env_file}")
        print("\n🎉 Azure Speech Service is ready!")
        
        # Test voice synthesis
        test_synthesis = input("\n🎵 Test voice synthesis? (y/n): ").lower()
        if test_synthesis == 'y':
            test_waifu_voices(azure_tts)
        
        return True
        
    else:
        print("❌ Connection failed!")
        print("Please check your subscription key and region.")
        return False

def test_waifu_voices(azure_tts: AzureWaifuTTS):
    """Test different waifu character voices"""
    print("\n🎭 Testing Waifu Character Voices")
    print("-" * 40)
    
    test_cases = [
        {
            "character": "sakura",
            "emotion": "cheerful", 
            "text": "Konnichiwa! ♪ I'm Sakura and I'm so happy to meet you!"
        },
        {
            "character": "yuki", 
            "emotion": "shy",
            "text": "Um... hello... I'm Yuki... nice to meet you..."
        },
        {
            "character": "rei",
            "emotion": "teasing",
            "text": "Ara ara~ I'm Rei. You seem quite interesting..."
        },
        {
            "character": "miku",
            "emotion": "excited", 
            "text": "Yay! I'm Miku! This is so exciting!"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🎵 Test {i}: {test['character'].title()} ({test['emotion']})")
        print(f"Text: \"{test['text']}\"")
        
        try:
            audio_data = azure_tts.synthesize(
                text=test['text'],
                character=test['character'],
                emotion=test['emotion']
            )
            
            if len(audio_data) > 1000:  # Check if we got actual audio data
                filename = f"test_{test['character']}_{test['emotion']}.wav"
                with open(filename, 'wb') as f:
                    f.write(audio_data)
                print(f"✅ Audio generated: {filename}")
            else:
                print("⚠️ Generated audio seems too short")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

def check_existing_config():
    """Check if Azure is already configured"""
    env_file = Path(__file__).parent.parent / ".env"
    
    if env_file.exists():
        print("📋 Found existing configuration in .env file")
        
        # Try to load and test
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        key = os.environ.get('AZURE_SPEECH_KEY')
        region = os.environ.get('AZURE_SPEECH_REGION')
        
        if key and region:
            print(f"🔑 Key: {key[:8]}...")  # Show first 8 characters
            print(f"🌍 Region: {region}")
            
            azure_tts = AzureWaifuTTS(subscription_key=key, region=region)
            if azure_tts.test_connection():
                print("✅ Configuration is working!")
                return True
            else:
                print("❌ Configuration exists but connection failed")
                return False
        else:
            print("⚠️ Configuration file exists but missing Azure credentials")
            return False
    else:
        return False

def main():
    """Main setup function"""
    print("🌸 Waifu Voice Synthesis - Azure Setup")
    print("=" * 50)
    
    # Check for existing configuration
    if check_existing_config():
        reconfigure = input("\n🔄 Reconfigure Azure settings? (y/n): ").lower()
        if reconfigure != 'y':
            return
    
    # Setup new configuration
    if setup_azure_credentials():
        print("\n✨ Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Restart your API server if it's running")
        print("2. Test the API with: curl -X GET http://127.0.0.1:5000/")
        print("3. Try voice synthesis with the provided curl commands")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled.")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
