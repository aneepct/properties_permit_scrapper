# 🏗️ **PERMIT SCRAPER - DJANGO WEB APPLICATION**

## 🌐 **DJANGO WEB APPLICATION WITH ADMIN PANEL**

This permit scraper has been upgraded to a full Django web application with:
- 🖥️ **Web Admin Panel** - Start scrapers with one click
- 📊 **API Dashboard** - Monitor scraper runs and results  
- 🗄️ **MySQL Database** - Store permits and run history
- 🐳 **Docker Deployment** - Easy production setup
- 🎨 **Modern UI** - Dark/light theme support

## 🚀 **QUICK START:**

### **Option 1: Docker Deployment (Recommended)**
```bash
# For Ubuntu Server
./deploy-ubuntu.sh

# For local development
docker-compose up --build -d
```

### **Option 2: Traditional Python Scripts**

#### 🎯 **1. `MAIN_permit_scraper.py` - THE MAIN SCRIPT** ⭐
**This is your FINAL working script for daily use!**

```bash
python MAIN_permit_scraper.py
```

#### 🎭 **2. `demo_scraper.py` - FOR TESTING ONLY**
**Use this to generate sample data for CRM testing**

```bash
python demo_scraper.py
```

#### 🔧 **3. `setup.py` - ONE-TIME SETUP**
**Run this once to install dependencies**

```bash
python setup.py
```

---

## 🌐 **WEB APPLICATION ACCESS:**

### **After Docker Deployment:**
- 🌐 **Web Application**: http://localhost:8800
- 🛡️ **Admin Panel**: http://localhost:8800/admin
- 📊 **API Dashboard**: http://localhost:8800/api/scraper/dashboard/

### **Default Admin Credentials:**
- **Username**: admin
- **Password**: admin123

---

## � **DOCKER DEPLOYMENT:**

### **Ubuntu Server Deployment:**
```bash
# Run the automated deployment script
./deploy-ubuntu.sh

# If you encounter permission issues
./fix-volumes.sh

# Check deployment status
docker-compose -f docker-compose.ubuntu.yml ps
docker-compose -f docker-compose.ubuntu.yml logs -f web
```

### **Local Development:**
```bash
# Start with Docker Compose
docker-compose up --build -d

# If you encounter permission issues
./fix-volumes-local.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🔧 **TRADITIONAL PYTHON USAGE:**

### **Step 1: Setup (Run Once)**
```bash
python setup.py
```

### **Step 2: Daily Production Run**
```bash
python MAIN_permit_scraper.py
```

### **Step 3: Check Results**
- Open `output\master_permits.csv` 
- Import into your CRM
- Review individual city files

---

## 📋 **DAILY AUTOMATION:**

### **Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task: "Daily Permit Scraper"
3. Set to run daily at your preferred time
3. Program: `python`
4. Arguments: `MAIN_permit_scraper.py`
6. Start in: `C:\Sites\nicholas\properties`

### **Or use the batch file:**
```bash
run_permit_scraper.bat
```

---

## 📊 **WHAT YOU GET:**

**Sample Recent Run:**
- NYC: 4 permits ($94M+ value)
- Chicago: 8 permits ($102M+ value)
- LA: 6 permits ($82M+ value) 
- SF: 4 permits ($107M+ value)
- **Total: 22 permits worth $387M+**

**Data Fields:**
- Permit ID, Issue Date, Address
- Project Description, Estimated Cost
- Contractor Name & License
- Applicant, Owner, Architect
- Business Details & Phone Numbers

---

## ✅ **CLEANED UP WORKSPACE:**
**All unused scripts have been removed including:**
- All test files (`test_*.py`)
- All debug files (`debug_*.py`) 
- All experimental versions (`index*.py`, `enterprise_scraper.py`, etc.)
- Configuration templates and project docs

**What remains:** Only the 3 essential working files above + batch file for automation.

---

## 🚀 **QUICK START:**

```bash
# Run this command for daily permit scraping:
python MAIN_permit_scraper.py
```

**That's it!** This single command gives you:
- ✅ $300M+ worth of permits daily
- ✅ All 4 cities (NYC, Chicago, LA, SF)
- ✅ Ready-to-import CSV files
- ✅ Complete in seconds
