# Minecraft Server Enricher

A Python backend that fetches server data from [LunarClient ServerMappings](https://github.com/LunarClient/ServerMappings) and enriches it with live status data from [MCSRVSTAT.US API](https://api.mcsrvstat.us/).

## Features

- **Fetches 1000+ servers** from LunarClient's curated server list
- **Live status enrichment** using MCSRVSTAT.US API
- **SQLite database storage** for persistent data
- **JSON export** in multiple formats
- **Rate limiting** to be respectful to APIs
- **Automatic categorization** (Java/Bedrock, server types)
- **Error handling** for failed pings
- **iOS app integration** with formatted output

## Data Sources

### LunarClient ServerMappings
- **URL**: https://raw.githubusercontent.com/LunarClient/ServerMappings/master/servers.json
- **Content**: Curated list of popular Minecraft servers with metadata
- **Format**: JSON with server names, IPs, descriptions, categories

### MCSRVSTAT.US API
- **URL**: https://api.mcsrvstat.us/2/{server_ip}
- **Content**: Live server status information
- **Data**: Online status, player count, version, MOTD, software, ping

## Installation

1. **Install dependencies**:
```bash
pip install aiohttp
```

2. **Run the enricher**:
```bash
python run_server_enricher.py
```

## Output Files

### `servers.db` (SQLite Database)
- Complete server data with live status
- Indexed for fast queries
- Persistent storage

### `enriched_servers.json` (Full Data)
```json
{
  "metadata": {
    "total_servers": 1000,
    "online_servers": 750,
    "offline_servers": 250,
    "java_servers": 800,
    "bedrock_servers": 200,
    "last_updated": "2025-01-26T10:30:00"
  },
  "servers": {
    "all": [...],
    "online": [...],
    "offline": [...],
    "java": [...],
    "bedrock": [...]
  }
}
```

### `ios_servers.json` (iOS App Format)
- Optimized for iOS app consumption
- Matches existing `Server` model structure
- Categorized and tagged for filtering

## Server Categories

The enricher automatically categorizes servers based on metadata:

- **Popular**: Hypixel, Mineplex, CubeCraft, etc.
- **Survival**: HermitCraft, vanilla servers
- **Minigames**: Bedwars, Skywars, practice servers
- **Skyblock**: Skyblock-specific servers
- **Creative**: Building servers, BuildTheEarth
- **RPG**: MMORPG servers, Wynncraft
- **PvP**: Combat-focused servers
- **Factions**: Factions servers
- **Prison**: Prison servers
- **Anarchy**: 2b2t, anarchy servers

## Server Tags

Automatic tag generation based on server metadata:

- **Java/Bedrock**: Server edition
- **Category tags**: Survival, Minigames, Skyblock, etc.
- **Feature tags**: Free, Economy, Vanilla, Modded, etc.

## Rate Limiting

- **Concurrent requests**: 5 (configurable)
- **Delay between requests**: 0.1 seconds
- **Timeout**: 30 seconds per request
- **User-Agent**: DiamondFinder-ServerEnricher/1.0

## Error Handling

- **Failed pings**: Marked as offline, logged
- **Timeout errors**: Retry with exponential backoff
- **API errors**: Graceful degradation
- **Network issues**: Detailed logging

## Integration with iOS App

The enricher generates `ios_servers.json` that can be:

1. **Loaded directly** into the iOS app
2. **Served via API** from the backend
3. **Updated periodically** for fresh data

### iOS Data Format
```json
{
  "name": "Hypixel",
  "address": "mc.hypixel.net",
  "description": "The most popular Minecraft server",
  "category": "popular",
  "tags": ["Java", "Minigames", "Bedwars", "Skywars"],
  "isBedrock": false,
  "status": {
    "isOnline": true,
    "playerCount": 50000,
    "maxPlayers": 100000,
    "version": "1.8.8-1.21",
    "motd": "Welcome to Hypixel!",
    "software": "BungeeCord",
    "iconData": "data:image/png;base64,...",
    "plugins": [],
    "mods": []
  },
  "lastUpdated": "2025-01-26T10:30:00"
}
```

## Usage Examples

### Run Full Enrichment
```bash
python run_server_enricher.py
```

### Use in Python Code
```python
from server_enricher import ServerEnricher
import asyncio

async def main():
    enricher = ServerEnricher()
    async with enricher:
        enricher.init_database()
        await enricher.process_servers()
        enricher.export_to_json()

asyncio.run(main())
```

### Query Database
```python
import sqlite3

conn = sqlite3.connect('servers.db')
cursor = conn.cursor()

# Get all online servers
cursor.execute("SELECT name, ip, player_count FROM servers WHERE online = 1")
online_servers = cursor.fetchall()

# Get Java servers only
cursor.execute("SELECT name, ip FROM servers WHERE is_bedrock = 0")
java_servers = cursor.fetchall()

conn.close()
```

## Performance

- **Processing time**: ~10-15 minutes for 1000+ servers
- **Database size**: ~2-5 MB
- **Memory usage**: ~50-100 MB
- **Network usage**: ~10-20 MB

## Monitoring

- **Log file**: `server_enricher.log`
- **Console output**: Real-time progress
- **Error tracking**: Detailed error logging
- **Success metrics**: Server counts and statistics

## Future Enhancements

- **Scheduled updates**: Cron job integration
- **API endpoint**: Serve data via REST API
- **Caching**: Redis integration for faster queries
- **Analytics**: Server popularity tracking
- **Notifications**: Alert on server status changes

## License

MIT License - Same as LunarClient ServerMappings 