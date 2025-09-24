from django.urls import path
from . import views

app_name = 'scraper'

urlpatterns = [
    # Permit endpoints
    path('permits/', views.PermitListView.as_view(), name='permit-list'),
    path('permits/<int:pk>/', views.PermitDetailView.as_view(), name='permit-detail'),
    
    # Scraper run endpoints
    path('runs/', views.ScraperRunListView.as_view(), name='scraper-run-list'),
    path('runs/<int:pk>/', views.ScraperRunDetailView.as_view(), name='scraper-run-detail'),
    path('runs/<str:run_id>/status/', views.scraper_status, name='scraper-status'),
    
    # Scraper control endpoints
    path('start/', views.start_scraper, name='start-scraper'),
    
    # Dashboard endpoint
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
]