#!/bin/bash

echo "🔧 MySQL Configuration Helper for Docker Connection"
echo ""

# Check if MySQL is running
if brew services list | grep mysql | grep -q started; then
    echo "✅ MySQL service is running"
else
    echo "❌ MySQL service is not running"
    echo "🚀 Starting MySQL service..."
    brew services start mysql
    sleep 3
fi

echo ""
echo "🔍 Checking MySQL configuration..."

# Check if my.cnf exists and what bind-address is set
MYSQL_CONFIG="/opt/homebrew/etc/my.cnf"
if [ -f "$MYSQL_CONFIG" ]; then
    echo "📄 MySQL config file found: $MYSQL_CONFIG"
    if grep -q "bind-address" "$MYSQL_CONFIG"; then
        echo "🔍 Current bind-address setting:"
        grep "bind-address" "$MYSQL_CONFIG"
        echo ""
        echo "💡 For Docker to connect, you may need to:"
        echo "   1. Comment out the bind-address line, or"
        echo "   2. Set bind-address = 0.0.0.0"
    else
        echo "✅ No bind-address restriction found"
    fi
else
    echo "ℹ️  No my.cnf found at $MYSQL_CONFIG"
fi

echo ""
echo "🔑 Setting up MySQL user permissions for Docker access..."

# Grant permissions for root user from any host
mysql -u root -pAneep@2709 -e "
CREATE DATABASE IF NOT EXISTS properties_permit_scrapper;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'Aneep@2709';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY 'Aneep@2709';
FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user WHERE User = 'root';
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ MySQL permissions configured successfully"
else
    echo "❌ Failed to configure MySQL permissions"
    echo "💡 You may need to run this manually:"
    echo "   mysql -u root -p"
    echo "   CREATE DATABASE IF NOT EXISTS properties_permit_scrapper;"
    echo "   GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'Aneep@2709';"
    echo "   FLUSH PRIVILEGES;"
fi

echo ""
echo "🧪 Testing connection..."
./test-mysql-connection.sh