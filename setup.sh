#!/bin/bash

# LLM Data Visualizer - Complete Setup Script
# This script sets up the entire Django application

set -e  # Exit on error

echo "🚀 LLM Data Visualizer - Setup Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    print_status "Python $python_version detected"
else
    print_error "Python 3.11+ required, found $python_version"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_status "Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    print_status ".env file created"
    print_warning "Please update .env with your settings if needed"
else
    print_warning ".env file already exists"
fi

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
print_status "Database migrations complete"

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --no-input > /dev/null
print_status "Static files collected"

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p media/uploads
mkdir -p logs
print_status "Directories created"

# Check if Ollama is running
echo ""
echo "Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_status "Ollama is running and accessible"
    
    # List available models
    models=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; data = json.load(sys.stdin); print('\n'.join([m['name'] for m in data.get('models', [])]))" 2>/dev/null || echo "")
    
    if [ -n "$models" ]; then
        echo ""
        echo "Available Ollama models:"
        echo "$models" | while read -r model; do
            echo "  • $model"
        done
    else
        print_warning "No models found. Pull a model with: ollama pull llama3.2"
    fi
else
    print_warning "Ollama not detected. Please install and start Ollama:"
    echo "  1. Visit https://ollama.ai"
    echo "  2. Install Ollama"
    echo "  3. Run: ollama serve"
    echo "  4. Pull a model: ollama pull llama3.2"
fi

echo ""
echo "======================================"
print_status "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Start the server: python manage.py runserver"
echo "  3. Open http://localhost:8000/"
echo "  4. Configure Ollama: http://localhost:8000/ollama-config/"
echo ""
echo "For more details, see QUICKSTART.md"
echo ""
