#!/bin/bash

# Ubuntu Server Deployment Script for Django Permit Scraper

echo "🐧 Ubuntu Server Deployment - Django Permit Scraper"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    
    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed successfully"
    echo "⚠️  Please log out and back in to use Docker without sudo"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing..."
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker Compose installed successfully"
fi

echo ""
echo "🔍 Checking MySQL connectivity options..."

# Option 1: Try connecting to host MySQL
if mysqladmin ping -h localhost -u root -pDevneep@27092023 &>/dev/null; then
    echo "✅ Host MySQL is accessible - using host network mode"
    COMPOSE_FILE="docker-compose.yml"
else
    echo "⚠️  Host MySQL not accessible - using containerized MySQL"
    COMPOSE_FILE="docker-compose.ubuntu.yml"
fi

echo ""
echo "📦 Using compose file: $COMPOSE_FILE"
echo "🚀 Building and starting services..."

# Stop any existing containers
docker-compose -f $COMPOSE_FILE down 2>/dev/null

# Build and start services
docker-compose -f $COMPOSE_FILE up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if web service is running
if docker-compose -f $COMPOSE_FILE ps | grep -q "web.*Up"; then
    echo "✅ Web service is running"
else
    echo "❌ Web service failed to start. Checking logs..."
    docker-compose -f $COMPOSE_FILE logs web
    exit 1
fi

echo ""
echo "🎉 Django Permit Scraper is now running on Ubuntu!"
echo ""
echo "📍 Access your application at:"
echo "   🌐 Web Application: http://localhost:8800"
echo "   🌐 Web Application (External): http://$(hostname -I | awk '{print $1}'):8800"
echo "   🛡️  Admin Panel: http://localhost:8800/admin"
echo "   📊 API Dashboard: http://localhost:8800/api/scraper/dashboard/"
echo ""
echo "🔑 Admin Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "   Stop services: docker-compose -f $COMPOSE_FILE down"
echo "   Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "   Shell access: docker-compose -f $COMPOSE_FILE exec web bash"
echo ""
echo "🔥 If you need to open firewall port 8800:"
echo "   sudo ufw allow 8800"
echo ""