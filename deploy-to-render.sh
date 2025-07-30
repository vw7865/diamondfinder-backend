#!/bin/bash

# DiamondFinder Backend Deployment to Render.com
# Updated for working ore generation

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

echo "📋 Files to be deployed:"
echo "  ✅ server_api.py (with working ore generation)"
echo "  ✅ java_ore_generator.py (fixed coordinate bounds)"
echo "  ✅ ore_generator.py"
echo "  ✅ server_enricher_v2.py"
echo "  ✅ requirements.txt"
echo "  ✅ render.yaml (updated for uvicorn)"
echo "  ✅ Procfile (updated for uvicorn)"

if [ -f "enriched_servers.json" ]; then
    echo "  ✅ enriched_servers.json"
else
    echo "  ⚠️  enriched_servers.json (will be generated)"
fi

echo ""
echo "🔧 Configuration Summary:"
echo "  • Using uvicorn for proper ASGI server"
echo "  • Fixed ore generation coordinate bounds"
echo "  • Added ore type filtering support"
echo "  • Increased search radius to 128 blocks"
echo "  • Health check endpoint: /health"

echo ""
echo "🌐 Deployment URL: https://diamondfinder-backend.onrender.com"
echo ""
echo "📝 Next steps:"
echo "1. Push these files to your GitHub repository:"
echo "   git add ."
echo "   git commit -m \"Fix ore generation and deploy to Render\""
echo "   git push"
echo ""
echo "2. Connect your repository to Render.com if not already done"
echo "3. Render will automatically deploy using render.yaml"
echo ""
echo "🔗 Render.com Dashboard: https://dashboard.render.com"
echo "📊 Health Check: https://diamondfinder-backend.onrender.com/health"
echo "📋 API Data: https://diamondfinder-backend.onrender.com/enriched_servers.json"
echo "🔍 Test Ore Search: POST https://diamondfinder-backend.onrender.com/api/v1/java/find-ores"

echo ""
echo "✅ Deployment configuration ready!"
echo "💡 The ore generation should now work correctly with real data!" 