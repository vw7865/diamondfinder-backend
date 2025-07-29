# DiamondFinder Server API Deployment

This is a simplified deployment for the DiamondFinder Server API that serves enriched Minecraft server data from LunarClient.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Deploy using the provided script
./deploy-server.sh
```

### Option 2: Manual Docker Deployment

```bash
# Build the image
docker build -f Dockerfile.server -t diamondfinder-server-api .

# Run the container
docker run -d -p 8000:8000 --name diamondfinder-server diamondfinder-server-api
```

### Option 3: Direct Python Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python server_api.py
```

## API Endpoints

- **Health Check**: `GET /health`
- **Root Info**: `GET /`
- **Server Data**: `GET /enriched_servers.json`
- **Server Count**: `GET /servers/count`

## Configuration

The server will automatically:
1. Load existing `enriched_servers.json` if available
2. Generate new data from LunarClient if no file exists
3. Serve the data via REST API

## Troubleshooting

### Build Failures
- Ensure you're using Python 3.11+
- Check that all requirements are installed
- Verify `enriched_servers.json` exists (optional)

### Runtime Issues
- Check logs: `docker logs diamondfinder-server`
- Verify health endpoint: `curl http://localhost:8000/health`
- Ensure port 8000 is available

## Files

- `server_api.py` - Main FastAPI server
- `server_enricher_v2.py` - LunarClient data enrichment
- `enriched_servers.json` - Cached server data
- `Dockerfile.server` - Simplified Docker build
- `docker-compose.server.yml` - Docker Compose configuration
- `deploy-server.sh` - Automated deployment script

## Environment Variables

- `PYTHONUNBUFFERED=1` - Ensures Python output is not buffered
- Port 8000 - Default API port (configurable in docker-compose)

## Health Monitoring

The API includes health checks that verify:
- Server is responding
- Enriched data file exists
- Server count is available

Access health status at: `http://localhost:8000/health` 