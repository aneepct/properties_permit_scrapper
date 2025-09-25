#!/bin/bash

# Fix Docker volumes permissions for Ubuntu deployment

echo "🔧 Docker Volumes Permission Fix for Ubuntu"
echo "=========================================="

echo ""
echo "1️⃣  Stopping existing containers..."
docker-compose -f docker-compose.ubuntu.yml down

echo ""
echo "2️⃣  Removing existing volumes (this will preserve data)..."
# Note: We're not removing volumes as they contain valuable data
# docker volume rm properties_permit_scrapper_static_volume 2>/dev/null || true
# docker volume rm properties_permit_scrapper_media_volume 2>/dev/null || true

echo ""
echo "3️⃣  Creating local directories with proper permissions..."
mkdir -p logs output state
chmod 755 logs output state
chown -R $USER:$USER logs output state

echo ""
echo "4️⃣  Rebuilding and starting services..."
docker-compose -f docker-compose.ubuntu.yml up --build -d

echo ""
echo "5️⃣  Checking container status..."
sleep 10
docker-compose -f docker-compose.ubuntu.yml ps

echo ""
echo "6️⃣  Checking logs for any errors..."
echo "Web service logs:"
docker-compose -f docker-compose.ubuntu.yml logs --tail=20 web

echo ""
echo "MySQL service logs:"
docker-compose -f docker-compose.ubuntu.yml logs --tail=10 db

echo ""
echo "✅ Volume permissions have been fixed!"
echo ""
echo "📋 If you still see issues:"
echo "   Check logs: docker-compose -f docker-compose.ubuntu.yml logs -f web"
echo "   Access shell: docker-compose -f docker-compose.ubuntu.yml exec web bash"
echo "   Check volumes: docker volume ls"