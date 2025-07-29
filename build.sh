#!/bin/bash
set -e

echo "🔨 Starting DiamondFinder backend build..."

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Test imports
echo "🧪 Testing imports with postinstall.py..."
python postinstall.py

echo "✅ Build completed successfully!" 