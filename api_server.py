#!/usr/bin/env python3
"""
DiamondFinder API Server
REST API for ore generation using ext-vanillagenerator
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import uvicorn

from ore_generator import OreFinderService, OreResult
from java_ore_generator import JavaOreFinderService, JavaOreResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DiamondFinder API",
    description="Minecraft ore generation API using ext-vanillagenerator",
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

# Initialize the ore finder services
ore_service = OreFinderService()
java_ore_service = JavaOreFinderService()

# Pydantic models for API
class OreLocationResponse(BaseModel):
    type: str
    coordinates: dict
    count: int

class OreSearchRequest(BaseModel):
    seed: int
    x: int
    z: int
    radius: Optional[int] = 1
    ore_type: Optional[str] = None

class JavaOreSearchRequest(BaseModel):
    seed: int
    x: int
    z: int
    version: str
    radius: Optional[int] = 1
    ore_type: Optional[str] = None

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
        "message": "DiamondFinder Ore Generation API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test the generator
        test_result = ore_service.find_ores(123456789, 100, 200, radius=0)
        return {
            "status": "healthy",
            "generator": "working",
            "test_result": {
                "seed": test_result.seed,
                "ores_found": len(test_result.ores)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generator not working: {str(e)}")

@app.post("/api/v1/find-ores", response_model=OreSearchResponse)
async def find_ores(request: OreSearchRequest):
    """
    Find ores at the specified coordinates
    
    Args:
        request: OreSearchRequest with seed, coordinates, and optional parameters
        
    Returns:
        OreSearchResponse with found ore locations
    """
    try:
        logger.info(f"Finding ores: seed={request.seed}, x={request.x}, z={request.z}")
        
        # Find ores using the service
        result = ore_service.find_ores(
            seed=request.seed,
            x=request.x,
            z=request.z,
            radius=request.radius
        )
        
        # Filter by ore type if specified
        if request.ore_type:
            result.ores = [ore for ore in result.ores if ore.type.lower() == request.ore_type.lower()]
            result.total_count = sum(ore.count for ore in result.ores)
        
        # Convert to response format
        ore_locations = [
            OreLocationResponse(
                type=ore.type,
                coordinates={"x": ore.x, "y": ore.y, "z": ore.z},
                count=ore.count
            )
            for ore in result.ores
        ]
        
        return OreSearchResponse(
            seed=result.seed,
            search_coordinates={"x": result.search_x, "z": result.search_z},
            chunk_coordinates={"x": result.chunk_coordinates[0], "z": result.chunk_coordinates[1]},
            total_ores=result.total_count,
            ore_locations=ore_locations,
            success=True,
            message=f"Found {result.total_count} ore blocks"
        )
        
    except Exception as e:
        logger.error(f"Error finding ores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find ores: {str(e)}")

@app.get("/api/v1/find-ores")
async def find_ores_get(
    seed: int = Query(..., description="World seed"),
    x: int = Query(..., description="X coordinate"),
    z: int = Query(..., description="Z coordinate"),
    radius: int = Query(1, description="Search radius in chunks"),
    ore_type: Optional[str] = Query(None, description="Filter by ore type")
):
    """
    GET endpoint for finding ores (alternative to POST)
    """
    request = OreSearchRequest(
        seed=seed,
        x=x,
        z=z,
        radius=radius,
        ore_type=ore_type
    )
    return await find_ores(request)

@app.get("/api/v1/test")
async def test_generation():
    """Test endpoint with the specified parameters"""
    try:
        result = ore_service.find_ores(123456789, 100, 200)
        
        return {
            "test_parameters": {
                "seed": 123456789,
                "x": 100,
                "z": 200
            },
            "result": {
                "total_ores": result.total_count,
                "ore_locations": [
                    {
                        "type": ore.type,
                        "coordinates": {"x": ore.x, "y": ore.y, "z": ore.z},
                        "count": ore.count
                    }
                    for ore in result.ores
                ]
            },
            "success": True
        }
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@app.get("/api/v1/supported-ores")
async def get_supported_ores():
    """Get list of supported ore types"""
    return {
        "supported_ores": [
            "Diamond",
            "Emerald", 
            "Gold",
            "Iron",
            "Coal",
            "Redstone",
            "Lapis Lazuli",
            "Copper"
        ]
    }

# Java Edition Endpoints

@app.post("/api/v1/java/find-ores", response_model=JavaOreSearchResponse)
async def find_java_ores(request: JavaOreSearchRequest):
    """
    Find ores at the specified coordinates in Java Edition
    
    Args:
        request: JavaOreSearchRequest with seed, coordinates, version, and optional parameters
        
    Returns:
        JavaOreSearchResponse with found ore locations
    """
    try:
        logger.info(f"Finding Java ores: seed={request.seed}, x={request.x}, z={request.z}, version={request.version}")
        
        # Find ores using the Java service
        result = java_ore_service.find_ores(
            seed=request.seed,
            x=request.x,
            z=request.z,
            version=request.version,
            radius=request.radius
        )
        
        # Filter by ore type if specified
        if request.ore_type:
            result.ores = [ore for ore in result.ores if ore.type.lower() == request.ore_type.lower()]
            result.total_count = sum(ore.count for ore in result.ores)
        
        # Convert to response format
        ore_locations = [
            OreLocationResponse(
                type=ore.type,
                coordinates={"x": ore.x, "y": ore.y, "z": ore.z},
                count=ore.count
            )
            for ore in result.ores
        ]
        
        return JavaOreSearchResponse(
            seed=result.seed,
            search_coordinates={"x": result.search_x, "z": result.search_z},
            version=result.version,
            chunk_coordinates={"x": result.chunk_coordinates[0], "z": result.chunk_coordinates[1]},
            total_ores=result.total_count,
            ore_locations=ore_locations,
            success=True,
            message=f"Found {result.total_count} ore blocks in Java {result.version}"
        )
        
    except Exception as e:
        logger.error(f"Error finding Java ores: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find Java ores: {str(e)}")

@app.get("/api/v1/java/find-ores")
async def find_java_ores_get(
    seed: int = Query(..., description="World seed"),
    x: int = Query(..., description="X coordinate"),
    z: int = Query(..., description="Z coordinate"),
    version: str = Query(..., description="Java version (1.18, 1.19, 1.20, 1.21)"),
    radius: int = Query(1, description="Search radius in chunks"),
    ore_type: Optional[str] = Query(None, description="Filter by ore type")
):
    """
    GET endpoint for finding Java Edition ores (alternative to POST)
    """
    request = JavaOreSearchRequest(
        seed=seed,
        x=x,
        z=z,
        version=version,
        radius=radius,
        ore_type=ore_type
    )
    return await find_java_ores(request)

@app.get("/api/v1/java/test")
async def test_java_generation():
    """Test Java Edition ore generation with the specified parameters"""
    try:
        result = java_ore_service.find_ores(123456789, 100, 200, "1.18")
        
        return {
            "test_parameters": {
                "seed": 123456789,
                "x": 100,
                "z": 200,
                "version": "1.18"
            },
            "result": {
                "total_ores": result.total_count,
                "ore_locations": [
                    {
                        "type": ore.type,
                        "coordinates": {"x": ore.x, "y": ore.y, "z": ore.z},
                        "count": ore.count,
                        "biome": ore.biome
                    }
                    for ore in result.ores
                ]
            },
            "success": True
        }
    except Exception as e:
        logger.error(f"Java test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Java test failed: {str(e)}")

@app.get("/api/v1/java/supported-versions")
async def get_supported_java_versions():
    """Get list of supported Java versions"""
    return {
        "supported_versions": java_ore_service.get_supported_versions()
    }

@app.post("/api/v1/java/clear-cache")
async def clear_java_cache():
    """Clear the Java Edition ore generation cache"""
    try:
        java_ore_service.clear_cache()
        return {"message": "Java Edition cache cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear Java cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 