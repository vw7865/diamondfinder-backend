#!/usr/bin/env python3
"""
Simple API Server for Enriched Server Data
Serves enriched server data from LunarClient ServerMappings
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import logging
import uvicorn
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DiamondFinder Server API",
    description="API for serving enriched Minecraft server data from LunarClient",
    version="1.0.0"
)

# Add CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "DiamondFinder Server API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "enriched_servers": "/enriched_servers.json",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check if enriched servers file exists
        enriched_file = "enriched_servers.json"
        if os.path.exists(enriched_file):
            with open(enriched_file, 'r') as f:
                data = json.load(f)
            server_count = len(data.get('servers', []))
            return {
                "status": "healthy",
                "enriched_servers": {
                    "file_exists": True,
                    "server_count": server_count,
                    "last_updated": data.get('metadata', {}).get('last_updated', 'unknown')
                }
            }
        else:
            return {
                "status": "healthy",
                "enriched_servers": {
                    "file_exists": False,
                    "server_count": 0,
                    "message": "No enriched servers file found"
                }
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/enriched_servers.json")
async def get_enriched_servers():
    """Serve enriched server data from LunarClient"""
    try:
        # Try to load the enriched servers file
        enriched_file = "enriched_servers.json"
        if os.path.exists(enriched_file):
            with open(enriched_file, 'r') as f:
                data = json.load(f)
            server_count = len(data.get('servers', []))
            logger.info(f"Serving enriched servers data: {server_count} servers")
            return data
        else:
            # If no enriched data, try to generate it
            logger.info("No enriched servers file found, attempting to generate...")
            
            # Import and run the server enricher
            try:
                from server_enricher_v2 import ServerEnricher
                
                enricher = ServerEnricher()
                # Note: enrich_all_servers() is not async, so we don't await it
                enricher.enrich_all_servers()
                
                if os.path.exists(enriched_file):
                    with open(enriched_file, 'r') as f:
                        data = json.load(f)
                    server_count = len(data.get('servers', []))
                    logger.info(f"Generated and serving enriched servers data: {server_count} servers")
                    return data
                else:
                    raise HTTPException(status_code=404, detail="Unable to generate enriched server data")
            except ImportError as e:
                logger.error(f"Failed to import server enricher: {e}")
                raise HTTPException(status_code=500, detail="Server enricher not available")
            except Exception as e:
                logger.error(f"Failed to generate enriched servers: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to generate enriched servers: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error serving enriched servers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to serve enriched servers: {str(e)}")

@app.get("/servers/count")
async def get_server_count():
    """Get the count of enriched servers"""
    try:
        enriched_file = "enriched_servers.json"
        if os.path.exists(enriched_file):
            with open(enriched_file, 'r') as f:
                data = json.load(f)
            server_count = len(data.get('servers', []))
            return {
                "server_count": server_count,
                "metadata": data.get('metadata', {})
            }
        else:
            return {
                "server_count": 0,
                "message": "No enriched servers file found"
            }
    except Exception as e:
        logger.error(f"Error getting server count: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get server count: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 