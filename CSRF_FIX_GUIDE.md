# CSRF Fix for Django Production Deployment

## 🐛 **Problem:**
Getting "Forbidden (403) CSRF verification failed. Request aborted." error when accessing the Django application on the server.

## ✅ **Solution Applied:**

### **1. Updated Django Settings (`permit_api/settings.py`):**
Added CSRF trusted origins configuration:
```python
# CSRF Configuration for production deployment
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS', 
    'http://localhost:8800,http://127.0.0.1:8800'
).split(',')
```

### **2. Updated Docker Compose Files:**
Added CSRF trusted origins as environment variables in both `docker-compose.yml` and `docker-compose.ubuntu.yml`:
```yaml
environment:
  - CSRF_TRUSTED_ORIGINS=http://localhost:8800,http://127.0.0.1:8800,http://properties-scrapper.levenstein.net,https://properties-scrapper.levenstein.net
```

### **3. Added Production Security Settings:**
Enhanced security configuration for production:
```python
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000 if os.getenv('USE_HTTPS', 'False') == 'True' else 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

## 🚀 **To Apply the Fix:**

### **On Ubuntu Server:**
```bash
# Stop current containers
docker-compose -f docker-compose.ubuntu.yml down

# Rebuild and restart with new configuration
docker-compose -f docker-compose.ubuntu.yml up --build -d

# Check logs
docker-compose -f docker-compose.ubuntu.yml logs -f web
```

### **For Local Development:**
```bash
# Stop current containers
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## 🔍 **What This Fixes:**

1. **CSRF Token Validation:** Django now trusts requests from your domain
2. **Cross-Origin Requests:** Both HTTP and HTTPS versions of your domain are allowed
3. **Admin Panel Access:** The admin interface will work properly
4. **API Endpoints:** REST API calls will not be blocked by CSRF
5. **Form Submissions:** All form submissions will work correctly

## 🌐 **Trusted Origins Now Include:**
- ✅ `http://localhost:8800` (local development)
- ✅ `http://127.0.0.1:8800` (local development) 
- ✅ `http://properties-scrapper.levenstein.net` (production HTTP)
- ✅ `https://properties-scrapper.levenstein.net` (production HTTPS)

## 🔒 **Security Notes:**

1. **HTTPS Recommended:** Consider setting up SSL/TLS for production
2. **Environment Variables:** CSRF origins are configurable via environment variables
3. **Debug Mode:** Set `DEBUG=False` in production for security
4. **Security Headers:** Additional security headers are enabled in production mode

## 🧪 **Testing:**

After deployment, test these URLs:
- **Admin Login:** `http://properties-scrapper.levenstein.net:8800/admin`
- **API Dashboard:** `http://properties-scrapper.levenstein.net:8800/api/scraper/dashboard/`
- **Scraper Runs:** `http://properties-scrapper.levenstein.net:8800/admin/scraper/scraperrun/`

All forms and CSRF-protected endpoints should now work correctly! 🎉

## ⚡ **Quick Fix Command:**
```bash
# One-liner to fix and restart (Ubuntu)
docker-compose -f docker-compose.ubuntu.yml down && docker-compose -f docker-compose.ubuntu.yml up --build -d
```