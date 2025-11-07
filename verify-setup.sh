#!/bin/bash
# Quick setup verification script

echo "🔍 Verifying Signal Radar Setup..."
echo ""

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.11+"
fi

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js"
fi

# Check npm
echo "Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm $NPM_VERSION"
else
    echo "❌ npm not found. Please install npm"
fi

echo ""
echo "📁 Project Structure:"
echo "✅ Backend folder exists: $([ -d backend ] && echo 'Yes' || echo 'No')"
echo "✅ Frontend folder exists: $([ -d frontend ] && echo 'Yes' || echo 'No')"
echo "✅ Backend app.py exists: $([ -f backend/app.py ] && echo 'Yes' || echo 'No')"
echo "✅ Frontend src exists: $([ -d frontend/src ] && echo 'Yes' || echo 'No')"

echo ""
echo "🚀 Ready to start!"
echo ""
echo "Run: ./start-all.sh"
