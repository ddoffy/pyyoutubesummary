#!/bin/bash

# Navigate to the script's directory found.
cd "$(dirname "$0")"

# Check if a virtual environment exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the server
echo "Starting YouTube Summary API Server on port 8282..."
python3 main.py
