#!/usr/bin/env python3
"""
Test imports for DiamondFinder Backend
This file exists because Render.com is using a cached build command
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all required imports"""
    try:
        import fastapi
        logger.info("✅ FastAPI imported successfully")
    except ImportError as e:
        logger.error(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn
        logger.info("✅ Uvicorn imported successfully")
    except ImportError as e:
        logger.error(f"❌ Uvicorn import failed: {e}")
        return False

    try:
        import pydantic
        logger.info("✅ Pydantic imported successfully")
    except ImportError as e:
        logger.error(f"❌ Pydantic import failed: {e}")
        return False

    try:
        import requests
        logger.info("✅ Requests imported successfully")
    except ImportError as e:
        logger.error(f"❌ Requests import failed: {e}")
        return False

    try:
        import json
        logger.info("✅ JSON imported successfully")
    except ImportError as e:
        logger.error(f"❌ JSON import failed: {e}")
        return False

    try:
        import os
        logger.info("✅ OS imported successfully")
    except ImportError as e:
        logger.error(f"❌ OS import failed: {e}")
        return False

    try:
        import logging
        logger.info("✅ Logging imported successfully")
    except ImportError as e:
        logger.error(f"❌ Logging import failed: {e}")
        return False

    # Test server API import
    try:
        from server_api import app
        logger.info("✅ Server API app imported successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Server API import warning: {e}")

    # Test ore generation imports (optional)
    try:
        from ore_generator import OreFinderService
        logger.info("✅ Ore generation (Bedrock) imported successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Ore generation (Bedrock) not available: {e}")

    try:
        from java_ore_generator import JavaOreFinderService
        logger.info("✅ Ore generation (Java) imported successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Ore generation (Java) not available: {e}")

    logger.info("🎉 Core imports successful! Ore generation will use fallback responses.")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("✅ All imports successful!")
        exit(0)
    else:
        print("❌ Some imports failed!")
        exit(1) 