#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

try:
    print("Testing imports...")
    
    import fastapi
    print("✅ FastAPI imported successfully")
    
    import uvicorn
    print("✅ Uvicorn imported successfully")
    
    import pydantic
    print("✅ Pydantic imported successfully")
    
    import requests
    print("✅ Requests imported successfully")
    
    import json
    print("✅ JSON imported successfully")
    
    import os
    print("✅ OS imported successfully")
    
    import logging
    print("✅ Logging imported successfully")
    
    # Test server_api imports
    from server_api import app
    print("✅ Server API app imported successfully")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1) 