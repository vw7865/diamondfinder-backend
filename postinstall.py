#!/usr/bin/env python3
"""
Post-install script to test imports and verify setup
"""

import sys
import importlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    # Core Python modules (required)
    required_modules = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'requests',
        'json',
        'os',
        'logging'
    ]
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            return False
    
    # Test server_api import (required)
    try:
        from server_api import app
        print("✅ Server API app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import server_api: {e}")
        return False
    
    # Test ore generation imports (optional - won't fail build)
    ore_services_available = True
    
    try:
        from ore_generator import OreFinderService
        print("✅ Ore generation (Bedrock) imported successfully")
    except ImportError as e:
        print(f"⚠️  Ore generation (Bedrock) not available: {e}")
        ore_services_available = False
    except Exception as e:
        print(f"⚠️  Ore generation (Bedrock) failed to load: {e}")
        ore_services_available = False
    
    try:
        from java_ore_generator import JavaOreFinderService
        print("✅ Ore generation (Java) imported successfully")
    except ImportError as e:
        print(f"⚠️  Ore generation (Java) not available: {e}")
        ore_services_available = False
    except Exception as e:
        print(f"⚠️  Ore generation (Java) failed to load: {e}")
        ore_services_available = False
    
    if ore_services_available:
        print("🎉 All imports successful! Ore generation available.")
    else:
        print("🎉 Core imports successful! Ore generation will use fallback responses.")
    
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 