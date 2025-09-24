# Property Permit Scraper Django API

## Overview
This Django-based REST API system integrates with the existing permit scraper (`MAIN_permit_scraper.py`) and automatically saves scraped data to a MySQL database. The system provides a complete web API for running the scraper and accessing permit data.

## System Architecture

### Components
1. **Django Web Framework** - REST API server
2. **MySQL Database** - Data storage with proper indexing
3. **Django REST Framework** - API endpoints
4. **Django Admin** - Web-based data management
5. **Original Scraper Integration** - Reuses existing scraper logic

### Database Tables
- `permits` - Main permit records with full data model
- `scraper_runs` - Execution history and run tracking
- Standard Django tables (auth, admin, etc.)

## API Endpoints

### Core Endpoints
- `GET /api/` - API information and available endpoints
- `GET /api/scraper/dashboard/` - Dashboard statistics
- `POST /api/scraper/start/` - Execute the permit scraper
- `GET /api/scraper/permits/` - List permits (paginated)
- `GET /api/scraper/permits/{id}/` - Get specific permit
- `GET /api/scraper/runs/` - List scraper execution runs
- `GET /api/scraper/runs/{id}/` - Get specific run details
- `GET /admin/` - Django admin interface

### API Usage Examples

#### 1. Start Scraper (Execute MAIN_permit_scraper.py)
```bash
curl -X POST http://localhost:8000/api/scraper/start/ \
  -H "Content-Type: application/json" \
  -d '{"cities": [], "force_rescrape": false}'
```

Response:
```json
{
  "run_id": "run_3a49835d_20250924_054220",
  "status": "completed",
  "duration_seconds": 0.048968,
  "total_permits_found": 27,
  "total_project_value": "668003306",
  "cities_processed": ["nyc", "chicago", "la", "sf"],
  "city_summaries": [
    "SUCCESS New York City: 4 permits ($100,730,737)",
    "SUCCESS Chicago: 8 permits ($209,212,936)",
    "SUCCESS Los Angeles: 8 permits ($184,412,534)",
    "SUCCESS San Francisco: 7 permits ($173,647,099)"
  ],
  "errors": [],
  "message": "Scraper completed successfully! Found 27 permits worth $668,003,306"
}
```

#### 2. Get Dashboard Statistics
```bash
curl http://localhost:8000/api/scraper/dashboard/
```

Response:
```json
{
  "total_permits": 29,
  "total_value": "697505820.00",
  "city_stats": [
    {"city": "New York City", "permit_count": 6, "total_value": "130233251.00"},
    {"city": "Chicago", "permit_count": 8, "total_value": "209212936.00"},
    {"city": "Los Angeles", "permit_count": 8, "total_value": "184412534.00"},
    {"city": "San Francisco", "permit_count": 7, "total_value": "173647099.00"}
  ],
  "recent_runs": [...]
}
```

#### 3. List Permits with Filtering
```bash
# Get recent permits
curl "http://localhost:8000/api/scraper/permits/?page_size=5"

# Filter by city
curl "http://localhost:8000/api/scraper/permits/?city=Chicago&page_size=10"

# Filter by date range and cost
curl "http://localhost:8000/api/scraper/permits/?start_date=2025-09-01&min_cost=1000000"

# Search in descriptions
curl "http://localhost:8000/api/scraper/permits/?search=residential"
```

## Configuration

### Environment Variables (.env)
```env
DB_NAME=properties_permit_scrapper
DB_USER=root
DB_PASSWORD=Aneep@2709
DB_HOST=127.0.0.1
DB_PORT=3306
DEBUG=True
SECRET_KEY=django-insecure-permit-scraper-dev-key-2025
```

### MySQL Database
- **Database**: `properties_permit_scrapper`
- **Host**: `127.0.0.1:3306`
- **User**: `root`
- **Password**: `Aneep@2709`

## Installation & Setup

### 1. Install Dependencies
```bash
pip install django django-cors-headers djangorestframework mysqlclient python-dotenv pandas requests
```

### 2. Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations (creates tables)
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser
```

### 3. Start Server
```bash
python manage.py runserver 8000
```

The server will be available at `http://localhost:8000/`

## Data Model

### Permit Model
```python
class Permit(models.Model):
    # Identification
    city = models.CharField(max_length=100)
    permit_id = models.CharField(max_length=50, unique=True)
    
    # Dates
    issue_date = models.DateField()
    scraped_at = models.DateTimeField()
    
    # Location
    full_address = models.CharField(max_length=500)
    borough_area = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    # Project Details
    project_description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Parties Involved
    contractor_name = models.CharField(max_length=200)
    applicant_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    architect_name = models.CharField(max_length=200)
    
    # Contact & Status
    license_status = models.CharField(max_length=50)
    business_address = models.CharField(max_length=500)
    business_phone = models.CharField(max_length=20)
    
    # Metadata
    data_source = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Integration Features

### 1. Seamless Scraper Integration
- Directly imports and executes `MAIN_permit_scraper.py`
- Preserves all original scraper functionality
- Automatically saves results to MySQL database
- Tracks execution history and performance

### 2. Data Management
- **Duplicate Prevention**: Uses `permit_id` as unique key
- **Data Updates**: Existing permits are updated, not duplicated
- **Indexing**: Optimized database indexes for fast queries
- **Admin Interface**: Full CRUD operations via Django admin

### 3. API Features
- **Pagination**: Large datasets handled efficiently
- **Filtering**: By city, date range, cost, search terms
- **Real-time Stats**: Dashboard with live statistics
- **Run Tracking**: Complete audit trail of scraper executions

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/`
- **Username**: `admin`
- **Password**: `admin123`

### Admin Features
- View and edit all permits
- Filter by city, date, cost
- Search permits by address, description, contractor
- View scraper run history
- Export data capabilities

## Testing

### Automated Test
```bash
python simple_test.py
```

### Manual Testing
```bash
# Test API root
curl http://localhost:8000/api/

# Run scraper
curl -X POST http://localhost:8000/api/scraper/start/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Check results  
curl http://localhost:8000/api/scraper/dashboard/
```

## File Structure
```
properties_permit_scrapper/
├── manage.py                    # Django management
├── permit_api/                  # Django project
│   ├── settings.py             # Configuration
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI application
├── scraper/                    # Django app
│   ├── models.py               # Database models
│   ├── views.py                # API endpoints
│   ├── serializers.py          # API serializers
│   ├── urls.py                 # App URL routing
│   └── admin.py                # Admin interface
├── MAIN_permit_scraper.py      # Original scraper (integrated)
├── .env                        # Environment configuration
├── test_api.py                 # Full API test client
└── simple_test.py              # Quick API test
```

## Production Deployment Notes

### Security
- Change `SECRET_KEY` in production
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use environment variables for all secrets

### Database
- Use connection pooling for high traffic
- Set up regular backups
- Monitor query performance
- Consider read replicas for scaling

### Server
- Use Gunicorn or uWSGI for production
- Set up Nginx for static files and reverse proxy
- Configure SSL/HTTPS
- Set up monitoring and logging

## Success Summary

✅ **Django API Successfully Configured**
✅ **MySQL Integration Working**
✅ **Original Scraper Fully Integrated**
✅ **Data Saving to Database**
✅ **REST API Endpoints Functional**
✅ **Admin Interface Available**
✅ **Comprehensive Testing Completed**

The system is now fully operational and ready for use. You can execute the permit scraper via API calls and all data is automatically saved to your MySQL database as requested.