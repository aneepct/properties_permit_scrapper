#!/bin/bash

echo "🔍 Testing MySQL connection from Docker container..."

# Test connection using a simple MySQL client container
docker run --rm -it mysql:8.0 mysql \
  -h host.docker.internal \
  -P 3306 \
  -u root \
  -pAneep@2709 \
  -e "SELECT 'Connection successful!' as status; SHOW DATABASES;" \
  properties_permit_scrapper

echo ""
echo "If the connection failed, you might need to:"
echo "1. Check if MySQL is running: brew services list | grep mysql"
echo "2. Start MySQL if needed: brew services start mysql"
echo "3. Check MySQL bind address in /opt/homebrew/etc/my.cnf (should allow 0.0.0.0 or comment out bind-address)"
echo "4. Grant permissions: mysql -u root -p -e \"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'Aneep@2709'; FLUSH PRIVILEGES;\""
echo ""