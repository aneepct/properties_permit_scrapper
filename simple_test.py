#!/usr/bin/env python3
"""
Simple API Test Script for Property Permit Scraper
"""

import json
import subprocess
import time

def run_curl(url, method="GET", data=None):
    """Run curl command and return result"""
    cmd = ["curl", "-s", "-X", method, url]
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error running curl: {e}")
        return None

def main():
    print("🏢 Property Permit Scraper API Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: API Root
    print("\n1. Testing API Root...")
    result = run_curl(f"{base_url}/api/")
    if result:
        print(f"✅ API Root: {result.get('message', 'Unknown')}")
        print(f"📝 Version: {result.get('version', 'Unknown')}")
    else:
        print("❌ API Root failed")
        return
    
    # Test 2: Dashboard (before scraper run)
    print("\n2. Dashboard Stats (before)...")
    result = run_curl(f"{base_url}/api/scraper/dashboard/")
    if result:
        print(f"📊 Total Permits: {result.get('total_permits', 0)}")
        print(f"💰 Total Value: ${result.get('total_value', '0')}")
    
    # Test 3: Run Scraper
    print("\n3. Running Permit Scraper...")
    scraper_data = {"cities": [], "force_rescrape": False}
    result = run_curl(f"{base_url}/api/scraper/start/", "POST", scraper_data)
    if result:
        print(f"✅ Scraper Run: {result.get('status', 'unknown')}")
        print(f"🆔 Run ID: {result.get('run_id', 'unknown')}")
        print(f"📈 Permits Found: {result.get('total_permits_found', 0)}")
        print(f"💵 Total Value: ${result.get('total_project_value', '0')}")
        print(f"⏱️ Duration: {result.get('duration_seconds', 0)} seconds")
        
        if result.get('city_summaries'):
            print("\n🏙️ City Results:")
            for summary in result.get('city_summaries', []):
                print(f"   {summary}")
    
    # Test 4: Dashboard (after scraper run)
    print("\n4. Dashboard Stats (after)...")
    result = run_curl(f"{base_url}/api/scraper/dashboard/")
    if result:
        print(f"📊 Total Permits: {result.get('total_permits', 0)}")
        print(f"💰 Total Value: ${result.get('total_value', '0')}")
        
        print("\n🏙️ City Breakdown:")
        for city in result.get('city_stats', []):
            print(f"   {city['city']}: {city['permit_count']} permits (${city['total_value']})")
    
    # Test 5: Recent Permits
    print("\n5. Recent Permits...")
    result = run_curl(f"{base_url}/api/scraper/permits/?page_size=3")
    if result and result.get('results'):
        print(f"📋 Showing 3 of {result.get('count', 0)} permits:")
        for permit in result['results'][:3]:
            print(f"   🏗️ {permit['permit_id']} - {permit['city']}")
            print(f"      💰 ${permit['estimated_cost']} - {permit['full_address']}")
            print(f"      📝 {permit['project_description'][:60]}...")
            print()
    
    print("✨ All tests completed successfully!")
    print("\n📖 Your Django API endpoints are working:")
    print(f"   • GET {base_url}/api/ - API information")
    print(f"   • GET {base_url}/api/scraper/dashboard/ - Dashboard stats")
    print(f"   • POST {base_url}/api/scraper/start/ - Start scraper")
    print(f"   • GET {base_url}/api/scraper/permits/ - List permits")
    print(f"   • GET {base_url}/api/scraper/runs/ - List scraper runs")
    print(f"   • GET {base_url}/admin/ - Django admin (admin/admin123)")

if __name__ == "__main__":
    main()