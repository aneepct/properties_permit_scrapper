from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, render
import csv
import os
import zipfile
import tempfile
import time
from datetime import datetime
from django.utils import timezone
from .models import Permit, ScraperRun, FileProcessor


@admin.register(FileProcessor)
class FileProcessorAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'upload_file', 'status', 'files_count', 
        'uploaded_at', 'processed_at'
    ]
    list_filter = ['status', 'uploaded_at']
    readonly_fields = [
        'upload_file', 'uploaded_at', 'processed_at', 'files_count', 
        'output_file', 'error_message', 'status'
    ]
    
    def has_add_permission(self, request):
        """Remove the 'Add' button from admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make records read-only"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup"""
        return True
    
    fieldsets = (
        ('File Upload', {
            'fields': ('upload_file', 'status')
        }),
        ('Processing Results', {
            'fields': (
                'files_count', 'output_file', 'processed_at', 'error_message'
            )
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('process-zip/', self.admin_site.admin_view(self.process_zip_view), name='process_zip'),
            path('<int:object_id>/process/', self.admin_site.admin_view(self.process_single_file), name='process_single_file'),
            path('cleanup/<int:processor_id>/', self.admin_site.admin_view(self.cleanup_files_view), name='cleanup_files'),
        ]
        return custom_urls + urls
    
    def process_zip_view(self, request):
        """Handle ZIP processing from the admin"""
        import logging
        logger = logging.getLogger('scraper')
        
        if request.method == 'POST' and request.FILES.get('zip_file'):
            processor = None
            try:
                zip_file = request.FILES['zip_file']
                logger.info(f"Starting ZIP processing: {zip_file.name}, size: {zip_file.size} bytes")
                
                # Validate file size (1.5GB limit)
                max_size = 1610612736  # 1.5GB in bytes
                if zip_file.size > max_size:
                    error_msg = f'File too large: {zip_file.size} bytes (max: {max_size} bytes)'
                    logger.error(error_msg)
                    messages.error(request, error_msg)
                    return HttpResponseRedirect('../')
                
                # Create FileProcessor instance
                processor = FileProcessor.objects.create(
                    upload_file=zip_file,
                    status='processing'
                )
                logger.info(f"Created FileProcessor ID: {processor.id}")
                
                # Process the file with enhanced error handling
                try:
                    output_path = self._process_zip_file(processor)
                    logger.info(f"Processing completed for ID: {processor.id}, output: {output_path}")
                    
                    if processor.status == 'completed' and output_path:
                        # Auto-download the processed file
                        response = self._serve_and_cleanup_file(processor, output_path)
                        logger.info(f"File served for download: {processor.id}")
                        return response
                    else:
                        error_msg = f'Processing failed: {processor.error_message or "Unknown error"}'
                        logger.error(f"Processing failed for ID {processor.id}: {processor.error_message}")
                        messages.error(request, error_msg)
                        # Clean up failed processor
                        if processor:
                            try:
                                processor.delete()
                            except:
                                pass
                        return HttpResponseRedirect('../')
                        
                except Exception as process_error:
                    logger.error(f"Processing error for ID {processor.id}: {str(process_error)}", exc_info=True)
                    if processor:
                        processor.status = 'failed'
                        processor.error_message = str(process_error)
                        processor.save()
                    raise process_error
                
            except Exception as e:
                error_msg = f'Error processing ZIP file: {str(e)}'
                logger.error(error_msg, exc_info=True)
                messages.error(request, error_msg)
                # Clean up failed processor
                if processor:
                    try:
                        processor.delete()
                    except:
                        pass
                return HttpResponseRedirect('../')
        
        # Show upload form
        return render(request, 'admin/scraper/fileprocessor/upload_zip.html')
    
    def process_single_file(self, request, object_id):
        """Process a single uploaded file"""
        try:
            processor = FileProcessor.objects.get(id=object_id)
            if processor.status != 'uploaded':
                messages.warning(request, 'File has already been processed or is currently processing.')
                return HttpResponseRedirect('../')
            
            processor.status = 'processing'
            processor.save()
            
            self._process_zip_file(processor)
            
            messages.success(
                request, 
                f'File processed successfully! {processor.files_count} files found.'
            )
            
        except FileProcessor.DoesNotExist:
            messages.error(request, 'File not found.')
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            
        return HttpResponseRedirect('../')
    
    def cleanup_files_view(self, request, processor_id):
        """Handle cleanup request from client after download completes"""
        from django.http import JsonResponse
        
        try:
            # Get processor and output path from headers or session
            processor = FileProcessor.objects.get(id=processor_id)
            
            # Get output path from the processor record
            from django.conf import settings
            output_path = os.path.join(settings.MEDIA_ROOT, 'processed', processor.output_file)
            
            # Perform cleanup
            self._cleanup_files(processor, output_path)
            
            return JsonResponse({'status': 'success', 'message': 'Files cleaned up successfully'})
            
        except FileProcessor.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Processor not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    def _serve_and_cleanup_file(self, processor, output_path):
        """Serve the file for download and cleanup all related files"""
        import mimetypes
        import threading
        
        try:
            # Determine the content type
            content_type, _ = mimetypes.guess_type(output_path)
            if not content_type:
                content_type = 'application/zip'
            
            # Read the file content into memory
            with open(output_path, 'rb') as f:
                file_content = f.read()
            
            # Create download response
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{processor.output_file}"'
            response['Content-Length'] = len(file_content)
            
            # Set custom headers for client-side cleanup notification
            response['X-Cleanup-Required'] = 'true'
            response['X-Processor-ID'] = str(processor.id)
            response['X-Output-Path'] = output_path
            
            # Schedule a fallback cleanup in case client doesn't notify us
            # This ensures files are cleaned up even if the client-side cleanup fails
            def fallback_cleanup():
                import time
                time.sleep(30)  # Wait 30 seconds as fallback
                try:
                    # Check if processor still exists (means client cleanup didn't work)
                    test_processor = FileProcessor.objects.get(id=processor.id)
                    self._cleanup_files(test_processor, output_path)
                except FileProcessor.DoesNotExist:
                    # Already cleaned up by client notification - good!
                    pass
                except Exception as e:
                    print(f"Fallback cleanup error: {str(e)}")
            
            cleanup_thread = threading.Thread(target=fallback_cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            return response
            
        except Exception as e:
            # Cleanup immediately on error
            self._cleanup_files(processor, output_path)
            raise e
    
    def _cleanup_files(self, processor, output_path):
        """Clean up all files related to this processing"""
        import os
        import logging
        
        logger = logging.getLogger(__name__)
        files_deleted = []
        errors = []
        
        try:
            # Delete the processed output file
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    files_deleted.append(f"Processed file: {output_path}")
                    logger.info(f"Deleted processed file: {output_path}")
                except Exception as e:
                    errors.append(f"Failed to delete processed file {output_path}: {str(e)}")
            
            # Delete the uploaded file
            if processor.upload_file:
                upload_path = processor.upload_file.path
                if os.path.exists(upload_path):
                    try:
                        os.remove(upload_path)
                        files_deleted.append(f"Uploaded file: {upload_path}")
                        logger.info(f"Deleted uploaded file: {upload_path}")
                    except Exception as e:
                        errors.append(f"Failed to delete uploaded file {upload_path}: {str(e)}")
            
            # Clean up any remaining temporary directories
            temp_base = os.path.join(os.path.dirname(output_path or ''), '..', '..', 'temp')
            if os.path.exists(temp_base):
                for item in os.listdir(temp_base):
                    if item.startswith(f'process_{processor.id}_'):
                        temp_path = os.path.join(temp_base, item)
                        try:
                            import shutil
                            if os.path.isdir(temp_path):
                                shutil.rmtree(temp_path)
                                files_deleted.append(f"Temp directory: {temp_path}")
                                logger.info(f"Deleted temp directory: {temp_path}")
                        except Exception as e:
                            errors.append(f"Failed to delete temp directory {temp_path}: {str(e)}")
            
            # Delete the database record last
            try:
                processor_id = processor.id
                processor.delete()
                logger.info(f"Deleted database record for processor ID: {processor_id}")
            except Exception as e:
                errors.append(f"Failed to delete database record: {str(e)}")
            
            # Log summary
            if files_deleted:
                logger.info(f"Cleanup completed. Deleted: {', '.join(files_deleted)}")
            if errors:
                logger.error(f"Cleanup errors: {', '.join(errors)}")
                
        except Exception as e:
            logger.error(f"Cleanup failed with unexpected error: {str(e)}")
            print(f"Cleanup error: {str(e)}")
    
    def _process_zip_file(self, processor):
        """Extract ZIP file and combine all files into a new ZIP"""
        from django.conf import settings
        import shutil
        
        output_path = None
        try:
            # Ensure directories exist
            temp_dir = os.path.join(settings.BASE_DIR, 'temp')
            processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
            os.makedirs(temp_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)
            
            # Create unique working directory
            work_dir = os.path.join(temp_dir, f'process_{processor.id}_{int(time.time())}')
            os.makedirs(work_dir, exist_ok=True)
            
            # Extract the uploaded ZIP file
            extract_dir = os.path.join(work_dir, 'extracted')
            with zipfile.ZipFile(processor.upload_file.path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Collect all files recursively
            all_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Skip hidden files and directories
                    if not file.startswith('.') and os.path.isfile(file_path):
                        all_files.append(file_path)
            
            # Create output ZIP with timestamp
            timestamp = int(time.time())
            output_filename = f'combined_files_{timestamp}.zip'
            output_path = os.path.join(processed_dir, output_filename)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as output_zip:
                for file_path in all_files:
                    # Get relative path from extracted directory
                    rel_path = os.path.relpath(file_path, extract_dir)
                    # Add file to ZIP with flattened structure
                    filename = os.path.basename(file_path)
                    # Handle duplicate filenames by adding directory info
                    if rel_path != filename:
                        dir_name = os.path.dirname(rel_path).replace(os.sep, '_')
                        if dir_name:
                            filename = f"{dir_name}_{filename}"
                    
                    output_zip.write(file_path, filename)
            
            # Update processor record
            processor.status = 'completed'
            processor.processed_at = timezone.now()
            processor.files_count = len(all_files)
            processor.output_file = output_filename
            processor.save()
            
            # Clean up temporary directory
            shutil.rmtree(work_dir)
            
            return output_path
            
        except Exception as e:
            processor.status = 'failed'
            processor.error_message = str(e)
            processor.save()
            
            # Clean up on error
            if 'work_dir' in locals() and os.path.exists(work_dir):
                shutil.rmtree(work_dir)
            
            raise e
        
        return None
    
    def changelist_view(self, request, extra_context=None):
        """Add custom context for the changelist"""
        extra_context = extra_context or {}
        extra_context['show_upload_button'] = True
        return super().changelist_view(request, extra_context)


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
