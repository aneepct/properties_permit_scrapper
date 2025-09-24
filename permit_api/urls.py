"""
URL configuration for permit_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Property Permit Scraper API',
        'version': '1.0',
        'endpoints': {
            'scraper': '/api/scraper/',
            'permits': '/api/scraper/permits/',
            'runs': '/api/scraper/runs/',
            'dashboard': '/api/scraper/dashboard/',
            'start_scraper': '/api/scraper/start/',
            'admin': '/admin/',
        },
        'documentation': 'Send POST to /api/scraper/start/ to run the permit scraper'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/scraper/', include('scraper.urls')),
    path('', api_root, name='home'),  # Root URL shows API info
]
