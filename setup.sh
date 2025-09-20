#!/bin/bash

# Birthday Scoreboard Setup Script
echo "🎉 Birthday Scoreboard Setup"
echo "============================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📋 Python version: $PYTHON_VERSION"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python database.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run the app: python app.py"
echo ""
echo "🐳 Or use Docker:"
echo "   ./run.sh start"
echo ""
echo "🌐 The app will be available at: http://localhost:8080"