#!/bin/bash

# Quick redeploy script for Render.com

echo "🚀 Quick redeploy to Render.com..."

# Add all changes
git add .

# Commit with timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "Redeploy: $timestamp"

# Push to trigger auto-deploy
git push origin main

echo "✅ Changes pushed to GitHub"
echo "🔄 Render.com should auto-deploy in ~2-3 minutes"
echo ""
echo "📊 Check deployment status at:"
echo "   https://dashboard.render.com"
echo ""
echo "🌐 Your API will be at:"
echo "   https://diamondfinder-backend.onrender.com" 