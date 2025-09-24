#!/bin/bash

# Simple Docker run script using host network and host MySQL

echo "🐳 Building Django Permit Scraper Docker image..."

# Build the Docker image
docker build -t permit-scraper .

echo "🚀 Running Django Permit Scraper with host network..."

# Run the container with port mapping
docker run -d \
  --name permit-scraper-app \
  -p 8000:8000 \
  -e DEBUG=False \
  -e DATABASE_NAME=properties_permit_scrapper \
  -e DATABASE_USER=root \
  -e DATABASE_PASSWORD=Aneep@2709 \
  -e DATABASE_HOST=host.docker.internal \
  -e DATABASE_PORT=3306 \
  -e ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/state:/app/state" \
  -v "$(pwd)/staticfiles:/app/staticfiles" \
  permit-scraper

echo "⏳ Waiting for container to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
docker exec permit-scraper-app python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating admin user..."
docker exec permit-scraper-app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('✅ Admin user already exists')
"

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
echo "   View logs: docker logs -f permit-scraper-app"
echo "   Stop container: docker stop permit-scraper-app"
echo "   Remove container: docker rm permit-scraper-app"
echo "   Shell access: docker exec -it permit-scraper-app bash"
echo ""