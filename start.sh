#!/bin/bash

# Release OS - Startup Script
# This script starts both the backend and frontend in the background

set -e

echo "🎵 Release OS - Starting..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create watch folder
mkdir -p ~/Music/ReleaseDrop

# Start backend
echo -e "${BLUE}[1/3]${NC} Starting backend API..."
cd backend
source venv/bin/activate 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating it...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
    pip install -r requirements.txt
}

# Start backend in background
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓${NC} Backend API started (PID: $BACKEND_PID) - http://localhost:8000"

# Start frontend
cd ../frontend
echo -e "${BLUE}[2/3]${NC} Starting frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID) - http://localhost:5173"

# Start folder watcher
cd ../backend
echo -e "${BLUE}[3/3]${NC} Starting folder watcher..."
source venv/bin/activate
python folder_watcher.py > ../watcher.log 2>&1 &
WATCHER_PID=$!
echo -e "${GREEN}✓${NC} Folder watcher started (PID: $WATCHER_PID)"

cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🚀 Release OS is running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "  Watch Folder: ~/Music/ReleaseDrop"
echo ""
echo "  Backend PID:  $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo "  Watcher PID:  $WATCHER_PID"
echo ""
echo "Logs:"
echo "  backend.log  - Backend API logs"
echo "  frontend.log - Frontend logs"
echo "  watcher.log  - Folder watcher logs"
echo ""
echo "To stop all processes, run: ./stop.sh"
echo "Or manually kill processes:"
echo "  kill $BACKEND_PID $FRONTEND_PID $WATCHER_PID"
echo ""

# Save PIDs to file for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
echo "$WATCHER_PID" > .watcher.pid

# Keep script running and show logs
echo "Press Ctrl+C to stop all processes"
echo ""

# Trap Ctrl+C and cleanup
trap cleanup INT

cleanup() {
    echo ""
    echo "🛑 Stopping Release OS..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    kill $WATCHER_PID 2>/dev/null || true
    rm -f .backend.pid .frontend.pid .watcher.pid
    echo "✅ All processes stopped"
    exit 0
}

# Wait for any process to exit
wait -n

# If we get here, one process exited
echo "⚠️  A process exited. Stopping all processes..."
cleanup
