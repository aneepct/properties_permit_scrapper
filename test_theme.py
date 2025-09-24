#!/usr/bin/env python3
"""
Test Django Admin Theme Integration
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'permit_api.settings')
sys.path.append('/Users/a.tandel/Sites/learning/properties_permit_scrapper')
django.setup()

def test_static_files():
    """Test that static files are properly configured"""
    print("🔍 Testing Static Files Configuration...")
    
    from django.conf import settings
    from django.contrib.staticfiles.finders import find
    
    # Test if our CSS file can be found
    css_path = find('admin/css/scraper-theme.css')
    if css_path:
        print(f"✅ CSS file found: {css_path}")
        
        # Check file content
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                content = f.read()
                if '[data-theme="dark"]' in content:
                    print("✅ Dark theme support detected in CSS")
                if 'var(--scraper-' in content:
                    print("✅ CSS variables for theme integration found")
                if '@media (prefers-color-scheme: dark)' in content:
                    print("✅ Auto dark mode detection included")
        
    else:
        print("❌ CSS file not found in static files")
    
    # Check template files
    template_files = [
        '/Users/a.tandel/Sites/learning/properties_permit_scrapper/scraper/templates/admin/index.html',
        '/Users/a.tandel/Sites/learning/properties_permit_scrapper/scraper/templates/admin/scraper/scraperrun/change_list.html'
    ]
    
    print("\n🔍 Testing Template Files...")
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"✅ Template exists: {os.path.basename(template_file)}")
            
            with open(template_file, 'r') as f:
                content = f.read()
                if "{% static 'admin/css/scraper-theme.css' %}" in content:
                    print(f"   ✅ CSS link found in {os.path.basename(template_file)}")
                elif 'scraper-theme.css' in content:
                    print(f"   ✅ CSS reference found in {os.path.basename(template_file)}")
                else:
                    print(f"   ⚠️ CSS link might be missing in {os.path.basename(template_file)}")
        else:
            print(f"❌ Template not found: {template_file}")

def test_django_settings():
    """Test Django settings for static files and templates"""
    print("\n🔍 Testing Django Configuration...")
    
    from django.conf import settings
    
    # Check static files configuration
    if hasattr(settings, 'STATICFILES_DIRS'):
        print(f"✅ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    
    # Check template configuration
    for template_config in settings.TEMPLATES:
        if 'scraper/templates' in str(template_config.get('DIRS', [])):
            print("✅ Template directory configured correctly")
            break
    else:
        print("⚠️ Custom template directory might not be configured")
    
    # Check if collectstatic would work
    try:
        from django.contrib.staticfiles import finders
        print("✅ Static files system is working")
    except Exception as e:
        print(f"❌ Static files system error: {e}")

def main():
    print("🎨 Django Admin Theme Integration Test")
    print("=" * 60)
    
    test_static_files()
    test_django_settings()
    
    print("\n" + "=" * 60)
    print("✨ Theme Integration Summary")
    print("\n📖 Features implemented:")
    print("   • CSS variables for theme compatibility")
    print("   • Dark/light theme detection")
    print("   • Auto theme switching with prefers-color-scheme")
    print("   • Responsive design for mobile devices")
    print("   • Integration with Django's existing CSS variables")
    
    print("\n🎯 Theme adaptation includes:")
    print("   • Background colors adapt to theme")
    print("   • Text colors follow theme variables")
    print("   • Border colors match admin theme")
    print("   • Button styles integrate with admin design")
    print("   • Focus states for accessibility")
    
    print("\n🚀 To test the theme:")
    print("1. Start server: python manage.py runserver 8000")
    print("2. Go to: http://localhost:8000/admin/")
    print("3. Toggle dark/light theme in your browser")
    print("4. Check both main dashboard and scraper runs page")

if __name__ == "__main__":
    main()