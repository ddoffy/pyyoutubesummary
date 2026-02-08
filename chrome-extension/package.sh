#!/bin/bash

# Ensure we are in the chrome-extension directory
cd "$(dirname "$0")"

# Remove existing zip
if [ -f "chrome-extension.zip" ]; then
    rm "chrome-extension.zip"
fi

# Check if dist exists
if [ ! -d "dist" ]; then
    echo "Error: dist directory not found. Please run 'npm run build' first."
    exit 1
fi

# Zip the contents of dist
cd dist
zip -r ../chrome-extension.zip .
cd ..

echo "Created chrome-extension.zip"
