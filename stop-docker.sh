#!/bin/bash

# Stop and clean up Docker containers

echo "🛑 Stopping Django Permit Scraper..."

# Stop and remove the single container
if docker ps -q -f name=permit-scraper-app | grep -q .; then
    echo "Stopping permit-scraper-app container..."
    docker stop permit-scraper-app
    docker rm permit-scraper-app
    echo "✅ Container stopped and removed"
else
    echo "ℹ️  No running container found"
fi

# Also handle docker-compose if used
if docker-compose ps -q | grep -q .; then
    echo "Stopping docker-compose services..."
    docker-compose down
    echo "✅ Docker-compose services stopped"
fi

echo ""
echo "🧹 Cleanup completed!"
echo ""
echo "📋 To restart:"
echo "   Using simple container: ./run-docker.sh"
echo "   Using docker-compose: ./start-docker.sh"
echo ""