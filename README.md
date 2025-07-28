# DiamondFinder Ore Generation Backend

This backend integrates the [ext-vanillagenerator](https://github.com/NetherGamesMC/ext-vanillagenerator) library to provide accurate Minecraft Bedrock ore generation for the DiamondFinder iOS app.

## 🎯 Features

- **Accurate Bedrock Generation**: Uses the official ext-vanillagenerator library
- **Accurate Java Generation**: Uses Cubiomes for Java Edition ore generation
- **Multi-Version Support**: Supports Java 1.18, 1.19, 1.20, 1.21
- **REST API**: FastAPI-based API for easy mobile app integration
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **JSON Output**: Structured responses for mobile app consumption
- **Ore Grouping**: Groups adjacent ore blocks for better UX
- **Multiple Ore Types**: Supports all major ore types (Diamond, Emerald, Gold, etc.)
- **In-Memory Caching**: Avoids reprocessing repeated queries

## 🚀 Quick Start

### Prerequisites

- Docker
- Docker Compose
- curl (for testing)

### Build and Run

1. **Clone and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Make the build script executable:**
   ```bash
   chmod +x build.sh
   ```

3. **Run the build script:**
   ```bash
   ./build.sh
   ```

This will:
- Build the Docker image with ext-vanillagenerator
- Start the API server
- Run health checks
- Test ore generation with the specified parameters

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Bedrock Edition

#### Find Ores (POST)
```bash
POST /api/v1/find-ores
Content-Type: application/json

{
  "seed": 123456789,
  "x": 100,
  "z": 200,
  "radius": 1,
  "ore_type": "Diamond"
}
```

#### Find Ores (GET)
```bash
GET /api/v1/find-ores?seed=123456789&x=100&z=200&radius=1&ore_type=Diamond
```

#### Test Generation
```bash
GET /api/v1/test
```

### Java Edition

#### Find Ores (POST)
```bash
POST /api/v1/java/find-ores
Content-Type: application/json

{
  "seed": 123456789,
  "x": 100,
  "z": 200,
  "version": "1.18",
  "radius": 1,
  "ore_type": "Diamond"
}
```

#### Find Ores (GET)
```bash
GET /api/v1/java/find-ores?seed=123456789&x=100&z=200&version=1.18&radius=1&ore_type=Diamond
```

#### Test Generation
```bash
GET /api/v1/java/test
```

#### Supported Java Versions
```bash
GET /api/v1/java/supported-versions
```

#### Clear Cache
```bash
POST /api/v1/java/clear-cache
```

### General

#### Supported Ore Types
```bash
GET /api/v1/supported-ores
```

## 🧪 Testing

### Test Bedrock Edition:
```bash
curl http://localhost:8000/api/v1/test
```

### Test Java Edition:
```bash
curl http://localhost:8000/api/v1/java/test
```

### Test custom Bedrock parameters:
```bash
curl "http://localhost:8000/api/v1/find-ores?seed=123456789&x=100&z=200"
```

### Test custom Java parameters:
```bash
curl "http://localhost:8000/api/v1/java/find-ores?seed=123456789&x=100&z=200&version=1.18"
```

### Test POST endpoints:

#### Bedrock:
```bash
curl -X POST http://localhost:8000/api/v1/find-ores \
  -H "Content-Type: application/json" \
  -d '{"seed": 123456789, "x": 100, "z": 200, "radius": 1}'
```

#### Java:
```bash
curl -X POST http://localhost:8000/api/v1/java/find-ores \
  -H "Content-Type: application/json" \
  -d '{"seed": 123456789, "x": 100, "z": 200, "version": "1.18", "radius": 1}'
```

## 📊 Response Format

### Bedrock Edition Response
```json
{
  "seed": 123456789,
  "search_coordinates": {
    "x": 100,
    "z": 200
  },
  "chunk_coordinates": {
    "x": 6,
    "z": 12
  },
  "total_ores": 15,
  "ore_locations": [
    {
      "type": "Diamond",
      "coordinates": {
        "x": 96,
        "y": 8,
        "z": 208
      },
      "count": 3
    }
  ],
  "success": true,
  "message": "Found 15 ore blocks"
}
```

### Java Edition Response
```json
{
  "seed": 123456789,
  "search_coordinates": {
    "x": 100,
    "z": 200
  },
  "version": "1.18",
  "chunk_coordinates": {
    "x": 6,
    "z": 12
  },
  "total_ores": 12,
  "ore_locations": [
    {
      "type": "Diamond",
      "coordinates": {
        "x": 96,
        "y": 8,
        "z": 208
      },
      "count": 3
    }
  ],
  "success": true,
  "message": "Found 12 ore blocks in Java 1.18"
}
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   iOS App       │    │   FastAPI        │    │   ext-vanillagenerator │
│                 │───▶│   Backend        │───▶│   C++ Library       │
│   (SwiftUI)     │    │   (Python)       │    │   (PHP Extension)   │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                │
                                ▼
                       ┌─────────────────────┐
                       │   Cubiomes          │
                       │   C Library         │
                       │   (Java Edition)    │
                       └─────────────────────┘
```

## 🔧 Development

### Manual Build (without Docker)

1. **Install dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install build-essential cmake git php8.1-dev libphp8.1-embed pkg-config
   
   # macOS
   brew install cmake php
   ```

2. **Clone and build ext-vanillagenerator:**
   ```bash
   git clone https://github.com/NetherGamesMC/ext-vanillagenerator.git
   cd ext-vanillagenerator
   phpize
   ./configure
   make
   ```

3. **Clone and build Cubiomes:**
   ```bash
   git clone https://github.com/Cubitect/cubiomes.git
   cd cubiomes
   make
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the API server:**
   ```bash
   python api_server.py
   ```

### Docker Commands

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## 📱 iOS Integration

### Swift Network Call Example

```swift
import Foundation

struct OreSearchRequest: Codable {
    let seed: Int
    let x: Int
    let z: Int
    let radius: Int
    let oreType: String?
}

struct OreLocation: Codable {
    let type: String
    let coordinates: [String: Int]
    let count: Int
}

struct OreSearchResponse: Codable {
    let seed: Int
    let searchCoordinates: [String: Int]
    let totalOres: Int
    let oreLocations: [OreLocation]
    let success: Bool
    let message: String
}

// Bedrock Edition
func findBedrockOres(seed: Int, x: Int, z: Int, oreType: String? = nil) async throws -> OreSearchResponse {
    let url = URL(string: "http://localhost:8000/api/v1/find-ores")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body = OreSearchRequest(seed: seed, x: x, z: z, radius: 1, oreType: oreType)
    request.httpBody = try JSONEncoder().encode(body)
    
    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(OreSearchResponse.self, from: data)
}

// Java Edition
struct JavaOreSearchRequest: Codable {
    let seed: Int
    let x: Int
    let z: Int
    let version: String
    let radius: Int
    let oreType: String?
}

struct JavaOreSearchResponse: Codable {
    let seed: Int
    let searchCoordinates: [String: Int]
    let version: String
    let totalOres: Int
    let oreLocations: [OreLocation]
    let success: Bool
    let message: String
}

func findJavaOres(seed: Int, x: Int, z: Int, version: String, oreType: String? = nil) async throws -> JavaOreSearchResponse {
    let url = URL(string: "http://localhost:8000/api/v1/java/find-ores")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body = JavaOreSearchRequest(seed: seed, x: x, z: z, version: version, radius: 1, oreType: oreType)
    request.httpBody = try JSONEncoder().encode(body)
    
    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(JavaOreSearchResponse.self, from: data)
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Docker build fails:**
   - Ensure Docker has enough memory (4GB+ recommended)
   - Check internet connection for git clone
   - Try rebuilding: `docker-compose build --no-cache`

2. **API not responding:**
   - Check if container is running: `docker-compose ps`
   - View logs: `docker-compose logs diamondfinder-api`
   - Check port 8000 is not in use

3. **Generator errors:**
   - Verify ext-vanillagenerator compilation
   - Check PHP extension loading
   - Review generator logs

### Debug Mode

Run with debug logging:
```bash
docker-compose run --rm diamondfinder-api python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from ore_generator import OreFinderService
service = OreFinderService()
result = service.find_ores(123456789, 100, 200)
print(f'Found {len(result.ores)} ores')
"
```

## 📄 License

This project uses the ext-vanillagenerator library which is licensed under MIT. See the [original repository](https://github.com/NetherGamesMC/ext-vanillagenerator) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues related to:
- **ext-vanillagenerator**: [Original Repository](https://github.com/NetherGamesMC/ext-vanillagenerator)
- **This Backend**: Create an issue in this repository
- **iOS Integration**: Check the iOS app documentation 