#!/usr/bin/env python3
"""
Minecraft Server Data Enricher
Fetches server data from LunarClient ServerMappings and enriches with MCSRVSTAT.US API
"""

import json
import sqlite3
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server_enricher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServerData:
    """Server data structure"""
    name: str
    ip: str
    port: Optional[int] = None
    motd: Optional[str] = None
    version: Optional[str] = None
    online: bool = False
    player_count: Optional[int] = None
    max_players: Optional[int] = None
    software: Optional[str] = None
    icon: Optional[str] = None
    tags: List[str] = None
    category: Optional[str] = None
    is_bedrock: bool = False
    last_updated: Optional[str] = None
    ping_ms: Optional[int] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class ServerEnricher:
    def __init__(self, db_path: str = "servers.db"):
        self.db_path = db_path
        self.session: Optional[aiohttp.ClientSession] = None
        self.lunar_client_url = "https://raw.githubusercontent.com/LunarClient/ServerMappings/master/servers.json"
        self.mcsrvstat_base_url = "https://api.mcsrvstat.us/2"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": self.user_agent},
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ip TEXT NOT NULL,
                port INTEGER,
                motd TEXT,
                version TEXT,
                online BOOLEAN DEFAULT FALSE,
                player_count INTEGER,
                max_players INTEGER,
                software TEXT,
                icon TEXT,
                tags TEXT,  -- JSON array
                category TEXT,
                is_bedrock BOOLEAN DEFAULT FALSE,
                last_updated TEXT,
                ping_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_online ON servers(online)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_bedrock ON servers(is_bedrock)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON servers(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip ON servers(ip)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    async def fetch_lunar_client_servers(self) -> List[Dict[str, Any]]:
        """Fetch server data from LunarClient ServerMappings"""
        try:
            logger.info(f"Fetching server data from {self.lunar_client_url}")
            async with self.session.get(self.lunar_client_url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched {len(data)} servers from LunarClient")
                    return data
                else:
                    logger.error(f"Failed to fetch LunarClient data: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching LunarClient data: {e}")
            return []
    
    async def fetch_server_status(self, server_ip: str, is_bedrock: bool = False) -> Optional[Dict[str, Any]]:
        """Fetch server status from MCSRVSTAT.US API"""
        try:
            endpoint = f"{self.mcsrvstat_base_url}/bedrock/{server_ip}" if is_bedrock else f"{self.mcsrvstat_base_url}/{server_ip}"
            
            start_time = time.time()
            async with self.session.get(endpoint) as response:
                ping_ms = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    data['ping_ms'] = ping_ms
                    return data
                elif response.status == 404:
                    logger.debug(f"Server {server_ip} is offline (404)")
                    return {"online": False, "ping_ms": ping_ms}
                elif response.status == 403:
                    logger.warning(f"Rate limited (403) for {server_ip}, treating as offline")
                    return {"online": False, "ping_ms": ping_ms, "rate_limited": True}
                elif response.status == 429:
                    logger.warning(f"Too many requests (429) for {server_ip}, treating as offline")
                    return {"online": False, "ping_ms": ping_ms, "rate_limited": True}
                else:
                    logger.warning(f"Unexpected status {response.status} for {server_ip}")
                    return {"online": False, "ping_ms": ping_ms}
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching status for {server_ip}")
            return None
        except Exception as e:
            logger.error(f"Error fetching status for {server_ip}: {e}")
            return None
    
    def determine_server_type(self, server_data: Dict[str, Any]) -> bool:
        """Determine if server is Bedrock based on metadata"""
        # Check for Bedrock indicators in server data
        name_lower = server_data.get('name', '').lower()
        description = server_data.get('description', '').lower()
        
        bedrock_indicators = [
            'bedrock', 'pe', 'pocket', 'mobile', 'win10', 'xbox',
            'hive', 'nethergames', 'galaxite', 'lifeboat'
        ]
        
        for indicator in bedrock_indicators:
            if indicator in name_lower or indicator in description:
                return True
        
        return False
    
    def extract_tags(self, server_data: Dict[str, Any]) -> List[str]:
        """Extract tags from server metadata"""
        tags = []
        
        # Add server type
        if self.determine_server_type(server_data):
            tags.append("Bedrock")
        else:
            tags.append("Java")
        
        # Add category-based tags
        category = server_data.get('category', '').lower()
        if category:
            tags.append(category.title())
        
        # Add common server types based on name/description
        name_lower = server_data.get('name', '').lower()
        description = server_data.get('description', '').lower()
        
        if any(word in name_lower or word in description for word in ['survival', 'vanilla']):
            tags.append("Survival")
        if any(word in name_lower or word in description for word in ['minigame', 'bedwars', 'skywars', 'pvp']):
            tags.append("Minigames")
        if any(word in name_lower or word in description for word in ['skyblock', 'sky block']):
            tags.append("Skyblock")
        if any(word in name_lower or word in description for word in ['creative', 'build']):
            tags.append("Creative")
        if any(word in name_lower or word in description for word in ['rpg', 'mmorpg']):
            tags.append("RPG")
        if any(word in name_lower or word in description for word in ['anarchy']):
            tags.append("Anarchy")
        if any(word in name_lower or word in description for word in ['factions']):
            tags.append("Factions")
        if any(word in name_lower or word in description for word in ['prison']):
            tags.append("Prison")
        
        return list(set(tags))  # Remove duplicates
    
    async def enrich_server_data(self, server_data: Dict[str, Any]) -> Optional[ServerData]:
        """Enrich server data with live status information"""
        try:
            server_ip = server_data.get('ip', '').strip()
            if not server_ip:
                logger.warning(f"Missing IP for server: {server_data.get('name', 'Unknown')}")
                return None
            
            # Determine if it's a Bedrock server
            is_bedrock = self.determine_server_type(server_data)
            
            # Fetch live status
            status_data = await self.fetch_server_status(server_ip, is_bedrock)
            
            # Extract tags
            tags = self.extract_tags(server_data)
            
            # Create enriched server data
            enriched_data = ServerData(
                name=server_data.get('name', 'Unknown'),
                ip=server_ip,
                port=status_data.get('port') if status_data else None,
                motd=status_data.get('motd', {}).get('clean', [None])[0] if status_data and status_data.get('motd') else None,
                version=status_data.get('version') if status_data else None,
                online=status_data.get('online', False) if status_data else False,
                player_count=status_data.get('players', {}).get('online') if status_data else None,
                max_players=status_data.get('players', {}).get('max') if status_data else None,
                software=status_data.get('software') if status_data else None,
                icon=status_data.get('icon') if status_data else None,
                tags=tags,
                category=server_data.get('category', 'Unknown'),
                is_bedrock=is_bedrock,
                last_updated=datetime.now().isoformat(),
                ping_ms=status_data.get('ping_ms') if status_data else None
            )
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error enriching server data for {server_data.get('name', 'Unknown')}: {e}")
            return None
    
    async def process_servers(self, max_concurrent: int = 10):
        """Process all servers with rate limiting"""
        # Fetch server data from LunarClient
        lunar_servers = await self.fetch_lunar_client_servers()
        if not lunar_servers:
            logger.error("No servers fetched from LunarClient")
            return
        
        logger.info(f"Processing {len(lunar_servers)} servers with max {max_concurrent} concurrent requests")
        
        # Process servers in batches to avoid overwhelming the API
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_server(server_data):
            async with semaphore:
                enriched_data = await self.enrich_server_data(server_data)
                if enriched_data:
                    await self.save_server_to_db(enriched_data)
                # Small delay to be respectful to the API
                await asyncio.sleep(0.5)
        
        # Create tasks for all servers
        tasks = [process_single_server(server) for server in lunar_servers]
        
        # Process all servers
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Server processing completed")
    
    async def save_server_to_db(self, server_data: ServerData):
        """Save enriched server data to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if server already exists
            cursor.execute("SELECT id FROM servers WHERE ip = ?", (server_data.ip,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing server
                cursor.execute('''
                    UPDATE servers SET
                        name = ?, port = ?, motd = ?, version = ?, online = ?,
                        player_count = ?, max_players = ?, software = ?, icon = ?,
                        tags = ?, category = ?, is_bedrock = ?, last_updated = ?,
                        ping_ms = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ip = ?
                ''', (
                    server_data.name, server_data.port, server_data.motd,
                    server_data.version, server_data.online, server_data.player_count,
                    server_data.max_players, server_data.software, server_data.icon,
                    json.dumps(server_data.tags), server_data.category,
                    server_data.is_bedrock, server_data.last_updated,
                    server_data.ping_ms, server_data.ip
                ))
            else:
                # Insert new server
                cursor.execute('''
                    INSERT INTO servers (
                        name, ip, port, motd, version, online, player_count,
                        max_players, software, icon, tags, category, is_bedrock,
                        last_updated, ping_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    server_data.name, server_data.ip, server_data.port,
                    server_data.motd, server_data.version, server_data.online,
                    server_data.player_count, server_data.max_players,
                    server_data.software, server_data.icon, json.dumps(server_data.tags),
                    server_data.category, server_data.is_bedrock,
                    server_data.last_updated, server_data.ping_ms
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving server {server_data.name} to database: {e}")
    
    def export_to_json(self, output_file: str = "enriched_servers.json"):
        """Export enriched server data to JSON file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, ip, port, motd, version, online, player_count,
                       max_players, software, icon, tags, category, is_bedrock,
                       last_updated, ping_ms
                FROM servers
                ORDER BY online DESC, player_count DESC NULLS LAST
            ''')
            
            servers = []
            for row in cursor.fetchall():
                server = {
                    'name': row[0],
                    'ip': row[1],
                    'port': row[2],
                    'motd': row[3],
                    'version': row[4],
                    'online': bool(row[5]),
                    'player_count': row[6],
                    'max_players': row[7],
                    'software': row[8],
                    'icon': row[9],
                    'tags': json.loads(row[10]) if row[10] else [],
                    'category': row[11],
                    'is_bedrock': bool(row[12]),
                    'last_updated': row[13],
                    'ping_ms': row[14]
                }
                servers.append(server)
            
            conn.close()
            
            # Group servers by status
            online_servers = [s for s in servers if s['online']]
            offline_servers = [s for s in servers if not s['online']]
            
            # Group by Java/Bedrock
            java_servers = [s for s in servers if not s['is_bedrock']]
            bedrock_servers = [s for s in servers if s['is_bedrock']]
            
            output_data = {
                'metadata': {
                    'total_servers': len(servers),
                    'online_servers': len(online_servers),
                    'offline_servers': len(offline_servers),
                    'java_servers': len(java_servers),
                    'bedrock_servers': len(bedrock_servers),
                    'last_updated': datetime.now().isoformat()
                },
                'servers': {
                    'all': servers,
                    'online': online_servers,
                    'offline': offline_servers,
                    'java': java_servers,
                    'bedrock': bedrock_servers
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(servers)} servers to {output_file}")
            logger.info(f"Online: {len(online_servers)}, Offline: {len(offline_servers)}")
            logger.info(f"Java: {len(java_servers)}, Bedrock: {len(bedrock_servers)}")
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

async def main():
    """Main function"""
    enricher = ServerEnricher()
    
    async with enricher:
        # Initialize database
        enricher.init_database()
        
        # Process servers
        await enricher.process_servers(max_concurrent=3)  # Conservative rate limiting
        
        # Export to JSON
        enricher.export_to_json()

if __name__ == "__main__":
    asyncio.run(main()) 