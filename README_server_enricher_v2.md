# Minecraft Server Enricher V2

A Python backend that fetches Minecraft server data from LunarClient ServerMappings and enriches it with live status information from the MCSRVSTAT.US API.

## Features

✅ **Fetches server data** from LunarClient ServerMappings repository  
✅ **Enriches with live data** from https://api.mcsrvstat.us/2/  
✅ **Saves to SQLite database** and JSON files  
✅ **Groups servers** by online status and Java/Bedrock  
✅ **Handles failed pings** gracefully with proper error handling  
✅ **Rate limiting** to be respectful to APIs  
✅ **Comprehensive data** including name, IP, MOTD, version, player count, tags, and status  
✅ **iOS app format** export for mobile applications  

## Quick Start

### Prerequisites

```bash
pip install -r requirements_server_enricher.txt
```

### Basic Usage

```bash
# Test with sample data
python3 test_enricher_v2.py

# Run the full enricher (when LunarClient API is available)
python3 server_enricher_v2.py
```

## How It Works

### 1. Data Sources

- **LunarClient ServerMappings**: Repository containing server metadata
- **MCSRVSTAT.US API**: Live server status and player information

### 2. Data Flow

```
LunarClient Repository → Server Metadata → MCSRVSTAT.US API → Enriched Data → Database/JSON
```

### 3. Server Types Detected

- **Java Edition**: Standard Minecraft servers
- **Bedrock Edition**: Mobile/console servers (detected by keywords)

### 4. Categories & Tags

Automatically categorizes servers based on:
- **Anarchy**: No rules servers
- **Survival**: Survival gameplay
- **Minigames**: Bedwars, Skywars, PvP games
- **Skyblock**: Skyblock gameplay
- **Creative**: Building servers
- **RPG**: Role-playing games
- **Factions**: Faction-based servers
- **Prison**: Prison servers

## Output Formats

### 1. SQLite Database

Stores all server data with indexes for efficient querying:

```sql
CREATE TABLE servers (
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
);
```

### 2. JSON Export

Structured JSON with metadata and grouped servers:

```json
{
  "metadata": {
    "total_servers": 5,
    "online_servers": 3,
    "offline_servers": 2,
    "java_servers": 3,
    "bedrock_servers": 2,
    "last_updated": "2025-07-28T17:14:36.370845"
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

### 3. iOS App Format

Optimized for mobile applications:

```json
{
  "name": "Hypixel",
  "address": "mc.hypixel.net",
  "description": "Hypixel Network [1.8-1.21]",
  "category": "minigames",
  "tags": ["Java", "Minigames"],
  "isBedrock": false,
  "status": {
    "isOnline": true,
    "playerCount": 30698,
    "maxPlayers": 200000,
    "version": "Requires MC 1.8 / 1.21",
    "motd": "Hypixel Network [1.8-1.21]",
    "software": null,
    "iconData": "data:image/png;base64,...",
    "plugins": [],
    "mods": []
  },
  "lastUpdated": "2025-07-28T17:14:34.147158"
}
```

## Configuration

### Rate Limiting

Adjust concurrent requests in the code:

```python
# Conservative rate limiting
await enricher.process_servers(max_concurrent=3)

# More aggressive (use with caution)
await enricher.process_servers(max_concurrent=10)
```

### Database Path

```python
enricher = ServerEnricherV2(db_path="my_servers.db")
```

### Output Files

```python
# JSON export
enricher.export_to_json("my_servers.json")

# iOS format export
export_ios_format(enricher, "ios_servers.json")
```

## Error Handling

The system gracefully handles:

- **404 errors**: Server offline
- **403/429 errors**: Rate limiting
- **Timeouts**: Network issues
- **Missing data**: Incomplete server information
- **API failures**: Fallback to basic data

## Sample Output

### Test Results

```
🧪 Testing Server Enricher V2...
🗄️  Initializing database...
⚡ Processing sample servers...
✅ Processed: Hypixel (mc.hypixel.net) - Online: True
✅ Processed: Wynncraft (play.wynncraft.com) - Online: True
✅ Processed: 2b2t (2b2t.org) - Online: True
✅ Processed: NetherGames (play.nethergames.org) - Online: False
✅ Processed: The Hive (play.hivebedrock.network) - Online: False
💾 Exporting enriched data to JSON...
📱 Exported 5 servers in iOS format
📊 Summary:
   Total servers: 5
   Online servers: 3
   Java servers: 3
   Bedrock servers: 2
✅ Test completed!
```

### Sample Server Data

```json
{
  "name": "Hypixel",
  "ip": "mc.hypixel.net",
  "port": 25565,
  "motd": "Hypixel Network [1.8-1.21]",
  "version": "Requires MC 1.8 / 1.21",
  "online": true,
  "player_count": 30698,
  "max_players": 200000,
  "software": null,
  "icon": "data:image/png;base64,...",
  "tags": ["Java", "Minigames"],
  "category": "minigames",
  "is_bedrock": false,
  "last_updated": "2025-07-28T17:14:34.147158",
  "ping_ms": 424
}
```

## API Integration

### MCSRVSTAT.US Endpoints

- **Java servers**: `https://api.mcsrvstat.us/2/{server_ip}`
- **Bedrock servers**: `https://api.mcsrvstat.us/2/bedrock/{server_ip}`

### Response Fields

- `online`: Server status
- `players.online`: Current player count
- `players.max`: Maximum player capacity
- `version`: Server version
- `motd.clean`: Server description
- `software`: Server software
- `icon`: Server icon (base64)

## Development

### Adding New Server Types

Edit the `determine_server_type()` method:

```python
def determine_server_type(self, server_data: Dict[str, Any]) -> bool:
    # Add new Bedrock indicators
    bedrock_indicators = [
        'bedrock', 'pe', 'pocket', 'mobile', 'win10', 'xbox',
        'hive', 'nethergames', 'galaxite', 'lifeboat',
        'your_new_indicator'  # Add here
    ]
```

### Adding New Categories

Edit the `extract_tags()` method:

```python
def extract_tags(self, server_data: Dict[str, Any]) -> List[str]:
    # Add new category detection
    if any(word in name_lower or word in description for word in ['new_category']):
        tags.append("NewCategory")
```

## Troubleshooting

### Common Issues

1. **404 errors**: Server is offline or IP changed
2. **Rate limiting**: Reduce concurrent requests
3. **Timeout errors**: Check network connection
4. **Missing data**: Server metadata incomplete

### Logs

Check the log file for detailed information:

```bash
tail -f server_enricher_v2.log
```

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- Check the logs for error details
- Review the configuration
- Test with sample data first
- Ensure network connectivity to APIs 