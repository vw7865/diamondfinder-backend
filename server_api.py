#!/usr/bin/env python3
"""
DiamondFinder API Server
Combined API for ore generation and enriched server data
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import logging
import uvicorn

# Import ore generation services
try:
    from ore_generator import OreFinderService, OreResult
    from java_ore_generator import JavaOreFinderService, JavaOreResult
    ORE_SERVICES_AVAILABLE = True
except ImportError:
    ORE_SERVICES_AVAILABLE = False
    logger.warning("Ore generation services not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DiamondFinder API",
    description="Combined API for Minecraft ore generation and server data",
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

# Initialize the ore finder services if available
if ORE_SERVICES_AVAILABLE:
    ore_service = OreFinderService()
    java_ore_service = JavaOreFinderService()

# Pydantic models for ore generation API
class OreLocationResponse(BaseModel):
    type: str
    coordinates: dict
    count: int

class OreSearchRequest(BaseModel):
    seed: int
    x: int
    z: int
    radius: Optional[int] = 1
    oreType: Optional[str] = None

class JavaOreSearchRequest(BaseModel):
    seed: int
    x: int
    z: int
    version: str
    radius: Optional[int] = 1
    oreType: Optional[str] = None

class OreSearchResponse(BaseModel):
    seed: int
    search_coordinates: dict
    chunk_coordinates: dict
    total_ores: int
    ore_locations: List[OreLocationResponse]
    success: bool
    message: str

class JavaOreSearchResponse(BaseModel):
    seed: int
    search_coordinates: dict
    version: str
    chunk_coordinates: dict
    total_ores: int
    ore_locations: List[OreLocationResponse]
    success: bool
    message: str

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

# MARK: - Ore Generation Endpoints

@app.post("/api/v1/find-ores", response_model=OreSearchResponse)
async def find_ores(request: OreSearchRequest):
    """Find ores in Bedrock edition"""
    if not ORE_SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Ore generation services not available")
    
    try:
        logger.info(f"Searching for ores: seed={request.seed}, x={request.x}, z={request.z}, radius={request.radius}")
        
        result = ore_service.find_ores(
            request.seed, 
            request.x, 
            request.z, 
            radius=request.radius,
            ore_type=request.oreType
        )
        
        # Convert to response format
        ore_locations = []
        for ore in result.ores:
            ore_locations.append(OreLocationResponse(
                type=ore.type,
                coordinates={"x": ore.x, "y": ore.y, "z": ore.z},
                count=ore.count
            ))
        
        return OreSearchResponse(
            seed=result.seed,
            search_coordinates={"x": request.x, "z": request.z},
            chunk_coordinates={"x": result.chunk_x, "z": result.chunk_z},
            total_ores=result.total_ores,
            ore_locations=ore_locations,
            success=True,
            message=f"Found {result.total_ores} ores"
        )
        
    except Exception as e:
        logger.error(f"Error finding ores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find ores: {str(e)}")

@app.post("/api/v1/java/find-ores", response_model=JavaOreSearchResponse)
async def find_java_ores(request: JavaOreSearchRequest):
    """Find ores in Java edition"""
    if not ORE_SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Ore generation services not available")
    
    try:
        logger.info(f"Searching for Java ores: seed={request.seed}, x={request.x}, z={request.z}, version={request.version}")
        
        result = java_ore_service.find_ores(
            request.seed, 
            request.x, 
            request.z, 
            request.version,
            radius=request.radius,
            ore_type=request.oreType
        )
        
        # Convert to response format
        ore_locations = []
        for ore in result.ores:
            ore_locations.append(OreLocationResponse(
                type=ore.type,
                coordinates={"x": ore.x, "y": ore.y, "z": ore.z},
                count=ore.count
            ))
        
        return JavaOreSearchResponse(
            seed=result.seed,
            search_coordinates={"x": request.x, "z": request.z},
            version=request.version,
            chunk_coordinates={"x": result.chunk_x, "z": result.chunk_z},
            total_ores=result.total_ores,
            ore_locations=ore_locations,
            success=True,
            message=f"Found {result.total_ores} ores"
        )
        
    except Exception as e:
        logger.error(f"Error finding Java ores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find Java ores: {str(e)}")

@app.get("/api/v1/test")
async def test_generation():
    """Test ore generation"""
    if not ORE_SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Ore generation services not available")
    
    try:
        # Test Bedrock generation
        result = ore_service.find_ores(123456789, 100, 200, radius=0)
        return {
            "status": "working",
            "bedrock_test": {
                "seed": result.seed,
                "total_ores": result.total_ores,
                "chunk": {"x": result.chunk_x, "z": result.chunk_z}
            }
        }
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")

@app.get("/api/v1/java/test")
async def test_java_generation():
    """Test Java ore generation"""
    if not ORE_SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Ore generation services not available")
    
    try:
        # Test Java generation
        result = java_ore_service.find_ores(123456789, 100, 200, "1.20", radius=0)
        return {
            "status": "working",
            "java_test": {
                "seed": result.seed,
                "version": "1.20",
                "total_ores": result.total_ores,
                "chunk": {"x": result.chunk_x, "z": result.chunk_z}
            }
        }
    except Exception as e:
        logger.error(f"Java test generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Java test generation failed: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "server_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        log_level="info"
    ) 