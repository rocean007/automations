#!/bin/bash
set -e

echo "🔥 BRAINROT AUTOMATION SETUP 🔥"
echo "================================"
echo ""

echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version found"
echo ""

echo "📋 Checking ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg is installed"
else
    echo "❌ ffmpeg not found. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ffmpeg
    else
        echo "Please install ffmpeg manually"
        exit 1
    fi
fi
echo ""

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

if [ ! -f "config.yaml" ]; then
    echo "⚠️  config.yaml not found!"
    exit 1
fi

if [ ! -f "client_secrets.json" ]; then
    echo "⚠️  client_secrets.json not found!"
    echo "Download it from Google Cloud Console"
    exit 1
fi

char_count=$(find character_dataset -mindepth 1 -type d | wc -l)
if [ "$char_count" -eq 0 ]; then
    echo "⚠️  No characters in character_dataset/"
    exit 1
fi

echo "✅ Found $char_count characters"
echo ""
echo "🎉 SETUP COMPLETE!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your API keys"
echo "2. Run: python3 main.py"
echo "3. Or use Docker: docker-compose up -d"
