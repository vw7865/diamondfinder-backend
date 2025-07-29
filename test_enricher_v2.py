#!/usr/bin/env python3
"""
Test script for Server Enricher V2
Uses sample server data to test the enrichment functionality
"""

import asyncio
import json
from server_enricher_v2 import ServerEnricherV2

# Sample server data for testing
SAMPLE_SERVERS = [
    {
        "name": "Hypixel",
        "ip": "mc.hypixel.net",
        "description": "The largest Minecraft server network",
        "category": "minigames"
    },
    {
        "name": "2b2t",
        "ip": "2b2t.org",
        "description": "Anarchy server",
        "category": "anarchy"
    },
    {
        "name": "Wynncraft",
        "ip": "play.wynncraft.com",
        "description": "MMORPG server",
        "category": "rpg"
    },
    {
        "name": "NetherGames",
        "ip": "play.nethergames.org",
        "description": "Bedrock minigames server",
        "category": "minigames"
    },
    {
        "name": "The Hive",
        "ip": "play.hivebedrock.network",
        "description": "Bedrock server",
        "category": "minigames"
    }
]

async def test_enricher():
    """Test the server enricher with sample data"""
    print("🧪 Testing Server Enricher V2...")
    
    enricher = ServerEnricherV2(db_path="test_servers_v2.db")
    
    async with enricher:
        # Initialize database
        print("🗄️  Initializing database...")
        enricher.init_database()
        
        # Process sample servers
        print("⚡ Processing sample servers...")
        
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        
        async def process_single_server(server_data):
            async with semaphore:
                enriched_data = await enricher.enrich_server_data(server_data)
                if enriched_data:
                    await enricher.save_server_to_db(enriched_data)
                    print(f"✅ Processed: {enriched_data.name} ({enriched_data.ip}) - Online: {enriched_data.online}")
                else:
                    print(f"❌ Failed to process: {server_data['name']}")
                await asyncio.sleep(0.5)
        
        # Create tasks for all sample servers
        tasks = [process_single_server(server) for server in SAMPLE_SERVERS]
        
        # Process all servers
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Export to JSON
        print("💾 Exporting enriched data to JSON...")
        enricher.export_to_json("test_enriched_servers_v2.json")
        
        # Also export iOS format
        export_ios_format(enricher)
    
    print("✅ Test completed!")

def export_ios_format(enricher: ServerEnricherV2):
    """Export data in a format suitable for iOS app"""
    try:
        # Read the enriched data
        with open("test_enriched_servers_v2.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to iOS app format
        ios_servers = []
        
        for server in data['servers']['all']:
            # Determine category based on tags and metadata
            category = determine_ios_category(server)
            
            ios_server = {
                'name': server['name'],
                'address': server['ip'],
                'description': server.get('motd', server['name']),
                'category': category,
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
        
        # Create iOS format data
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
        
        # Save iOS format
        with open("test_ios_servers_v2.json", 'w', encoding='utf-8') as f:
            json.dump(ios_data, f, indent=2, ensure_ascii=False)
        
        print(f"📱 Exported {len(ios_servers)} servers in iOS format to test_ios_servers_v2.json")
        
        # Print summary
        online_count = len([s for s in ios_servers if s['status']['isOnline']])
        java_count = len([s for s in ios_servers if not s['isBedrock']])
        bedrock_count = len([s for s in ios_servers if s['isBedrock']])
        
        print(f"📊 Summary:")
        print(f"   Total servers: {len(ios_servers)}")
        print(f"   Online servers: {online_count}")
        print(f"   Java servers: {java_count}")
        print(f"   Bedrock servers: {bedrock_count}")
        
    except Exception as e:
        print(f"❌ Error exporting iOS format: {e}")

def determine_ios_category(server: dict) -> str:
    """Determine iOS app category based on server data"""
    tags = server.get('tags', [])
    name_lower = server['name'].lower()
    motd_lower = server.get('motd', '').lower() if server.get('motd') else ''
    
    # Check for specific categories
    if any(tag.lower() in ['anarchy'] for tag in tags) or 'anarchy' in name_lower:
        return 'anarchy'
    elif any(tag.lower() in ['survival', 'vanilla'] for tag in tags) or 'survival' in name_lower:
        return 'survival'
    elif any(tag.lower() in ['minigames', 'bedwars', 'skywars', 'pvp'] for tag in tags):
        return 'minigames'
    elif any(tag.lower() in ['skyblock'] for tag in tags) or 'skyblock' in name_lower:
        return 'skyblock'
    elif any(tag.lower() in ['creative', 'build'] for tag in tags):
        return 'creative'
    elif any(tag.lower() in ['rpg', 'mmorpg'] for tag in tags):
        return 'rpg'
    elif any(tag.lower() in ['pvp'] for tag in tags):
        return 'pvp'
    elif any(tag.lower() in ['factions'] for tag in tags):
        return 'factions'
    elif any(tag.lower() in ['prison'] for tag in tags):
        return 'prison'
    else:
        return 'popular'

if __name__ == "__main__":
    asyncio.run(test_enricher()) 