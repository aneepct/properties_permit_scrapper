#!/usr/bin/env python3
"""
Installation and Setup Script for Enterprise Permit Scraper
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required Python packages"""
    requirements = [
        "requests>=2.28.0",
        "pandas>=1.5.0", 
        "python-dateutil>=2.8.0",
        "python-dotenv>=0.19.0",
        "airtable-python-wrapper>=0.15.0",
        "schedule>=1.1.0"
    ]
    
    print("Installing required packages...")
    for req in requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    print("✅ All packages installed successfully")

def create_directories():
    """Create required directory structure"""
    directories = [
        "output", 
        "state", 
        "logs", 
        "license_data"
    ]
    
    print("Creating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}/")
    print("✅ Directory structure ready")

def setup_task_scheduler():
    """Instructions for Windows Task Scheduler setup"""
    print("\n🔧 WINDOWS TASK SCHEDULER SETUP")
    print("="*50)
    print("1. Open Task Scheduler (taskschd.msc)")
    print("2. Click 'Create Basic Task'")
    print("3. Name: 'Daily Permit Scraper'")
    print("4. Trigger: Daily at your preferred time")
    print(f"5. Action: Start program")
    print(f"   Program: {os.path.abspath('run_permit_scraper.bat')}")
    print(f"   Start in: {os.getcwd()}")
    print("6. Finish and test the task")

def setup_cron():
    """Instructions for Linux/Mac cron setup"""
    print("\n🔧 CRON SETUP (Linux/Mac)")
    print("="*30)
    print("Add this line to your crontab (crontab -e):")
    print(f"0 6 * * * cd {os.getcwd()} && python3 enterprise_scraper.py")

def main():
    print("🚀 Enterprise Permit Scraper Setup")
    print("="*40)
    
    # Install dependencies
    install_requirements()
    
    # Create directories
    create_directories()
    
    # Configuration setup
    print("\n📝 CONFIGURATION SETUP")
    print("="*25)
    print("1. Copy 'config.env.template' to '.env'")
    print("2. Fill in your API tokens and email settings")
    print("3. Test the scraper with: python enterprise_scraper.py")
    
    # Automation setup
    if os.name == 'nt':  # Windows
        setup_task_scheduler()
    else:  # Linux/Mac
        setup_cron()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Configure your .env file")
    print("2. Test: python enterprise_scraper.py")
    print("3. Set up daily automation")
    print("4. Download license CSVs if needed")

if __name__ == "__main__":
    main()
