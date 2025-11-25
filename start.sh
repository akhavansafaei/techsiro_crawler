#!/bin/bash

echo "================================================"
echo "   Techsiro Price Monitor - Starting Server"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✓ Using Python: $PYTHON_CMD"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
$PYTHON_CMD -c "import flask, playwright, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed."
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements.txt
    playwright install chromium
    echo ""
fi

echo "✓ Dependencies OK"
echo ""

# Start the server
echo "🚀 Starting Techsiro Price Monitor..."
echo ""
echo "   Open your browser and navigate to:"
echo "   👉 http://localhost:5000"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

$PYTHON_CMD app.py
