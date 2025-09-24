#!/bin/bash

# Build and run the Django permit scraper with Docker

echo "🐳 Starting Django Permit Scraper with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec web python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating admin user..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('✅ Admin user already exists')
"

# Show status
echo ""
echo "🎉 Django Permit Scraper is now running!"
echo ""
echo "📍 Access your application at:"
echo "   🌐 Web Application: http://localhost:8000"
echo "   🛡️  Admin Panel: http://localhost:8000/admin"
echo "   📊 API Dashboard: http://localhost:8000/api/scraper/dashboard/"
echo ""
echo "🔑 Admin Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo ""