#!/bin/bash

# Release OS - Stop Script
# This script stops all Release OS processes

echo "🛑 Stopping Release OS..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Read PIDs from files
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo "✓ Backend stopped (PID: $BACKEND_PID)" || echo "⚠️  Backend process not found"
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo "✓ Frontend stopped (PID: $FRONTEND_PID)" || echo "⚠️  Frontend process not found"
    rm .frontend.pid
fi

if [ -f .watcher.pid ]; then
    WATCHER_PID=$(cat .watcher.pid)
    kill $WATCHER_PID 2>/dev/null && echo "✓ Folder watcher stopped (PID: $WATCHER_PID)" || echo "⚠️  Watcher process not found"
    rm .watcher.pid
fi

echo ""
echo "✅ Release OS stopped"
