from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
import csv
from datetime import datetime
from .models import Permit, ScraperRun


@admin.register(Permit)
class PermitAdmin(admin.ModelAdmin):
    list_display = [
        'permit_id', 'city', 'issue_date', 'formatted_cost', 
        'contractor_name', 'scraped_at'
    ]
    list_filter = [
        'city', 'issue_date', 'license_status', 'scraped_at'
    ]
    search_fields = [
        'permit_id', 'full_address', 'project_description', 
        'contractor_name', 'applicant_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'scraped_at']
    date_hierarchy = 'issue_date'
    actions = ['export_selected_permits']
    
    fieldsets = (
        ('Identification', {
            'fields': ('permit_id', 'city', 'issue_date')
        }),
        ('Location', {
            'fields': ('full_address', 'borough_area', 'zip_code')
        }),
        ('Project Details', {
            'fields': ('project_description', 'estimated_cost')
        }),
        ('Parties Involved', {
            'fields': (
                'contractor_name', 'contractor_license', 
                'applicant_name', 'owner_name', 'architect_name'
            )
        }),
        ('Contact & Status', {
            'fields': (
                'license_status', 'business_address', 'business_phone'
            )
        }),
        ('Metadata', {
            'fields': ('data_source', 'scraped_at', 'created_at', 'updated_at')
        }),
    )
    
    def formatted_cost(self, obj):
        return f"${obj.estimated_cost:,}"
    formatted_cost.short_description = 'Cost'
    formatted_cost.admin_order_field = 'estimated_cost'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-csv/', self.admin_site.admin_view(self.export_permits_csv), name='export_permits_csv'),
        ]
        return custom_urls + urls
    
    def export_permits_csv(self, request):
        """Export all permits to CSV"""
        return self._export_permits_to_csv(request, Permit.objects.all(), "permits")
    
    def _export_permits_to_csv(self, request, queryset, filename_prefix):
        """Helper method to export permits to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write header row with comprehensive fields
        writer.writerow([
            'Permit ID', 'City', 'Issue Date', 'Full Address', 'Borough/Area', 'ZIP Code',
            'Project Description', 'Estimated Cost', 'Contractor Name', 'Contractor License',
            'Applicant Name', 'Owner Name', 'Architect Name', 'License Status',
            'Business Address', 'Business Phone', 'Data Source', 'Scraped At'
        ])
        
        # Write data rows
        for permit in queryset:
            writer.writerow([
                permit.permit_id,
                permit.city,
                permit.issue_date.strftime('%Y-%m-%d') if permit.issue_date else '',
                permit.full_address,
                permit.borough_area or '',
                permit.zip_code or '',
                permit.project_description,
                float(permit.estimated_cost) if permit.estimated_cost else 0,
                permit.contractor_name or '',
                permit.contractor_license or '',
                permit.applicant_name or '',
                permit.owner_name or '',
                permit.architect_name or '',
                permit.license_status or '',
                permit.business_address or '',
                permit.business_phone or '',
                permit.data_source or '',
                permit.scraped_at.strftime('%Y-%m-%d %H:%M:%S') if permit.scraped_at else ''
            ])
        
        count = queryset.count()
        self.message_user(request, f'Successfully exported {count} permits to {filename}')
        return response

    def export_selected_permits(self, request, queryset):
        """Export selected permits to CSV"""
        return self._export_permits_to_csv(request, queryset, "selected_permits")
    
    export_selected_permits.short_description = "Export selected permits to CSV"


class ScraperRunAdmin(admin.ModelAdmin):
    list_display = [
        'run_id', 'status', 'started_at', 'duration_display',
        'total_permits_found', 'formatted_value'
    ]
    list_filter = ['status', 'started_at']
    search_fields = ['run_id']
    readonly_fields = [
        'run_id', 'started_at', 'completed_at', 'duration_seconds',
        'total_permits_found', 'total_project_value', 'cities_processed',
        'errors', 'summary_report'
    ]
    
    fieldsets = (
        ('Run Information', {
            'fields': ('run_id', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds')
        }),
        ('Results', {
            'fields': (
                'total_permits_found', 'total_project_value', 'cities_processed'
            )
        }),
        ('Details', {
            'fields': ('errors', 'summary_report'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        if obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "N/A"
    duration_display.short_description = 'Duration'
    
    def formatted_value(self, obj):
        return f"${obj.total_project_value:,}"
    formatted_value.short_description = 'Total Value'
    formatted_value.admin_order_field = 'total_project_value'


# Custom Admin View for Scraper Control - inherits from ScraperRunAdmin
class ScraperControlAdmin(ScraperRunAdmin):
    """Custom admin view for scraper control"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start-scraper/', self.admin_site.admin_view(self.start_scraper_view), name='scraper_start'),
        ]
        return custom_urls + urls
    
    def start_scraper_view(self, request):
        """Handle the start scraper button click"""
        try:
            # Import the scraper function
            import sys
            import os
            from django.conf import settings
            
            # Add project root to path
            sys.path.append(os.path.dirname(settings.BASE_DIR))
            
            # Import our API view to reuse the scraper logic
            from .views import start_scraper
            from rest_framework.request import Request
            from django.http import HttpRequest
            
            # Create a mock API request
            mock_request = HttpRequest()
            mock_request.method = 'POST'
            mock_request.META['CONTENT_TYPE'] = 'application/json'
            
            # Create a DRF request object
            from rest_framework.test import APIRequestFactory
            factory = APIRequestFactory()
            api_request = factory.post('/api/scraper/start/', {}, format='json')
            
            # Call our existing API function
            response = start_scraper(api_request)
            
            if response.status_code == 200:
                data = response.data
                message = f"✅ Scraper completed successfully!\n"
                message += f"🆔 Run ID: {data.get('run_id', 'Unknown')}\n"
                message += f"📊 Permits found: {data.get('total_permits_found', 0)}\n"
                total_value = int(data.get('total_project_value', 0))
                message += f"💰 Total value: ${total_value:,}\n"
                message += f"⏱️ Duration: {data.get('duration_seconds', 0)} seconds\n"
                
                if data.get('city_summaries'):
                    message += "\n🏙️ City Results:\n"
                    for summary in data.get('city_summaries', []):
                        message += f"   • {summary}\n"
                
                messages.success(request, message)
            else:
                error_data = response.data
                messages.error(request, f"❌ Scraper failed: {error_data.get('error', 'Unknown error')}")
                
        except Exception as e:
            messages.error(request, f"❌ Error starting scraper: {str(e)}")
        
        # Stay on the current page (scraper runs changelist) instead of redirecting
        from django.urls import reverse
        return HttpResponseRedirect(reverse('admin:scraper_scraperrun_changelist'))
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist to add custom buttons"""
        extra_context = extra_context or {}
        extra_context['show_scraper_button'] = True
        return super().changelist_view(request, extra_context)


# Register the admins
admin.site.register(ScraperRun, ScraperControlAdmin)
