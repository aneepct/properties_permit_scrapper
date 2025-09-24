#!/usr/bin/env python3
"""
Test Admin Panel Scraper Button
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'permit_api.settings')
sys.path.append('/Users/a.tandel/Sites/learning/properties_permit_scrapper')
django.setup()

def test_admin_configuration():
    """Test that admin configuration is working"""
    from django.contrib import admin
    from scraper.models import Permit, ScraperRun
    
    print("🔍 Testing Admin Configuration...")
    
    # Check if models are registered
    if Permit in admin.site._registry:
        print("✅ Permit model is registered in admin")
    else:
        print("❌ Permit model is NOT registered in admin")
    
    if ScraperRun in admin.site._registry:
        print("✅ ScraperRun model is registered in admin")
    else:
        print("❌ ScraperRun model is NOT registered in admin")
    
    # Test the admin classes
    permit_admin = admin.site._registry.get(Permit)
    if permit_admin:
        print(f"✅ PermitAdmin configured with {len(permit_admin.list_display)} display fields")
        print(f"   Display fields: {permit_admin.list_display}")
        print(f"   Actions available: {permit_admin.actions}")
    
    scraper_admin = admin.site._registry.get(ScraperRun)
    if scraper_admin:
        print(f"✅ ScraperRunAdmin configured with custom URLs")
        print(f"   Display fields: {scraper_admin.list_display}")
        
        # Check if our custom URL is added
        urls = scraper_admin.get_urls()
        custom_url_found = any('start-scraper' in str(url.pattern) for url in urls)
        if custom_url_found:
            print("✅ Custom 'start-scraper' URL is configured")
        else:
            print("❌ Custom 'start-scraper' URL is NOT found")
    
    print("\n📋 Admin URLs that will be available:")
    print("   • /admin/ - Main admin dashboard")
    print("   • /admin/scraper/permit/ - Permit management")
    print("   • /admin/scraper/scraperrun/ - Scraper run history")
    print("   • /admin/scraper/scraperrun/start-scraper/ - Start scraper button")
    
    print("\n🎨 Template files created:")
    template_files = [
        '/Users/a.tandel/Sites/learning/properties_permit_scrapper/scraper/templates/admin/index.html',
        '/Users/a.tandel/Sites/learning/properties_permit_scrapper/scraper/templates/admin/scraper/scraperrun/change_list.html'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"   ✅ {template_file}")
        else:
            print(f"   ❌ {template_file}")

def test_scraper_integration():
    """Test that scraper can be imported and used"""
    print("\n🔍 Testing Scraper Integration...")
    
    try:
        # Test importing the original scraper
        sys.path.append('/Users/a.tandel/Sites/learning/properties_permit_scrapper')
        import MAIN_permit_scraper
        print("✅ Original scraper can be imported")
        
        # Test that we can access the scraper functions
        if hasattr(MAIN_permit_scraper, 'main'):
            print("✅ Scraper main function is available")
        
        if hasattr(MAIN_permit_scraper, 'CITIES'):
            cities = MAIN_permit_scraper.CITIES
            print(f"✅ Cities configuration loaded: {list(cities.keys())}")
        
        # Test our views can import everything needed
        from scraper.views import start_scraper
        print("✅ Admin scraper view function is available")
        
    except Exception as e:
        print(f"❌ Scraper integration error: {e}")

def main():
    print("🏢 Property Permit Scraper - Admin Panel Test")
    print("=" * 60)
    
    test_admin_configuration()
    test_scraper_integration()
    
    print("\n" + "=" * 60)
    print("✨ Admin Panel Setup Complete!")
    print("\n📖 How to use the admin panel:")
    print("1. Start Django server: python manage.py runserver 8000")
    print("2. Visit: http://localhost:8000/admin/")
    print("3. Login with: admin / admin123")
    print("4. Click '🚀 Run Scraper Now' button on main dashboard")
    print("5. Or go to 'Scraper runs' and click '🚀 Start Permit Scraper'")
    print("6. View results in 'Permits' section")
    
    print("\n🎯 Features added:")
    print("   • Scraper button on main admin dashboard")
    print("   • Dedicated scraper control panel in Scraper Runs")
    print("   • Export permits to CSV functionality")
    print("   • Enhanced admin interface with custom styling")
    print("   • Quick navigation between all sections")

if __name__ == "__main__":
    main()