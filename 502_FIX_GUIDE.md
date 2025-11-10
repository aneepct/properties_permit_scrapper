# 502 Bad Gateway Fix - Large File Upload Issues

## 🚨 Immediate Actions for 502 Error

Your 502 Bad Gateway error is likely caused by timeout issues when processing large files. Here's the step-by-step fix:

### Step 1: Update Apache Configuration (CRITICAL)

**Replace your current Apache configuration with:**

```bash
sudo nano /etc/apache2/sites-available/properties-scrapper.conf
```

Use the configuration from `apache-production-config.conf` in this repository. Key settings:

```apache
# Critical timeout settings
Timeout 3600                    # 60 minutes
ProxyTimeout 3600              # 60 minutes  
KeepAliveTimeout 3600          # Keep connections alive

# Disable proxy buffering (IMPORTANT!)
SetEnv proxy-nokeepalive 1
SetEnv proxy-sendcl 1
ProxyIOBufferSize 65536

# Large file limit
LimitRequestBody 1610612736    # 1.5GB
```

### Step 2: Update Docker Configuration

**Redeploy with updated settings:**

```bash
# Pull latest changes
git pull origin main

# Rebuild with new configuration
sudo docker-compose down
sudo docker-compose up --build -d

# Or for Ubuntu version:
sudo docker-compose -f docker-compose.ubuntu.yml down
sudo docker-compose -f docker-compose.ubuntu.yml up --build -d
```

**New Docker settings include:**
- Single worker (prevents memory conflicts)
- 60-minute timeout (was 30 minutes)
- Enhanced error logging
- Better memory management

### Step 3: Enable Required Apache Modules

```bash
# Enable all required modules
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod ssl
sudo a2enmod headers
sudo a2enmod expires
sudo a2enmod deflate

# Restart Apache
sudo systemctl restart apache2
```

### Step 4: Create Required Directories

```bash
# On server, in your project directory:
mkdir -p logs temp media/processed

# Set proper permissions
chmod 755 logs temp media
chown -R www-data:www-data logs temp media  # or your web server user
```

### Step 5: Test and Monitor

```bash
# Run the troubleshooting script
chmod +x troubleshoot-502.sh
./troubleshoot-502.sh

# Monitor real-time logs during upload
sudo docker-compose logs -f web &
sudo tail -f /var/log/apache2/error.log &

# Test with a small file first
curl -X POST -F 'zip_file=@small-test.zip' \
  http://localhost:8800/admin/scraper/fileprocessor/process-zip/
```

## 🔧 Configuration Changes Made

### Docker Changes:
- **Workers**: Reduced from 2 to 1 (prevents worker conflicts)
- **Timeout**: Increased to 3600 seconds (60 minutes)
- **Memory**: 4GB limit with 2GB reserved
- **Logging**: Enhanced debug logging enabled
- **Buffering**: Optimized for large file handling

### Apache Changes:
- **Timeout**: 3600 seconds (was likely 300)
- **ProxyTimeout**: 3600 seconds  
- **Buffering**: Disabled proxy buffering
- **Headers**: Added debugging headers
- **SSL**: Production-ready SSL configuration

### Django Changes:
- **Logging**: Comprehensive file and console logging
- **Sessions**: Extended timeout for long uploads
- **Caching**: Added memory caching for better performance
- **Error Handling**: Enhanced error capture and reporting

## 🎯 Root Cause Analysis

The 502 error occurs because:

1. **Apache Default Timeout**: Usually 300 seconds (5 minutes)
2. **Proxy Buffering**: Apache buffers large requests by default
3. **Worker Conflicts**: Multiple Gunicorn workers competing for memory
4. **Memory Pressure**: Large files cause memory spikes

## 📊 Expected Performance After Fix

### Upload Timeouts:
- **Small files (<100MB)**: 2-5 minutes
- **Medium files (100-500MB)**: 5-15 minutes  
- **Large files (500MB-1.5GB)**: 15-45 minutes

### Memory Usage:
- **Per Upload**: ~2-3GB RAM
- **Processing**: Up to 4GB during ZIP extraction
- **Storage**: 3x file size temporary space needed

## 🚨 If Issues Persist

### 1. Check Apache Error Logs:
```bash
sudo tail -f /var/log/apache2/error.log
```

Look for:
- `proxy: error reading status line from remote server`
- `proxy: pass request body failed`
- `Timeout waiting for output from CGI script`

### 2. Check Docker Container:
```bash
# Container status
docker ps

# Container logs
docker logs $(docker ps | grep web | awk '{print $1}')

# Container resources
docker stats --no-stream
```

### 3. Memory Issues:
```bash
# Check memory
free -h

# Check swap
swapon --show

# Add swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 4. Disk Space Issues:
```bash
# Check disk space
df -h

# Clean up if needed
docker system prune -f
sudo rm -rf /tmp/* 2>/dev/null
```

## ✅ Verification Steps

After applying fixes:

1. **Restart services**:
   ```bash
   sudo systemctl restart apache2
   sudo docker-compose restart
   ```

2. **Test small upload** (< 10MB) first

3. **Test medium upload** (100-200MB)

4. **Monitor logs** during upload:
   ```bash
   # Terminal 1: Apache logs
   sudo tail -f /var/log/apache2/error.log
   
   # Terminal 2: Docker logs  
   sudo docker-compose logs -f web
   
   # Terminal 3: System resources
   watch -n 1 'free -h && echo && docker stats --no-stream'
   ```

5. **Test large upload** (500MB+) only after smaller tests pass

## 🔄 Recovery Commands

If something goes wrong:

```bash
# Quick restart everything
sudo systemctl restart apache2
sudo docker-compose restart

# Full rebuild
sudo docker-compose down
sudo docker-compose up --build -d

# Reset to working state
git checkout main
git pull origin main
sudo docker-compose up --build -d
```

This configuration should resolve your 502 Bad Gateway errors for large file uploads!