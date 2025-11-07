#!/bin/bash
# Quick start script for frontend

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting Signal Radar Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --ignore-scripts
fi

# Start the dev server
echo "✨ Starting Vite dev server on http://localhost:5173"
npm run dev
