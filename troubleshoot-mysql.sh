#!/bin/bash

# MySQL Connectivity Troubleshooting for Ubuntu Server

echo "🔧 MySQL Connectivity Troubleshooting for Ubuntu Server"
echo "======================================================"

echo ""
echo "1️⃣  Checking if MySQL is installed and running..."

# Check if MySQL is installed
if command -v mysql &> /dev/null; then
    echo "✅ MySQL client is installed"
else
    echo "❌ MySQL client not found. Install with: sudo apt-get install mysql-client"
fi

# Check if MySQL server is running
if systemctl is-active --quiet mysql; then
    echo "✅ MySQL service is running"
elif systemctl is-active --quiet mysqld; then
    echo "✅ MySQL service is running (mysqld)"
else
    echo "❌ MySQL service is not running"
    echo "💡 Start with: sudo systemctl start mysql"
    echo "💡 Enable auto-start: sudo systemctl enable mysql"
fi

echo ""
echo "2️⃣  Testing MySQL connectivity..."

# Test local connection
if mysql -u root -pDevneep@27092023 -e "SELECT 1;" &>/dev/null; then
    echo "✅ Can connect to MySQL as root"
    
    # Check if database exists
    if mysql -u root -pDevneep@27092023 -e "USE properties_permit_scrapper; SELECT 1;" &>/dev/null; then
        echo "✅ Database 'properties_permit_scrapper' exists"
    else
        echo "⚠️  Database 'properties_permit_scrapper' does not exist"
        echo "📝 Creating database..."
        mysql -u root -pDevneep@27092023 -e "CREATE DATABASE IF NOT EXISTS properties_permit_scrapper;"
        if [ $? -eq 0 ]; then
            echo "✅ Database created successfully"
        else
            echo "❌ Failed to create database"
        fi
    fi
else
    echo "❌ Cannot connect to MySQL as root"
    echo "💡 Possible solutions:"
    echo "   - Check password: mysql -u root -p"
    echo "   - Reset password: sudo mysql_secure_installation"
    echo "   - Check if MySQL is running: sudo systemctl status mysql"
fi

echo ""
echo "3️⃣  Checking MySQL configuration for Docker access..."

# Check bind address
MYSQL_CONFIG="/etc/mysql/mysql.conf.d/mysqld.cnf"
if [ -f "$MYSQL_CONFIG" ]; then
    echo "📄 Checking MySQL config: $MYSQL_CONFIG"
    
    if grep -q "^bind-address" "$MYSQL_CONFIG"; then
        BIND_ADDRESS=$(grep "^bind-address" "$MYSQL_CONFIG" | cut -d'=' -f2 | tr -d ' ')
        echo "🔍 Current bind-address: $BIND_ADDRESS"
        
        if [ "$BIND_ADDRESS" = "127.0.0.1" ]; then
            echo "⚠️  MySQL is only listening on localhost"
            echo "💡 To allow Docker access, modify $MYSQL_CONFIG:"
            echo "   sudo nano $MYSQL_CONFIG"
            echo "   Change: bind-address = 127.0.0.1"
            echo "   To:     bind-address = 0.0.0.0"
            echo "   Then restart: sudo systemctl restart mysql"
        elif [ "$BIND_ADDRESS" = "0.0.0.0" ]; then
            echo "✅ MySQL is configured to accept external connections"
        fi
    else
        echo "ℹ️  No bind-address restriction found (good for Docker)"
    fi
else
    echo "⚠️  MySQL config file not found at $MYSQL_CONFIG"
fi

echo ""
echo "4️⃣  Network connectivity test..."

# Test if port 3306 is open
if netstat -tlnp 2>/dev/null | grep -q ":3306 "; then
    echo "✅ MySQL port 3306 is listening"
    netstat -tlnp 2>/dev/null | grep ":3306 "
else
    echo "❌ MySQL port 3306 is not listening"
    echo "💡 Check if MySQL is running and configured correctly"
fi

echo ""
echo "5️⃣  Docker network test..."

# Test Docker to host connectivity
echo "🧪 Testing Docker container MySQL connectivity..."
docker run --rm mysql:8.0 mysql -h 172.17.0.1 -P 3306 -u root -pDevneep@27092023 -e "SELECT 'Docker connection successful!' as status;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Docker can connect to host MySQL"
else
    echo "❌ Docker cannot connect to host MySQL"
    echo "💡 Try using containerized MySQL instead:"
    echo "   docker-compose -f docker-compose.ubuntu.yml up -d"
fi

echo ""
echo "📋 Summary of deployment options:"
echo ""
echo "🐳 Option 1: Use host MySQL (current docker-compose.yml)"
echo "   - Requires MySQL running on host"
echo "   - Uses host network mode"
echo "   - Access: http://localhost:8800"
echo ""
echo "🐳 Option 2: Use containerized MySQL (docker-compose.ubuntu.yml)"
echo "   - Includes MySQL container"
echo "   - Self-contained solution"
echo "   - Access: http://localhost:8800"
echo ""
echo "🚀 Deploy with:"
echo "   ./deploy-ubuntu.sh (auto-detects best option)"
echo "   OR"
echo "   docker-compose -f docker-compose.ubuntu.yml up -d (force containerized MySQL)"
echo ""