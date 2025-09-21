@echo off
REM Windows Task Scheduler Batch Script for Daily Permit Scraper
REM Save this as run_permit_scraper.bat

cd /d "C:\Sites\nicholas\properties"
python MAIN_permit_scraper.py

REM Optional: Add error handling
if errorlevel 1 (
    echo Scraper failed with error level %errorlevel%
    REM Could send alert email here
)
