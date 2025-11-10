#!/bin/bash
# Server Troubleshooting Script for Large Upload 502 Errors
# Run this script on your server to diagnose and fix 502 Bad Gateway issues

echo "=== Properties Scraper - Large Upload Troubleshooting Script ==="
echo "Checking server configuration for 502 Bad Gateway issues..."
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system resources
echo "1. SYSTEM RESOURCES:"
echo "   Memory Usage:"
free -h
echo ""
echo "   Disk Space:"
df -h
echo ""
echo "   Load Average:"
uptime
echo ""

# Check Docker status
echo "2. DOCKER STATUS:"
if command_exists docker; then
    echo "   Docker service status:"
    sudo systemctl status docker --no-pager -l
    echo ""
    
    echo "   Running containers:"
    docker ps
    echo ""
    
    echo "   Container resource usage:"
    docker stats --no-stream
    echo ""
    
    # Check specific container logs
    CONTAINER_NAME=$(docker ps --format "table {{.Names}}" | grep -E "(web|app|django)" | head -1)
    if [ ! -z "$CONTAINER_NAME" ]; then
        echo "   Recent logs from container: $CONTAINER_NAME"
        docker logs --tail=50 $CONTAINER_NAME
        echo ""
    fi
else
    echo "   Docker not found!"
fi

# Check Apache status and configuration
echo "3. APACHE STATUS:"
if command_exists apache2; then
    echo "   Apache service status:"
    sudo systemctl status apache2 --no-pager -l
    echo ""
    
    echo "   Apache error logs (last 20 lines):"
    sudo tail -20 /var/log/apache2/error.log 2>/dev/null || echo "   Error log not found"
    echo ""
    
    echo "   Apache access logs (last 10 lines):"
    sudo tail -10 /var/log/apache2/access.log 2>/dev/null || echo "   Access log not found"
    echo ""
    
    echo "   Apache configuration test:"
    sudo apache2ctl configtest
    echo ""
    
    echo "   Enabled modules:"
    sudo apache2ctl -M | grep -E "(proxy|ssl|headers|rewrite)"
    echo ""
    
    echo "   Virtual hosts:"
    sudo apache2ctl -S
    echo ""
else
    echo "   Apache not found!"
fi

# Check if application is responding locally
echo "4. APPLICATION CONNECTIVITY:"
echo "   Testing local Django application on port 8800:"
if command_exists curl; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8800/admin/ --connect-timeout 10)
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
        echo "   ✓ Django app responding (HTTP $HTTP_STATUS)"
    else
        echo "   ✗ Django app not responding (HTTP $HTTP_STATUS)"
        
        # Check if port 8800 is open
        if command_exists netstat; then
            echo "   Port 8800 status:"
            sudo netstat -tlnp | grep :8800
        fi
    fi
else
    echo "   curl not available for testing"
fi
echo ""

# Check file permissions and directories
echo "5. FILE PERMISSIONS:"
PROJECT_DIR="/home/ubuntu/properties_permit_scrapper"  # Adjust this path
if [ -d "$PROJECT_DIR" ]; then
    echo "   Project directory: $PROJECT_DIR"
    ls -la $PROJECT_DIR/
    echo ""
    
    # Check temp directory
    if [ -d "$PROJECT_DIR/temp" ]; then
        echo "   Temp directory permissions:"
        ls -la $PROJECT_DIR/temp/
    else
        echo "   ✗ Temp directory missing! Creating..."
        mkdir -p $PROJECT_DIR/temp
        chmod 755 $PROJECT_DIR/temp
    fi
    echo ""
    
    # Check logs directory
    if [ -d "$PROJECT_DIR/logs" ]; then
        echo "   Logs directory:"
        ls -la $PROJECT_DIR/logs/
        echo ""
        
        # Show recent Django logs
        if [ -f "$PROJECT_DIR/logs/django.log" ]; then
            echo "   Recent Django logs:"
            tail -20 $PROJECT_DIR/logs/django.log
        fi
        echo ""
        
        if [ -f "$PROJECT_DIR/logs/uploads.log" ]; then
            echo "   Recent upload logs:"
            tail -20 $PROJECT_DIR/logs/uploads.log
        fi
    else
        echo "   ✗ Logs directory missing! Creating..."
        mkdir -p $PROJECT_DIR/logs
        chmod 755 $PROJECT_DIR/logs
    fi
else
    echo "   ✗ Project directory not found at $PROJECT_DIR"
    echo "   Please update the PROJECT_DIR variable in this script"
fi
echo ""

# Check system limits
echo "6. SYSTEM LIMITS:"
echo "   File descriptor limits:"
ulimit -n
echo ""
echo "   Memory limits:"
ulimit -v
echo ""
echo "   Process limits:"
ulimit -u
echo ""

# Provide recommendations
echo "7. RECOMMENDATIONS:"
echo ""

# Check Apache timeout configuration
APACHE_CONF="/etc/apache2/sites-available/properties-scrapper.conf"
if [ -f "$APACHE_CONF" ]; then
    TIMEOUT_SET=$(grep -i "Timeout 3600" $APACHE_CONF)
    if [ -z "$TIMEOUT_SET" ]; then
        echo "   ⚠️  Apache timeout not set to 3600 seconds"
        echo "      Add 'Timeout 3600' to your Apache configuration"
    else
        echo "   ✓ Apache timeout properly configured"
    fi
    
    PROXY_TIMEOUT=$(grep -i "ProxyTimeout 3600" $APACHE_CONF)
    if [ -z "$PROXY_TIMEOUT" ]; then
        echo "   ⚠️  Apache ProxyTimeout not set to 3600 seconds"
        echo "      Add 'ProxyTimeout 3600' to your Apache configuration"
    else
        echo "   ✓ Apache ProxyTimeout properly configured"
    fi
else
    echo "   ⚠️  Apache configuration not found at $APACHE_CONF"
    echo "      Please ensure you've installed the updated configuration"
fi

# Memory recommendations
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%d", $2}')
if [ "$TOTAL_MEM" -lt 8192 ]; then
    echo "   ⚠️  Server has ${TOTAL_MEM}MB RAM, recommend 8GB+ for large file processing"
fi

# Disk space recommendations
TEMP_SPACE=$(df /tmp | awk 'NR==2{print $4}')
if [ "$TEMP_SPACE" -lt 5242880 ]; then  # 5GB in KB
    echo "   ⚠️  Low disk space in /tmp (${TEMP_SPACE}KB), need 5GB+ for large files"
fi

echo ""
echo "8. QUICK FIXES:"
echo "   To restart services:"
echo "   sudo systemctl restart apache2"
echo "   sudo docker-compose down && sudo docker-compose up -d --build"
echo ""
echo "   To view real-time logs:"
echo "   sudo docker-compose logs -f web"
echo "   sudo tail -f /var/log/apache2/error.log"
echo ""
echo "   To test upload manually:"
echo "   curl -X POST -F 'zip_file=@test.zip' http://localhost:8800/admin/scraper/fileprocessor/process-zip/"
echo ""
echo "=== End of troubleshooting report ==="