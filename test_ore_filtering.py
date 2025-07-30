#!/usr/bin/env python3
"""
Test script to verify ore type filtering is working correctly
"""

import json
import requests

def test_ore_filtering():
    """Test ore filtering with different ore types"""
    
    base_url = "https://diamondfinder-backend.onrender.com/api/v1/java/find-ores"
    test_params = {
        "seed": 52245,
        "x": 8,
        "z": 5,
        "version": "1.20",
        "radius": 1
    }
    
    # Test individual ore types
    ore_types = ["diamond", "iron", "gold", "coal", "redstone", "lapis_lazuli", "emerald", "copper"]
    
    print("🔍 Testing individual ore type filtering:")
    print("=" * 50)
    
    for ore_type in ore_types:
        params = test_params.copy()
        params["oreType"] = ore_type
        
        try:
            response = requests.post(base_url, json=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {ore_type.capitalize()}: {data['total_ores']} ores found")
            else:
                print(f"❌ {ore_type.capitalize()}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {ore_type.capitalize()}: {e}")
    
    print("\n🔍 Testing multiple ore types:")
    print("=" * 50)
    
    # Test multiple ore types
    multi_tests = [
        ["diamond", "iron"],
        ["gold", "emerald"],
        ["coal", "iron", "copper"]
    ]
    
    for ore_types in multi_tests:
        params = test_params.copy()
        params["oreTypes"] = ore_types
        
        try:
            response = requests.post(base_url, json=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {', '.join(ore_types).capitalize()}: {data['total_ores']} ores found")
            else:
                print(f"❌ {', '.join(ore_types).capitalize()}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {', '.join(ore_types).capitalize()}: {e}")
    
    print("\n🔍 Testing all ores (no filter):")
    print("=" * 50)
    
    try:
        response = requests.post(base_url, json=test_params)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ All ores: {data['total_ores']} ores found")
        else:
            print(f"❌ All ores: Error {response.status_code}")
    except Exception as e:
        print(f"❌ All ores: {e}")

if __name__ == "__main__":
    test_ore_filtering() 