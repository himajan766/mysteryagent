#!/bin/bash

# Murder Mystery Game - Web UI Launcher

echo "🕵️‍♂️ Starting Murder Mystery Web Application 🔍"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  OPENAI_API_KEY environment variable not set!"
    echo "You can set it now or enter it in the web interface."
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    if [ ! -z "$api_key" ]; then
        export OPENAI_API_KEY=$api_key
    fi
fi

echo ""
echo "🚀 Launching web application..."
echo "The app will open in your browser automatically."
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Run streamlit
streamlit run web_app.py
