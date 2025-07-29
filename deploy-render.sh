#!/bin/bash

# DiamondFinder Backend Deployment to Render.com

echo "🚀 Deploying DiamondFinder Backend to Render.com..."

# Check if we're in the right directory
if [ ! -f "server_api.py" ]; then
    echo "❌ Error: server_api.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found. Please ensure the Render configuration exists."
    exit 1
fi

# Check if enriched_servers.json exists
if [ ! -f "enriched_servers.json" ]; then
    echo "⚠️  Warning: enriched_servers.json not found. The API will generate it on first run."
fi

echo "📋 Files to be deployed:"
echo "  ✅ server_api.py"
echo "  ✅ server_enricher_v2.py"
echo "  ✅ requirements.txt"
echo "  ✅ render.yaml"
if [ -f "enriched_servers.json" ]; then
    echo "  ✅ enriched_servers.json"
else
    echo "  ⚠️  enriched_servers.json (will be generated)"
fi

echo ""
echo "🌐 Deployment URL: https://diamondfinder-backend.onrender.com"
echo ""
echo "📝 Next steps:"
echo "1. Push these files to your GitHub repository"
echo "2. Connect your repository to Render.com"
echo "3. Render will automatically deploy using render.yaml"
echo ""
echo "🔗 Render.com Dashboard: https://dashboard.render.com"
echo "📊 Health Check: https://diamondfinder-backend.onrender.com/health"
echo "📋 API Data: https://diamondfinder-backend.onrender.com/enriched_servers.json"

echo ""
echo "✅ Deployment configuration ready!"
echo "💡 Tip: Use 'git add . && git commit -m \"Deploy to Render\" && git push' to deploy" 