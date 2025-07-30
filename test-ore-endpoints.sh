#!/bin/bash

# Test ore generation endpoints for DiamondFinder Backend

API_URL="https://diamondfinder-backend.onrender.com"

echo "🧪 Testing DiamondFinder Ore Generation endpoints..."
echo "🌐 API URL: $API_URL"
echo ""

# Test ore generation test endpoint
echo "1️⃣ Testing ore generation test endpoint..."
if curl -s "$API_URL/api/v1/test" > /dev/null; then
    echo "✅ Ore generation test endpoint is working"
else
    echo "❌ Ore generation test endpoint failed"
fi

# Test Java ore generation test endpoint
echo ""
echo "2️⃣ Testing Java ore generation test endpoint..."
if curl -s "$API_URL/api/v1/java/test" > /dev/null; then
    echo "✅ Java ore generation test endpoint is working"
else
    echo "❌ Java ore generation test endpoint failed"
fi

# Test Bedrock ore search endpoint (POST)
echo ""
echo "3️⃣ Testing Bedrock ore search endpoint..."
TEST_DATA='{"seed": 123456789, "x": 100, "z": 200, "radius": 1}'
if curl -s -X POST "$API_URL/api/v1/find-ores" \
    -H "Content-Type: application/json" \
    -d "$TEST_DATA" > /dev/null; then
    echo "✅ Bedrock ore search endpoint is working"
else
    echo "❌ Bedrock ore search endpoint failed"
fi

# Test Java ore search endpoint (POST)
echo ""
echo "4️⃣ Testing Java ore search endpoint..."
TEST_DATA='{"seed": 123456789, "x": 100, "z": 200, "version": "1.20", "radius": 1}'
if curl -s -X POST "$API_URL/api/v1/java/find-ores" \
    -H "Content-Type: application/json" \
    -d "$TEST_DATA" > /dev/null; then
    echo "✅ Java ore search endpoint is working"
else
    echo "❌ Java ore search endpoint failed"
fi

echo ""
echo "🎯 Ore generation endpoint test complete!"
echo "📊 Check detailed logs at: https://dashboard.render.com"
echo ""
echo "💡 If endpoints fail, check if ore generation services are available" 