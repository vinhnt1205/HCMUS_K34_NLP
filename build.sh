#!/bin/bash
# Build script for Render deployment

echo "=== Starting build process ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download model file
echo "Downloading model file..."
python download_model.py

echo "=== Build completed ===" 