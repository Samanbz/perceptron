#!/bin/bash
# Format Python code with black and isort

echo "🎨 Formatting Python code..."
echo "Running isort..."
isort .
echo "Running black..."
black .
echo "✅ Formatting complete!"
