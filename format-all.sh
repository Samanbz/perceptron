#!/bin/bash
# Format both backend and frontend

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🎨 Formatting entire codebase..."

echo ""
echo "📡 Formatting backend (Python with black & isort)..."
chmod +x backend/format.sh
(cd backend && ./format.sh)

echo ""
echo "🎨 Formatting frontend (React with Prettier & ESLint)..."
chmod +x frontend/format.sh
(cd frontend && ./format.sh)

echo ""
echo "✅ All code formatted!"
