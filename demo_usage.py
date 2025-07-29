#!/usr/bin/env python3
"""
Demo script showing how to use the enriched server data
"""

import json
import sqlite3
from typing import List, Dict, Any

def load_enriched_data(json_file: str = "test_enriched_servers_v2.json") -> Dict[str, Any]:
    """Load enriched server data from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File {json_file} not found. Run test_enricher_v2.py first.")
        return None

def demo_basic_queries(data: Dict[str, Any]):
    """Demonstrate basic queries on the enriched data"""
    print("🔍 Basic Queries Demo")
    print("=" * 50)
    
    servers = data['servers']['all']
    
    # Find most popular servers
    online_servers = [s for s in servers if s['online']]
    popular_servers = sorted(online_servers, key=lambda x: x.get('player_count', 0), reverse=True)[:5]
    
    print(f"\n🏆 Top 5 Most Popular Servers:")
    for i, server in enumerate(popular_servers, 1):
        print(f"  {i}. {server['name']} ({server['ip']})")
        print(f"     Players: {server.get('player_count', 'N/A')}/{server.get('max_players', 'N/A')}")
        print(f"     Category: {server['category']}")
        print(f"     Tags: {', '.join(server['tags'])}")
        print()
    
    # Find servers by category
    categories = {}
    for server in servers:
        category = server['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(server)
    
    print(f"📊 Servers by Category:")
    for category, category_servers in categories.items():
        online_count = len([s for s in category_servers if s['online']])
        print(f"  {category.title()}: {len(category_servers)} total, {online_count} online")
    
    # Find Java vs Bedrock servers
    java_servers = [s for s in servers if not s['is_bedrock']]
    bedrock_servers = [s for s in servers if s['is_bedrock']]
    
    print(f"\n🎮 Server Types:")
    print(f"  Java Edition: {len(java_servers)} servers")
    print(f"  Bedrock Edition: {len(bedrock_servers)} servers")

def demo_advanced_queries(data: Dict[str, Any]):
    """Demonstrate advanced queries and filtering"""
    print("\n🔬 Advanced Queries Demo")
    print("=" * 50)
    
    servers = data['servers']['all']
    
    # Find servers with specific tags
    minigame_servers = [s for s in servers if 'Minigames' in s['tags']]
    anarchy_servers = [s for s in servers if 'Anarchy' in s['tags']]
    rpg_servers = [s for s in servers if 'RPG' in s['tags']]
    
    print(f"\n🎯 Servers by Game Type:")
    print(f"  Minigames: {len(minigame_servers)} servers")
    print(f"  Anarchy: {len(anarchy_servers)} servers")
    print(f"  RPG: {len(rpg_servers)} servers")
    
    # Find servers with high player counts
    high_population = [s for s in servers if s.get('player_count') and s.get('player_count', 0) > 1000]
    print(f"\n👥 High Population Servers (>1000 players): {len(high_population)}")
    
    # Find servers with specific software
    software_types = {}
    for server in servers:
        software = server.get('software')
        if software:
            if software not in software_types:
                software_types[software] = []
            software_types[software].append(server)
    
    if software_types:
        print(f"\n⚙️  Servers by Software:")
        for software, software_servers in software_types.items():
            print(f"  {software}: {len(software_servers)} servers")

def demo_database_queries(db_path: str = "test_servers_v2.db"):
    """Demonstrate SQL queries on the database"""
    print("\n🗄️  Database Queries Demo")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total server count
        cursor.execute("SELECT COUNT(*) FROM servers")
        total = cursor.fetchone()[0]
        print(f"📈 Total servers in database: {total}")
        
        # Get online server count
        cursor.execute("SELECT COUNT(*) FROM servers WHERE online = 1")
        online = cursor.fetchone()[0]
        print(f"🟢 Online servers: {online}")
        
        # Get average player count
        cursor.execute("SELECT AVG(player_count) FROM servers WHERE online = 1 AND player_count IS NOT NULL")
        avg_players = cursor.fetchone()[0]
        if avg_players:
            print(f"👥 Average players per online server: {avg_players:.0f}")
        
        # Get servers by category
        cursor.execute("""
            SELECT category, COUNT(*) as count, 
                   SUM(CASE WHEN online = 1 THEN 1 ELSE 0 END) as online_count
            FROM servers 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        print(f"\n📊 Servers by Category (Database):")
        for row in cursor.fetchall():
            category, total_count, online_count = row
            print(f"  {category or 'Unknown'}: {total_count} total, {online_count} online")
        
        # Get fastest responding servers
        cursor.execute("""
            SELECT name, ip, ping_ms 
            FROM servers 
            WHERE online = 1 AND ping_ms IS NOT NULL 
            ORDER BY ping_ms ASC 
            LIMIT 5
        """)
        
        print(f"\n⚡ Fastest Responding Servers:")
        for row in cursor.fetchall():
            name, ip, ping = row
            print(f"  {name} ({ip}): {ping}ms")
        
        conn.close()
        
    except sqlite3.OperationalError:
        print(f"❌ Database {db_path} not found. Run test_enricher_v2.py first.")

def demo_ios_integration(data: Dict[str, Any]):
    """Demonstrate iOS app integration"""
    print("\n📱 iOS Integration Demo")
    print("=" * 50)
    
    # Show how the data is structured for iOS
    ios_servers = []
    for server in data['servers']['all']:
        ios_server = {
            'name': server['name'],
            'address': server['ip'],
            'description': server.get('motd', server['name']),
            'category': server['category'],
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
    
    # Show sample iOS server data
    if ios_servers:
        sample = ios_servers[0]
        print(f"\n📋 Sample iOS Server Data:")
        print(f"  Name: {sample['name']}")
        print(f"  Address: {sample['address']}")
        print(f"  Category: {sample['category']}")
        print(f"  Online: {sample['status']['isOnline']}")
        print(f"  Players: {sample['status']['playerCount']}/{sample['status']['maxPlayers']}")
        print(f"  Tags: {', '.join(sample['tags'])}")
        print(f"  Bedrock: {sample['isBedrock']}")

def main():
    """Main demo function"""
    print("🚀 Minecraft Server Enricher V2 - Demo")
    print("=" * 60)
    
    # Load data
    data = load_enriched_data()
    if not data:
        return
    
    # Run demos
    demo_basic_queries(data)
    demo_advanced_queries(data)
    demo_database_queries()
    demo_ios_integration(data)
    
    print(f"\n✅ Demo completed!")
    print(f"\n💡 Tips:")
    print(f"  - Run 'python3 test_enricher_v2.py' to generate fresh data")
    print(f"  - Check the JSON files for complete server information")
    print(f"  - Use the database for complex queries and analytics")
    print(f"  - The iOS format is ready for mobile app integration")

if __name__ == "__main__":
    main() 