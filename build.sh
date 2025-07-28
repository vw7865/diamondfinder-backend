#!/bin/bash

# DiamondFinder Backend Build Script
# This script builds the ext-vanillagenerator and sets up the Python backend

set -e

echo "🚀 Building DiamondFinder Ore Generation Backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully!"
else
    print_error "Failed to build Docker image"
    exit 1
fi

print_status "Starting the API server..."
docker-compose up -d

# Wait for the server to start
print_status "Waiting for server to start..."
sleep 10

# Test the API
print_status "Testing the API..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "API server is running and healthy!"
else
    print_warning "API server might not be ready yet. Check logs with: docker-compose logs"
fi

# Test the Bedrock ore generation
print_status "Testing Bedrock ore generation with seed=123456789, x=100, z=200..."
BEDROCK_TEST_RESPONSE=$(curl -s http://localhost:8000/api/v1/test)

if echo "$BEDROCK_TEST_RESPONSE" | grep -q "success.*true"; then
    print_success "Bedrock ore generation test passed!"
    echo "$BEDROCK_TEST_RESPONSE" | python3 -m json.tool
else
    print_warning "Bedrock ore generation test failed. Check the response:"
    echo "$BEDROCK_TEST_RESPONSE"
fi

# Test the Java ore generation
print_status "Testing Java ore generation with seed=123456789, x=100, z=200, version=1.18..."
JAVA_TEST_RESPONSE=$(curl -s http://localhost:8000/api/v1/java/test)

if echo "$JAVA_TEST_RESPONSE" | grep -q "success.*true"; then
    print_success "Java ore generation test passed!"
    echo "$JAVA_TEST_RESPONSE" | python3 -m json.tool
else
    print_warning "Java ore generation test failed. Check the response:"
    echo "$JAVA_TEST_RESPONSE"
fi

print_success "Build complete! 🎉"
echo ""
echo "📋 Next steps:"
echo "1. API is running at: http://localhost:8000"
echo "2. API documentation: http://localhost:8000/docs"
echo "3. Test endpoint: http://localhost:8000/api/v1/test"
echo "4. View logs: docker-compose logs -f"
echo "5. Stop server: docker-compose down"
echo ""
echo "🔗 API Endpoints:"
echo "  Bedrock Edition:"
echo "    POST /api/v1/find-ores - Find Bedrock ores at coordinates"
echo "    GET  /api/v1/find-ores - Find Bedrock ores (GET version)"
echo "    GET  /api/v1/test      - Test Bedrock with seed=123456789, x=100, z=200"
echo "  Java Edition:"
echo "    POST /api/v1/java/find-ores - Find Java ores at coordinates"
echo "    GET  /api/v1/java/find-ores - Find Java ores (GET version)"
echo "    GET  /api/v1/java/test      - Test Java with seed=123456789, x=100, z=200, version=1.18"
echo "    GET  /api/v1/java/supported-versions - List supported Java versions"
echo "  General:"
echo "    GET  /health           - Health check"
echo "    GET  /api/v1/supported-ores - List supported ore types"
echo ""
print_status "Ready to integrate with your iOS app! 📱" 