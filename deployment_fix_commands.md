# Fix Docker Deployment - Missing Requests Module

## The Problem
The Docker container is missing the `requests` module because it was added to the code but not to requirements.txt when we integrated real API functionality.

## Solution Steps

### 1. Update your server with latest code
```bash
# On your Ubuntu server
cd /path/to/your/project
git pull origin main
```

### 2. Stop current containers
```bash
docker-compose -f docker-compose.ubuntu.yml down
```

### 3. Rebuild the Docker image (this will install requests)
```bash
# Force rebuild to get new requirements.txt
docker-compose -f docker-compose.ubuntu.yml build --no-cache
```

### 4. Start containers with new image
```bash
docker-compose -f docker-compose.ubuntu.yml up -d
```

### 5. Check logs to verify it's working
```bash
# Check Django logs
docker-compose -f docker-compose.ubuntu.yml logs web

# Check if requests module is available
docker-compose -f docker-compose.ubuntu.yml exec web python -c "import requests; print('requests module OK')"
```

## Alternative Quick Fix (if you can't rebuild immediately)
If you need a quick fix without rebuilding, you can install requests directly in the running container:

```bash
# Install requests in running container (temporary fix)
docker-compose -f docker-compose.ubuntu.yml exec web pip install requests==2.31.0

# Restart the web service
docker-compose -f docker-compose.ubuntu.yml restart web
```

**Note:** The alternative fix is temporary - you'll still need to rebuild the image eventually with the updated requirements.txt for a permanent fix.

## Updated Requirements.txt
The requirements.txt has been updated to include:
- requests==2.31.0 (for API calls to city permit data)
- pandas==2.2.3 (already was there, for data processing)

## Test After Fix
After deployment, test that the real permit data is working:
1. Visit your Django admin panel
2. Try the scraper API endpoint
3. Check that contractor names and real permit data appear correctly