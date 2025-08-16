#!/bin/bash
echo "🌸 Starting Waifu Voice Synthesis API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/installed.flag" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/installed.flag
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Download models if not present
if [ ! -f "models/model_index.json" ]; then
    echo "🤖 Setting up voice models..."
    python scripts/download_models.py
fi

# Set environment variables
export FLASK_PORT=5001
export FLASK_DEBUG=False

# Start the API server
echo "🚀 Starting API server on port $FLASK_PORT..."
echo ""
echo "Open your browser to: http://localhost:$FLASK_PORT"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
