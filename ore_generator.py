#!/usr/bin/env python3
"""
DiamondFinder Ore Generator Backend
Integrates ext-vanillagenerator for accurate Bedrock ore generation
"""

import json
import subprocess
import sys
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OreBlock:
    """Represents a single ore block found in the world"""
    type: str
    x: int
    y: int
    z: int
    count: int = 1

@dataclass
class OreResult:
    """Complete result of an ore search"""
    seed: int
    search_x: int
    search_z: int
    ores: List[OreBlock]
    total_count: int
    chunk_coordinates: Tuple[int, int]

class VanillaGeneratorWrapper:
    """Wrapper for the ext-vanillagenerator C++ library"""
    
    def __init__(self, generator_path: str = "./vanilla_generator"):
        """
        Initialize the wrapper
        
        Args:
            generator_path: Path to the compiled vanilla generator executable
        """
        self.generator_path = generator_path
        self._validate_generator()
    
    def _validate_generator(self) -> None:
        """Validate that the generator executable exists and is working"""
        if not os.path.exists(self.generator_path):
            raise FileNotFoundError(f"Generator not found at: {self.generator_path}")
        
        # Test the generator
        try:
            result = subprocess.run([self.generator_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                logger.warning(f"Generator version check failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.warning("Generator version check timed out")
        except Exception as e:
            logger.warning(f"Generator validation failed: {e}")
    
    def generate_chunk_ores(self, seed: int, chunk_x: int, chunk_z: int) -> List[OreBlock]:
        """
        Generate ore blocks for a specific chunk
        
        Args:
            seed: World seed
            chunk_x: Chunk X coordinate
            chunk_z: Chunk Z coordinate
            
        Returns:
            List of ore blocks found in the chunk
        """
        try:
            # Call the generator
            cmd = [
                self.generator_path,
                str(seed),
                str(chunk_x),
                str(chunk_z)
            ]
            
            logger.info(f"Generating chunk: seed={seed}, chunk_x={chunk_x}, chunk_z={chunk_z}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Generator failed: {result.stderr}")
                return []
            
            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                return self._parse_generator_output(data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse generator output: {e}")
                return []
                
        except subprocess.TimeoutExpired:
            logger.error("Generator timed out")
            return []
        except Exception as e:
            logger.error(f"Generator error: {e}")
            return []
    
    def _parse_generator_output(self, data: Dict) -> List[OreBlock]:
        """Parse the JSON output from the generator"""
        ores = []
        
        try:
            # Handle mock generator format
            if "ores" in data:
                for ore_data in data["ores"]:
                    ore_type = self._map_ore_type(ore_data["type"])
                    ores.append(OreBlock(
                        type=ore_type,
                        x=ore_data["x"],
                        y=ore_data["y"],
                        z=ore_data["z"],
                        count=ore_data["count"]
                    ))
                return ores
            
            # Expected format from ext-vanillagenerator
            if "blocks" in data:
                for block in data["blocks"]:
                    if block.get("type") in ["diamond_ore", "emerald_ore", "gold_ore", 
                                           "iron_ore", "coal_ore", "redstone_ore", 
                                           "lapis_ore", "copper_ore"]:
                        ore_type = self._map_ore_type(block["type"])
                        ores.append(OreBlock(
                            type=ore_type,
                            x=block["x"],
                            y=block["y"],
                            z=block["z"]
                        ))
            
            # Group adjacent ores
            return self._group_adjacent_ores(ores)
            
        except Exception as e:
            logger.error(f"Failed to parse generator data: {e}")
            return []
    
    def _map_ore_type(self, minecraft_type: str) -> str:
        """Map Minecraft ore types to our app's ore types"""
        mapping = {
            "diamond_ore": "Diamond",
            "diamond": "Diamond",
            "emerald_ore": "Emerald",
            "emerald": "Emerald", 
            "gold_ore": "Gold",
            "gold": "Gold",
            "iron_ore": "Iron",
            "iron": "Iron",
            "coal_ore": "Coal",
            "coal": "Coal",
            "redstone_ore": "Redstone",
            "redstone": "Redstone",
            "lapis_ore": "Lapis Lazuli",
            "lapis_lazuli": "Lapis Lazuli",
            "copper_ore": "Copper",
            "copper": "Copper"
        }
        return mapping.get(minecraft_type, minecraft_type)
    
    def _group_adjacent_ores(self, ores: List[OreBlock]) -> List[OreBlock]:
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
                grouped.append(OreBlock(
                    type=current_group[0].type,
                    x=current_group[0].x,
                    y=current_group[0].y,
                    z=current_group[0].z,
                    count=len(current_group)
                ))
                current_group = [ore]
        
        # Add final group
        if current_group:
            grouped.append(OreBlock(
                type=current_group[0].type,
                x=current_group[0].x,
                y=current_group[0].y,
                z=current_group[0].z,
                count=len(current_group)
            ))
        
        return grouped

class OreFinderService:
    """Main service for finding ores in Minecraft worlds"""
    
    def __init__(self):
        self.generator = VanillaGeneratorWrapper()
    
    def find_ores(self, seed: int, x: int, z: int, radius: int = 1, ore_type: str = None, ore_types: List[str] = None) -> OreResult:
        """
        Find ores around the specified coordinates
        
        Args:
            seed: World seed
            x: X coordinate
            z: Z coordinate
            radius: Number of chunks to search around the point
            
        Returns:
            OreResult with all found ores
        """
        # Convert world coordinates to chunk coordinates
        chunk_x = x // 16
        chunk_z = z // 16
        
        all_ores = []
        
        # Search chunks in radius
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                search_chunk_x = chunk_x + dx
                search_chunk_z = chunk_z + dz
                
                chunk_ores = self.generator.generate_chunk_ores(seed, search_chunk_x, search_chunk_z)
                all_ores.extend(chunk_ores)
        
        # Filter ores within reasonable distance from search point
        filtered_ores = []
        max_distance = 64  # blocks
        
        for ore in all_ores:
            distance = ((ore.x - x) ** 2 + (ore.z - z) ** 2) ** 0.5
            if distance <= max_distance:
                filtered_ores.append(ore)
        
        # Filter by ore type(s) if specified
        if ore_type or ore_types:
            # Handle both single ore type and multiple ore types
            target_types = []
            if ore_type:
                target_types.append(ore_type.lower())
            if ore_types:
                target_types.extend([ot.lower() for ot in ore_types])
            
            # Remove duplicates and filter
            target_types = list(set(target_types))
            filtered_ores = [ore for ore in filtered_ores if ore.type.lower() in target_types]
        
        # Sort by distance from search point
        filtered_ores.sort(key=lambda o: ((o.x - x) ** 2 + (o.z - z) ** 2) ** 0.5)
        
        return OreResult(
            seed=seed,
            search_x=x,
            search_z=z,
            ores=filtered_ores,
            total_count=sum(ore.count for ore in filtered_ores),
            chunk_coordinates=(chunk_x, chunk_z)
        )

def main():
    """Test the ore finder with the specified parameters"""
    if len(sys.argv) != 4:
        print("Usage: python ore_generator.py <seed> <x> <z>")
        sys.exit(1)
    
    try:
        seed = int(sys.argv[1])
        x = int(sys.argv[2])
        z = int(sys.argv[3])
        
        service = OreFinderService()
        result = service.find_ores(seed, x, z)
        
        # Output as JSON
        output = {
            "seed": result.seed,
            "search_coordinates": {"x": result.search_x, "z": result.search_z},
            "chunk_coordinates": {"x": result.chunk_coordinates[0], "z": result.chunk_coordinates[1]},
            "total_ores": result.total_count,
            "ore_locations": [
                {
                    "type": ore.type,
                    "coordinates": {"x": ore.x, "y": ore.y, "z": ore.z},
                    "count": ore.count
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