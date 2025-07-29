#!/bin/bash

# DiamondFinder Server API Deployment Script

echo "🚀 Starting DiamondFinder Server API deployment..."

# Check if we're in the right directory
if [ ! -f "server_api.py" ]; then
    echo "❌ Error: server_api.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if enriched_servers.json exists
if [ ! -f "enriched_servers.json" ]; then
    echo "⚠️  Warning: enriched_servers.json not found. The API will generate it on first run."
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.server -t diamondfinder-server-api .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.server.yml down

# Start the new container
echo "▶️  Starting server API..."
docker-compose -f docker-compose.server.yml up -d

# Wait for the service to be healthy
echo "⏳ Waiting for service to be healthy..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Server API is healthy and running!"
        echo "🌐 API available at: http://localhost:8000"
        echo "📊 Health check: http://localhost:8000/health"
        echo "📋 Servers data: http://localhost:8000/enriched_servers.json"
        exit 0
    fi
    echo "⏳ Waiting... ($i/30)"
    sleep 2
done

echo "❌ Service failed to start properly"
docker-compose -f docker-compose.server.yml logs
exit 1 