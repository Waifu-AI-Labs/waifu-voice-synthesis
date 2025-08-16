@echo off
echo 🌸 Starting Waifu Voice Synthesis API...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
if not exist "venv\installed.flag" (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 0 (
        echo. > venv\installed.flag
    ) else (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Download models if not present
if not exist "models\model_index.json" (
    echo 🤖 Setting up voice models...
    python scripts\download_models.py
)

REM Set environment variables
set FLASK_PORT=5001
set FLASK_DEBUG=False

REM Start the API server
echo 🚀 Starting API server on port %FLASK_PORT%...
echo.
echo Open your browser to: http://localhost:%FLASK_PORT%
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
