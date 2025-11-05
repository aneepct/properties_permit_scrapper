from django.db import models
from django.utils import timezone


class FileProcessor(models.Model):
    """Model to track file processing operations"""
    upload_file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='uploaded')
    files_count = models.IntegerField(default=0)
    output_file = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'file_processor'
        ordering = ['-uploaded_at']


class Permit(models.Model):
    # Identification fields
    city = models.CharField(max_length=100)
    permit_id = models.CharField(max_length=50, unique=True)
    
    # Date fields
    issue_date = models.DateField()
    scraped_at = models.DateTimeField(default=timezone.now)
    
    # Address information
    full_address = models.CharField(max_length=500)
    borough_area = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Project details
    project_description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Parties involved
    contractor_name = models.CharField(max_length=200, blank=True, null=True)
    contractor_license = models.CharField(max_length=100, blank=True, null=True)
    applicant_name = models.CharField(max_length=200, blank=True, null=True)
    owner_name = models.CharField(max_length=200, blank=True, null=True)
    architect_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Status and contact
    license_status = models.CharField(max_length=50, blank=True, null=True)
    business_address = models.CharField(max_length=500, blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Metadata
    data_source = models.CharField(max_length=200, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permits'
        ordering = ['-issue_date', '-created_at']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['permit_id']),
            models.Index(fields=['scraped_at']),
        ]
    
    def __str__(self):
        return f"{self.permit_id} - {self.city} - ${self.estimated_cost:,}"


class ScraperRun(models.Model):
    """Track scraper execution runs"""
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
    ]
    
    run_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    
    # Run details
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Results
    total_permits_found = models.IntegerField(default=0)
    total_project_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    cities_processed = models.JSONField(default=list)
    errors = models.JSONField(default=list)
    
    # Summary
    summary_report = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'scraper_runs'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Run {self.run_id} - {self.status} - {self.total_permits_found} permits"
