#!/bin/bash

# LinkedIn Enricher Setup Script

echo "🚀 LinkedIn Lead Enricher - Setup Script"
echo "========================================"
echo ""

# Check Python version
echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "📁 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check .env file
echo "🔐 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template .env 2>/dev/null || echo "📝 Please copy .env.template to .env and add your API credentials"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit .env and add your RapidAPI credentials"
echo "  2. Run: python app.py"
echo "  3. Open: http://localhost:5000"
echo ""
echo "For detailed setup instructions, see README.md or QUICK_START.md"
