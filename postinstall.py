#!/usr/bin/env python3
"""
Post-install script to test imports and verify setup
"""

import sys
import importlib

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
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
    
    # Test server_api import
    try:
        from server_api import app
        print("✅ Server API app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import server_api: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 