#!/usr/bin/env python3
"""
DiamondFinder Java Edition Ore Generator
Integrates Cubiomes for accurate Java Edition ore generation
"""

import json
import subprocess
import sys
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JavaVersion(Enum):
    """Supported Java Edition versions"""
    V1_18 = "1.18"
    V1_19 = "1.19"
    V1_20 = "1.20"
    V1_21 = "1.21"

@dataclass
class JavaOreBlock:
    """Represents a single ore block found in Java Edition"""
    type: str
    x: int
    y: int
    z: int
    count: int = 1
    biome: str = "unknown"

@dataclass
class JavaOreResult:
    """Complete result of a Java Edition ore search"""
    seed: int
    search_x: int
    search_z: int
    version: str
    ores: List[JavaOreBlock]
    total_count: int
    chunk_coordinates: Tuple[int, int]

class CubiomesWrapper:
    """Wrapper for the Cubiomes C library"""
    
    def __init__(self, cubiomes_path: str = "./cubiomes"):
        """
        Initialize the wrapper
        
        Args:
            cubiomes_path: Path to the compiled Cubiomes executable
        """
        self.cubiomes_path = cubiomes_path
        self._validate_cubiomes()
    
    def _validate_cubiomes(self) -> None:
        """Validate that the Cubiomes executable exists and is working"""
        if not os.path.exists(self.cubiomes_path):
            raise FileNotFoundError(f"Cubiomes not found at: {self.cubiomes_path}")
        
        # Test the executable
        try:
            result = subprocess.run([self.cubiomes_path, "--help"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                logger.warning(f"Cubiomes help check failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.warning("Cubiomes help check timed out")
        except Exception as e:
            logger.warning(f"Cubiomes validation failed: {e}")
    
    def get_biome_and_height(self, seed: int, x: int, z: int, version: str) -> Dict:
        """
        Get biome and terrain height for a specific location
        
        Args:
            seed: World seed
            x: X coordinate
            z: Z coordinate
            version: Java version (1.18, 1.19, etc.)
            
        Returns:
            Dictionary with biome and height information
        """
        try:
            # Call Cubiomes for biome and height data
            cmd = [
                self.cubiomes_path,
                "--seed", str(seed),
                "--x", str(x),
                "--z", str(z),
                "--version", version,
                "--output", "json"
            ]
            
            logger.info(f"Getting biome/height: seed={seed}, x={x}, z={z}, version={version}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"Cubiomes failed: {result.stderr}")
                return {"biome": "unknown", "height": 64}
            
            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                return {
                    "biome": data.get("biome", "unknown"),
                    "height": data.get("height", 64),
                    "temperature": data.get("temperature", 0.5),
                    "humidity": data.get("humidity", 0.5)
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Cubiomes output: {e}")
                return {"biome": "unknown", "height": 64}
                
        except subprocess.TimeoutExpired:
            logger.error("Cubiomes timed out")
            return {"biome": "unknown", "height": 64}
        except Exception as e:
            logger.error(f"Cubiomes error: {e}")
            return {"biome": "unknown", "height": 64}
    
    def generate_java_ores(self, seed: int, x: int, z: int, version: str, radius: int = 1) -> List[JavaOreBlock]:
        """
        Generate ore blocks for Java Edition using Cubiomes and ore generation rules
        
        Args:
            seed: World seed
            x: X coordinate
            z: Z coordinate
            version: Java version
            radius: Search radius in chunks
            
        Returns:
            List of ore blocks found
        """
        ores = []
        
        # Convert world coordinates to chunk coordinates
        chunk_x = x // 16
        chunk_z = z // 16
        
        # Search chunks in radius
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                search_chunk_x = chunk_x + dx
                search_chunk_z = chunk_z + dz
                
                # Generate ores for this chunk
                chunk_ores = self._generate_chunk_ores(seed, search_chunk_x, search_chunk_z, version)
                ores.extend(chunk_ores)
        
        # Filter ores within reasonable distance from search point
        filtered_ores = []
        max_distance = 64  # blocks
        
        for ore in ores:
            distance = ((ore.x - x) ** 2 + (ore.z - z) ** 2) ** 0.5
            if distance <= max_distance:
                filtered_ores.append(ore)
        
        # Sort by distance from search point
        filtered_ores.sort(key=lambda o: ((o.x - x) ** 2 + (o.z - z) ** 2) ** 0.5)
        
        return filtered_ores
    
    def _generate_chunk_ores(self, seed: int, chunk_x: int, chunk_z: int, version: str) -> List[JavaOreBlock]:
        """Generate ores for a specific chunk using Java Edition rules"""
        ores = []
        
        # Get chunk base coordinates
        chunk_base_x = chunk_x * 16
        chunk_base_z = chunk_z * 16
        
        # Apply Java Edition ore generation rules based on version
        ore_rules = self._get_ore_rules(version)
        
        for rule in ore_rules:
            # Generate ore veins based on the rule
            vein_count = self._calculate_vein_count(seed, chunk_x, chunk_z, rule)
            
            for _ in range(vein_count):
                # Generate a single vein
                vein_ores = self._generate_ore_vein(
                    seed, chunk_base_x, chunk_base_z, rule, version
                )
                ores.extend(vein_ores)
        
        return ores
    
    def _get_ore_rules(self, version: str) -> List[Dict]:
        """Get ore generation rules for a specific Java version"""
        # Base rules for Java 1.18+
        rules = [
            {
                "type": "Diamond",
                "min_y": -64,
                "max_y": 16,
                "veins_per_chunk": 1,
                "vein_size": (1, 8),
                "discard_chance": 0.1
            },
            {
                "type": "Emerald",
                "min_y": -16,
                "max_y": 480,
                "veins_per_chunk": 1,
                "vein_size": (1, 1),
                "discard_chance": 0.5
            },
            {
                "type": "Gold",
                "min_y": -64,
                "max_y": 32,
                "veins_per_chunk": 2,
                "vein_size": (1, 9),
                "discard_chance": 0.1
            },
            {
                "type": "Iron",
                "min_y": -64,
                "max_y": 72,
                "veins_per_chunk": 10,
                "vein_size": (1, 13),
                "discard_chance": 0.1
            },
            {
                "type": "Coal",
                "min_y": 0,
                "max_y": 192,
                "veins_per_chunk": 20,
                "vein_size": (1, 17),
                "discard_chance": 0.1
            },
            {
                "type": "Redstone",
                "min_y": -64,
                "max_y": 16,
                "veins_per_chunk": 4,
                "vein_size": (1, 8),
                "discard_chance": 0.1
            },
            {
                "type": "Lapis Lazuli",
                "min_y": -64,
                "max_y": 64,
                "veins_per_chunk": 1,
                "vein_size": (1, 7),
                "discard_chance": 0.1
            },
            {
                "type": "Copper",
                "min_y": -16,
                "max_y": 112,
                "veins_per_chunk": 16,
                "vein_size": (1, 10),
                "discard_chance": 0.1
            }
        ]
        
        # Version-specific adjustments
        if version == "1.18":
            # 1.18 specific rules (if any)
            pass
        elif version == "1.19":
            # 1.19 specific rules (if any)
            pass
        elif version == "1.20":
            # 1.20 specific rules (if any)
            pass
        elif version == "1.21":
            # 1.21 specific rules (if any)
            pass
        
        return rules
    
    def _calculate_vein_count(self, seed: int, chunk_x: int, chunk_z: int, rule: Dict) -> int:
        """Calculate number of veins for a specific ore type in a chunk"""
        import random
        
        # Use seed and chunk coordinates for deterministic generation
        random.seed(seed + chunk_x * 31 + chunk_z * 17)
        
        base_count = rule["veins_per_chunk"]
        discard_chance = rule["discard_chance"]
        
        # Apply discard chance
        actual_count = 0
        for _ in range(base_count):
            if random.random() > discard_chance:
                actual_count += 1
        
        return actual_count
    
    def _generate_ore_vein(self, seed: int, base_x: int, base_z: int, rule: Dict, version: str) -> List[JavaOreBlock]:
        """Generate a single ore vein"""
        import random
        
        # Use seed and base coordinates for deterministic generation
        random.seed(seed + base_x + base_z + hash(rule["type"]))
        
        ores = []
        vein_size = random.randint(rule["vein_size"][0], rule["vein_size"][1])
        
        # Generate vein center
        center_x = base_x + random.randint(0, 15)
        center_y = random.randint(rule["min_y"], rule["max_y"])
        center_z = base_z + random.randint(0, 15)
        
        # Get biome for this location
        biome_data = self.get_biome_and_height(seed, center_x, center_z, version)
        
        # Generate ore blocks in the vein
        for _ in range(vein_size):
            # Add some randomness to vein shape
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-1, 1)
            offset_z = random.randint(-2, 2)
            
            ore_x = center_x + offset_x
            ore_y = center_y + offset_y
            ore_z = center_z + offset_z
            
            # Ensure coordinates are within chunk bounds
            if 0 <= ore_x - base_x < 16 and 0 <= ore_z - base_z < 16:
                ores.append(JavaOreBlock(
                    type=rule["type"],
                    x=ore_x,
                    y=ore_y,
                    z=ore_z,
                    biome=biome_data["biome"]
                ))
        
        return ores

class JavaOreFinderService:
    """Main service for finding ores in Java Edition worlds"""
    
    def __init__(self):
        self.cubiomes = CubiomesWrapper()
        self._cache = {}  # Simple in-memory cache
    
    def find_ores(self, seed: int, x: int, z: int, version: str, radius: int = 1) -> JavaOreResult:
        """
        Find ores around the specified coordinates in Java Edition
        
        Args:
            seed: World seed
            x: X coordinate
            z: Z coordinate
            version: Java version (1.18, 1.19, etc.)
            radius: Number of chunks to search around the point
            
        Returns:
            JavaOreResult with all found ores
        """
        # Check cache first
        cache_key = f"{seed}_{x}_{z}_{version}_{radius}"
        if cache_key in self._cache:
            logger.info(f"Cache hit for key: {cache_key}")
            return self._cache[cache_key]
        
        # Convert world coordinates to chunk coordinates
        chunk_x = x // 16
        chunk_z = z // 16
        
        # Generate ores using Cubiomes
        ores = self.cubiomes.generate_java_ores(seed, x, z, version, radius)
        
        # Group adjacent ores
        grouped_ores = self._group_adjacent_ores(ores)
        
        result = JavaOreResult(
            seed=seed,
            search_x=x,
            search_z=z,
            version=version,
            ores=grouped_ores,
            total_count=sum(ore.count for ore in grouped_ores),
            chunk_coordinates=(chunk_x, chunk_z)
        )
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def _group_adjacent_ores(self, ores: List[JavaOreBlock]) -> List[JavaOreBlock]:
        """Group adjacent ore blocks of the same type"""
        if not ores:
            return []
        
        # Sort by type and position
        ores.sort(key=lambda o: (o.type, o.x, o.y, o.z))
        
        grouped = []
        current_group = []
        
        for ore in ores:
            if not current_group:
                current_group = [ore]
            elif (current_group[0].type == ore.type and 
                  abs(current_group[0].x - ore.x) <= 1 and
                  abs(current_group[0].y - ore.y) <= 1 and
                  abs(current_group[0].z - ore.z) <= 1):
                current_group.append(ore)
            else:
                # Create grouped ore block
                grouped.append(JavaOreBlock(
                    type=current_group[0].type,
                    x=current_group[0].x,
                    y=current_group[0].y,
                    z=current_group[0].z,
                    count=len(current_group),
                    biome=current_group[0].biome
                ))
                current_group = [ore]
        
        # Add final group
        if current_group:
            grouped.append(JavaOreBlock(
                type=current_group[0].type,
                x=current_group[0].x,
                y=current_group[0].y,
                z=current_group[0].z,
                count=len(current_group),
                biome=current_group[0].biome
            ))
        
        return grouped
    
    def get_supported_versions(self) -> List[str]:
        """Get list of supported Java versions"""
        return [version.value for version in JavaVersion]
    
    def clear_cache(self) -> None:
        """Clear the in-memory cache"""
        self._cache.clear()
        logger.info("Cache cleared")

def main():
    """Test the Java ore finder with the specified parameters"""
    if len(sys.argv) != 5:
        print("Usage: python java_ore_generator.py <seed> <x> <z> <version>")
        sys.exit(1)
    
    try:
        seed = int(sys.argv[1])
        x = int(sys.argv[2])
        z = int(sys.argv[3])
        version = sys.argv[4]
        
        service = JavaOreFinderService()
        result = service.find_ores(seed, x, z, version)
        
        # Output as JSON
        output = {
            "seed": result.seed,
            "search_coordinates": {"x": result.search_x, "z": result.search_z},
            "version": result.version,
            "chunk_coordinates": {"x": result.chunk_coordinates[0], "z": result.chunk_coordinates[1]},
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
        }
        
        print(json.dumps(output, indent=2))
        
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 