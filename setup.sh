#!/bin/bash

# Simple setup script for Parakeet Audio Transcriber
echo "🦜 Setting up Parakeet Audio Transcriber..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create virtual environment with uv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install requirements using uv
echo "Installing requirements with uv..."
uv pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the transcriber:"
echo "1. source .venv/bin/activate"
echo "2. python main.py"
echo ""
echo "Note: The first run will download the Parakeet model (~600MB)"
