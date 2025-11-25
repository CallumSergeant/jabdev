#!/bin/bash

# JABchem CMS - Flask Server Startup Script

echo "JABchem CMS - Starting Flask Server"
echo "===================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your settings."
fi

# Start the server
echo ""
echo "Starting Flask server..."
cd server
python app.py
