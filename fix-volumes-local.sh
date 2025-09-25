#!/bin/bash

# Fix Docker volumes permissions for local development

echo "🔧 Docker Volumes Permission Fix for Local Development"
echo "===================================================="

echo ""
echo "1️⃣  Stopping existing containers..."
docker-compose down

echo ""
echo "2️⃣  Creating local directories with proper permissions..."
mkdir -p logs output state
chmod 755 logs output state
chown -R $USER:$USER logs output state

echo ""
echo "3️⃣  Rebuilding and starting services..."
docker-compose up --build -d

echo ""
echo "4️⃣  Checking container status..."
sleep 10
docker-compose ps

echo ""
echo "5️⃣  Checking logs for any errors..."
echo "Web service logs:"
docker-compose logs --tail=20 web

echo ""
echo "✅ Volume permissions have been fixed for local development!"
echo ""
echo "📋 If you still see issues:"
echo "   Check logs: docker-compose logs -f web"
echo "   Access shell: docker-compose exec web bash"
echo "   Check volumes: docker volume ls"

echo ""
echo "🌐 Access your application at:"
echo "   Web App: http://localhost:8800"
echo "   Admin Panel: http://localhost:8800/admin"
echo "   API Dashboard: http://localhost:8800/api/scraper/dashboard/"
echo ""
echo "🔑 Admin credentials: admin / admin123"