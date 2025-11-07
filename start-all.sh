#!/bin/bash
# Start both backend and frontend

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting Signal Radar Full Stack..."

# Make scripts executable
chmod +x backend/run.sh frontend/run.sh

# Function to handle cleanup
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap CTRL+C
trap cleanup INT

# Start backend in background
echo "📡 Starting backend..."
(cd backend && ./run.sh) &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend..."
(cd frontend && ./run.sh) &
FRONTEND_PID=$!

echo ""
echo "✅ Both services are starting..."
echo "📡 Backend: http://localhost:8000 (docs: http://localhost:8000/docs)"
echo "🎨 Frontend: http://localhost:5173"
echo ""
echo "Press CTRL+C to stop both services"

# Wait for both processes
wait
