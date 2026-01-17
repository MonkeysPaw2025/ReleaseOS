#!/bin/bash

# Release OS - Setup Script
# Run this once to set up the entire project

set -e

echo "🎵 Release OS - Setup"
echo "===================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️  FFmpeg not found${NC}"
    echo "   Install it with: brew install ffmpeg"
    echo ""
    read -p "Continue without FFmpeg? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    FFMPEG_VERSION=$(ffmpeg -version | head -1 | cut -d' ' -f3)
    echo -e "${GREEN}✓${NC} FFmpeg $FFMPEG_VERSION"
fi

echo ""

# Setup backend
echo -e "${BLUE}[1/3] Setting up backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo -e "${GREEN}✓${NC} Backend setup complete"
echo ""

# Setup frontend
cd ../frontend
echo -e "${BLUE}[2/3] Setting up frontend...${NC}"

echo "Installing Node.js dependencies..."
npm install --silent

echo -e "${GREEN}✓${NC} Frontend setup complete"
echo ""

# Create watch folder
echo -e "${BLUE}[3/3] Creating watch folder...${NC}"
mkdir -p ~/Music/ReleaseDrop
echo -e "${GREEN}✓${NC} Watch folder created at ~/Music/ReleaseDrop"
echo ""

# Make scripts executable
cd ..
chmod +x start.sh stop.sh setup.sh

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start Release OS, run:"
echo "  ./start.sh"
echo ""
echo "Or see QUICKSTART.md for manual setup"
echo ""
