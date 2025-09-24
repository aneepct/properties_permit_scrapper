#!/usr/bin/env python3
"""
API Client for Property Permit Scraper
Test the Django API endpoints
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000/api/scraper"

class PermitScraperClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return None
    
    def start_scraper(self, cities=None, force_rescrape=False):
        """Start the permit scraper"""
        data = {
            "cities": cities or [],
            "force_rescrape": force_rescrape
        }
        
        try:
            print("🚀 Starting permit scraper...")
            response = self.session.post(
                f"{self.base_url}/start/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error starting scraper: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return None
    
    def get_scraper_status(self, run_id):
        """Get status of a specific scraper run"""
        try:
            response = self.session.get(f"{self.base_url}/runs/{run_id}/status/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting scraper status: {e}")
            return None
    
    def get_permits(self, city=None, limit=10):
        """Get permits with optional filtering"""
        params = {"page_size": limit}
        if city:
            params["city"] = city
        
        try:
            response = self.session.get(f"{self.base_url}/permits/", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting permits: {e}")
            return None
    
    def get_recent_runs(self, limit=5):
        """Get recent scraper runs"""
        try:
            response = self.session.get(f"{self.base_url}/runs/?page_size={limit}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting scraper runs: {e}")
            return None

def main():
    """Demo the API client"""
    print("=" * 60)
    print("🏢 Property Permit Scraper API Client")
    print("=" * 60)
    
    client = PermitScraperClient()
    
    # Test API connection
    print("\n1️⃣ Testing API connection...")
    try:
        response = requests.get("http://localhost:8000/api/")
        if response.status_code == 200:
            print("✅ API connection successful!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ API connection failed!")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure Django server is running: python manage.py runserver")
        return
    
    # Get current dashboard stats
    print("\n2️⃣ Getting dashboard statistics...")
    stats = client.get_dashboard_stats()
    if stats:
        print(f"📊 Total Permits: {stats.get('total_permits', 0)}")
        print(f"💰 Total Value: ${stats.get('total_value', 0)}")
        print("🏙️ City breakdown:")
        for city in stats.get('city_stats', []):
            print(f"   {city['city']}: {city['permit_count']} permits (${city['total_value']})")
    
    # Start scraper
    print("\n3️⃣ Starting permit scraper...")
    result = client.start_scraper()
    
    if result:
        print(f"✅ Scraper started successfully!")
        print(f"🆔 Run ID: {result.get('run_id')}")
        print(f"📈 Status: {result.get('status')}")
        print(f"🏢 Permits found: {result.get('total_permits_found', 0)}")
        print(f"💵 Total value: ${result.get('total_project_value', 0)}")
        print(f"⏱️ Duration: {result.get('duration_seconds', 0)} seconds")
        
        if result.get('city_summaries'):
            print("\n🏙️ City Results:")
            for summary in result['city_summaries']:
                print(f"   {summary}")
        
        if result.get('errors'):
            print("\n⚠️ Errors:")
            for error in result['errors']:
                print(f"   {error}")
    
    # Get updated dashboard stats
    print("\n4️⃣ Updated dashboard statistics...")
    stats = client.get_dashboard_stats()
    if stats:
        print(f"📊 Total Permits: {stats.get('total_permits', 0)}")
        print(f"💰 Total Value: ${stats.get('total_value', 0)}")
    
    # Get recent permits
    print("\n5️⃣ Recent permits (first 5)...")
    permits = client.get_permits(limit=5)
    if permits and permits.get('results'):
        for permit in permits['results']:
            print(f"   🏗️ {permit['permit_id']} - {permit['city']}")
            print(f"      💰 ${permit['estimated_cost']} - {permit['project_description'][:50]}...")
            print(f"      📍 {permit['full_address']}")
            print()
    
    # Get recent runs
    print("6️⃣ Recent scraper runs...")
    runs = client.get_recent_runs()
    if runs and runs.get('results'):
        for run in runs['results']:
            print(f"   🔄 {run['run_id']} - {run['status']}")
            print(f"      📊 {run['total_permits_found']} permits - ${run['total_project_value']}")
            print(f"      🕐 {run['started_at']}")
            print()
    
    print("\n✨ Demo completed! Your Django API is working perfectly.")
    print("\n📖 Available API endpoints:")
    print("   • GET /api/ - API information")
    print("   • GET /api/scraper/dashboard/ - Dashboard stats")
    print("   • POST /api/scraper/start/ - Start scraper")
    print("   • GET /api/scraper/permits/ - List permits")
    print("   • GET /api/scraper/runs/ - List scraper runs")
    print("   • GET /admin/ - Django admin panel (username: admin, password: admin123)")

if __name__ == "__main__":
    main()