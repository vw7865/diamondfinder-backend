#!/bin/bash

# Test deployment script for DiamondFinder Backend

API_URL="https://diamondfinder-backend.onrender.com"

echo "🧪 Testing DiamondFinder Backend deployment..."
echo "🌐 API URL: $API_URL"
echo ""

# Test root endpoint
echo "1️⃣ Testing root endpoint..."
if curl -s "$API_URL/" > /dev/null; then
    echo "✅ Root endpoint is working"
else
    echo "❌ Root endpoint failed"
fi

# Test health endpoint
echo ""
echo "2️⃣ Testing health endpoint..."
if curl -s "$API_URL/health" > /dev/null; then
    echo "✅ Health endpoint is working"
else
    echo "❌ Health endpoint failed"
fi

# Test server data endpoint
echo ""
echo "3️⃣ Testing server data endpoint..."
if curl -s "$API_URL/enriched_servers.json" > /dev/null; then
    echo "✅ Server data endpoint is working"
else
    echo "❌ Server data endpoint failed"
fi

# Test server count endpoint
echo ""
echo "4️⃣ Testing server count endpoint..."
if curl -s "$API_URL/servers/count" > /dev/null; then
    echo "✅ Server count endpoint is working"
else
    echo "❌ Server count endpoint failed"
fi

echo ""
echo "🎯 Deployment test complete!"
echo "📊 Check detailed logs at: https://dashboard.render.com" 