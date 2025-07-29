#!/usr/bin/env python3
"""
Test the Minecraft Server Enricher with a small sample
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from server_enricher import ServerEnricher

async def test_enricher():
    """Test the enricher with a small sample"""
    print("🧪 Testing Minecraft Server Enricher...")
    
    # Create test server data (small sample)
    test_servers = [
        {
            "name": "Hypixel",
            "ip": "mc.hypixel.net",
            "description": "The most popular Minecraft server with minigames"
        },
        {
            "name": "2b2t",
            "ip": "2b2t.org", 
            "description": "Oldest anarchy server in Minecraft"
        },
        {
            "name": "Wynncraft",
            "ip": "play.wynncraft.com",
            "description": "MMORPG server with custom classes"
        },
        {
            "name": "The Hive",
            "ip": "play.hivebedrock.network",
            "description": "Popular Bedrock minigame server"
        },
        {
            "name": "NetherGames",
            "ip": "play.nethergames.org",
            "description": "Large Bedrock minigame network"
        }
    ]
    
    enricher = ServerEnricher("test_servers.db")
    
    async with enricher:
        # Initialize database
        print("🗄️  Initializing test database...")
        enricher.init_database()
        
        # Process test servers
        print("⚡ Processing test servers...")
        for server_data in test_servers:
            enriched_data = await enricher.enrich_server_data(server_data)
            if enriched_data:
                await enricher.save_server_to_db(enriched_data)
                print(f"✅ Processed: {enriched_data.name} ({'Online' if enriched_data.online else 'Offline'})")
            else:
                print(f"❌ Failed to process: {server_data['name']}")
        
        # Export test data
        print("💾 Exporting test data...")
        enricher.export_to_json("test_enriched_servers.json")
        
        # Test iOS format export
        print("📱 Testing iOS format export...")
        try:
            with open("test_enriched_servers.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ios_servers = []
            for server in data['servers']['all']:
                ios_server = {
                    'name': server['name'],
                    'address': server['ip'],
                    'description': server.get('motd', server['name']),
                    'category': 'popular',
                    'tags': server['tags'],
                    'isBedrock': server['is_bedrock'],
                    'status': {
                        'isOnline': server['online'],
                        'playerCount': server.get('player_count'),
                        'maxPlayers': server.get('max_players'),
                        'version': server.get('version'),
                        'motd': server.get('motd'),
                        'software': server.get('software'),
                        'iconData': server.get('icon'),
                        'plugins': [],
                        'mods': []
                    },
                    'lastUpdated': server.get('last_updated')
                }
                ios_servers.append(ios_server)
            
            ios_data = {
                'metadata': {
                    'total_servers': len(ios_servers),
                    'online_servers': len([s for s in ios_servers if s['status']['isOnline']]),
                    'offline_servers': len([s for s in ios_servers if not s['status']['isOnline']]),
                    'java_servers': len([s for s in ios_servers if not s['isBedrock']]),
                    'bedrock_servers': len([s for s in ios_servers if s['isBedrock']]),
                    'last_updated': data['metadata']['last_updated']
                },
                'servers': ios_servers
            }
            
            with open("test_ios_servers.json", 'w', encoding='utf-8') as f:
                json.dump(ios_data, f, indent=2, ensure_ascii=False)
            
            print(f"📱 Exported {len(ios_servers)} test servers in iOS format")
            
        except Exception as e:
            print(f"❌ Error exporting iOS format: {e}")
    
    print("✅ Test completed!")
    print("📁 Generated files:")
    print("   - test_servers.db (SQLite database)")
    print("   - test_enriched_servers.json (Full data)")
    print("   - test_ios_servers.json (iOS format)")

if __name__ == "__main__":
    asyncio.run(test_enricher()) 