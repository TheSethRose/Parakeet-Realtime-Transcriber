# Database Setup Guide

## Quick Start

### 1. Start Database
```bash
# Start PostgreSQL in background
docker-compose up -d

# View logs
docker-compose logs -f postgres
```

### 2. Test Connection
```bash
# Test database connectivity
python database.py
```

### 3. Use Database Management Script
```bash
# View all available commands
python db_manager.py --help

# Test connection
python db_manager.py --test

# View recent recordings
python db_manager.py --recent

# Get specific recording
python db_manager.py --get "WWDC25 on Youtube"

# Get recording statistics  
python db_manager.py --stats
```

## Database Operations

### Connect Directly
```bash
# Connect to database directly
docker-compose exec postgres psql -U transcription_user -d transcription_db
```

### View Data
```sql
-- View all recordings
SELECT * FROM recordings_formatted ORDER BY created_at DESC LIMIT 10;

-- Get recording statistics
SELECT recording_name, COUNT(*) as segments, 
       MIN(created_at) as started, MAX(created_at) as finished
FROM recordings 
GROUP BY recording_name 
ORDER BY started DESC;
```

## Environment Variables

The database uses these environment variables from your `.env` file:

- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5433` (non-standard port for security)
- `POSTGRES_DB=transcription_db`
- `POSTGRES_USER=transcription_user_xyz123` (randomized)
- `POSTGRES_PASSWORD=SecurePass789!AbC` (randomized)

## Troubleshooting

### Connection Issues
```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart postgres

# View database logs
docker-compose logs postgres
```

### Reset Database
```bash
# Stop and remove containers with data
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Port Conflicts
If port 5433 is already in use, edit `docker-compose.yml` and `.env` files to use a different port.

## Security Notes

- Uses non-standard port (5433) instead of default PostgreSQL port (5432)
- Randomized username and password
- Database only accessible from localhost
- Environment variables kept in `.env` (not committed to git)
