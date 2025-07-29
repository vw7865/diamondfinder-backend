#!/usr/bin/env python3
"""
Run the Minecraft Server Enricher
This script fetches server data from LunarClient ServerMappings and enriches it with live status
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from server_enricher import ServerEnricher

async def run_enricher():
    """Run the server enricher"""
    print("🚀 Starting Minecraft Server Enricher...")
    print("📡 Fetching server data from LunarClient ServerMappings...")
    print("🌐 Enriching with live data from MCSRVSTAT.US API...")
    
    enricher = ServerEnricher()
    
    async with enricher:
        # Initialize database
        print("🗄️  Initializing database...")
        enricher.init_database()
        
        # Process servers with conservative rate limiting
        print("⚡ Processing servers (rate limited to 5 concurrent requests)...")
        await enricher.process_servers(max_concurrent=5)
        
        # Export to JSON
        print("💾 Exporting enriched data to JSON...")
        enricher.export_to_json("enriched_servers.json")
        
        # Also export a simplified version for iOS
        export_ios_format(enricher)
    
    print("✅ Server enrichment completed!")

def export_ios_format(enricher: ServerEnricher):
    """Export data in a format suitable for iOS app"""
    try:
        # Read the enriched data
        with open("enriched_servers.json", 'r', encoding='utf-8') as f:
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
        with open("ios_servers.json", 'w', encoding='utf-8') as f:
            json.dump(ios_data, f, indent=2, ensure_ascii=False)
        
        print(f"📱 Exported {len(ios_servers)} servers in iOS format to ios_servers.json")
        
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
    motd_lower = server.get('motd', '').lower()
    
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
    asyncio.run(run_enricher()) 