import os
import sys
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.http import JsonResponse
from django.utils import timezone as django_timezone
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Permit, ScraperRun
from .serializers import PermitSerializer, ScraperRunSerializer, ScraperRunCreateSerializer

# Add the project root to Python path to import the scraper
sys.path.append(os.path.dirname(settings.BASE_DIR))
from MAIN_permit_scraper import main as run_scraper, CITIES


class PermitPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class PermitListView(generics.ListAPIView):
    """List all permits with filtering and pagination"""
    queryset = Permit.objects.all()
    serializer_class = PermitSerializer
    pagination_class = PermitPagination
    
    def get_queryset(self):
        queryset = Permit.objects.all()
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(issue_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(issue_date__lte=end_date)
        
        # Filter by minimum cost
        min_cost = self.request.query_params.get('min_cost')
        if min_cost:
            queryset = queryset.filter(estimated_cost__gte=min_cost)
        
        # Search in description or address
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                project_description__icontains=search
            ) | queryset.filter(
                full_address__icontains=search
            )
        
        return queryset.order_by('-issue_date', '-created_at')


class PermitDetailView(generics.RetrieveAPIView):
    """Get a single permit by ID"""
    queryset = Permit.objects.all()
    serializer_class = PermitSerializer


class ScraperRunListView(generics.ListAPIView):
    """List all scraper runs"""
    queryset = ScraperRun.objects.all()
    serializer_class = ScraperRunSerializer
    pagination_class = PermitPagination


class ScraperRunDetailView(generics.RetrieveAPIView):
    """Get a single scraper run by ID"""
    queryset = ScraperRun.objects.all()
    serializer_class = ScraperRunSerializer


@api_view(['POST'])
def start_scraper(request):
    """API endpoint to start the permit scraper"""
    try:
        serializer = ScraperRunCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid request data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new scraper run record
        run_id = f"run_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        scraper_run = ScraperRun.objects.create(
            run_id=run_id,
            status='running',
        )
        
        try:
            # Execute the scraper (this will run synchronously for now)
            start_time = django_timezone.now()
            
            # Import and run the scraper logic
            from MAIN_permit_scraper import (
                setup_logging, ensure_directories, load_state, save_state,
                process_city, save_city_csv, update_master_csv
            )
            
            # Setup
            logger = setup_logging()
            ensure_directories()
            
            # Run scraper for each city
            all_permits = []
            city_summaries = []
            errors = []
            cities_processed = []
            
            for city_key in CITIES.keys():
                try:
                    logger.info(f"Processing {city_key}")
                    permits = process_city(city_key)
                    
                    if permits:
                        # Save to database
                        for permit_data in permits:
                            try:
                                # Convert string cost to Decimal
                                cost = Decimal(str(permit_data['estimated_cost']))
                                
                                # Parse date
                                issue_date = datetime.strptime(permit_data['issue_date'], '%Y-%m-%d').date()
                                scraped_at = datetime.strptime(permit_data['scraped_at'], '%Y-%m-%d %H:%M:%S')
                                
                                # Create or update permit in database
                                permit, created = Permit.objects.update_or_create(
                                    permit_id=permit_data['permit_id'],
                                    defaults={
                                        'city': permit_data['city'],
                                        'issue_date': issue_date,
                                        'scraped_at': scraped_at,
                                        'full_address': permit_data['full_address'],
                                        'borough_area': permit_data.get('borough_area'),
                                        'zip_code': permit_data.get('zip_code'),
                                        'project_description': permit_data['project_description'],
                                        'estimated_cost': cost,
                                        'contractor_name': permit_data.get('contractor_name'),
                                        'contractor_license': permit_data.get('contractor_license'),
                                        'applicant_name': permit_data.get('applicant_name'),
                                        'owner_name': permit_data.get('owner_name'),
                                        'architect_name': permit_data.get('architect_name'),
                                        'license_status': permit_data.get('license_status'),
                                        'business_address': permit_data.get('business_address'),
                                        'business_phone': permit_data.get('business_phone'),
                                        'data_source': permit_data.get('data_source'),
                                    }
                                )
                                
                            except Exception as e:
                                error_msg = f"Error saving permit {permit_data.get('permit_id', 'unknown')}: {str(e)}"
                                logger.error(error_msg)
                                errors.append(error_msg)
                        
                        all_permits.extend(permits)
                        cities_processed.append(city_key)
                        
                        total_value = sum(int(p["estimated_cost"]) for p in permits)
                        city_summaries.append(f"SUCCESS {CITIES[city_key]['name']}: {len(permits)} permits (${total_value:,})")
                    else:
                        city_summaries.append(f"WARNING {CITIES[city_key]['name']}: No permits found")
                        
                except Exception as e:
                    error_msg = f"Error processing {CITIES[city_key]['name']}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    city_summaries.append(f"ERROR {CITIES[city_key]['name']}: {str(e)}")
            
            # Calculate final results
            end_time = django_timezone.now()
            duration = (end_time - start_time).total_seconds()
            total_permits = len(all_permits)
            total_value = sum(Decimal(str(p["estimated_cost"])) for p in all_permits) if all_permits else Decimal('0')
            
            # Update scraper run record
            scraper_run.status = 'completed' if not errors else ('partial' if total_permits > 0 else 'failed')
            scraper_run.completed_at = end_time
            scraper_run.duration_seconds = int(duration)
            scraper_run.total_permits_found = total_permits
            scraper_run.total_project_value = total_value
            scraper_run.cities_processed = cities_processed
            scraper_run.errors = errors
            scraper_run.summary_report = "\n".join(city_summaries)
            scraper_run.save()
            
            # Prepare response
            response_data = {
                'run_id': run_id,
                'status': scraper_run.status,
                'duration_seconds': duration,
                'total_permits_found': total_permits,
                'total_project_value': str(total_value),
                'cities_processed': cities_processed,
                'city_summaries': city_summaries,
                'errors': errors,
                'message': f'Scraper completed successfully! Found {total_permits} permits worth ${total_value:,}'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Update scraper run with failure
            scraper_run.status = 'failed'
            scraper_run.completed_at = django_timezone.now()
            scraper_run.errors = [str(e)]
            scraper_run.save()
            
            return Response(
                {
                    'error': f'Scraper execution failed: {str(e)}',
                    'run_id': run_id,
                    'status': 'failed'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': f'Failed to start scraper: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def scraper_status(request, run_id):
    """Get the status of a specific scraper run"""
    try:
        scraper_run = ScraperRun.objects.get(run_id=run_id)
        serializer = ScraperRunSerializer(scraper_run)
        return Response(serializer.data)
    except ScraperRun.DoesNotExist:
        return Response(
            {'error': f'Scraper run with ID {run_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        total_permits = Permit.objects.count()
        total_value = Permit.objects.aggregate(
            total=models.Sum('estimated_cost')
        )['total'] or 0
        
        # Recent runs
        recent_runs = ScraperRun.objects.filter(
            status__in=['completed', 'partial']
        ).order_by('-started_at')[:5]
        
        # City breakdown
        city_stats = []
        for city_key, city_data in CITIES.items():
            city_permits = Permit.objects.filter(city=city_data['name'])
            city_count = city_permits.count()
            city_value = city_permits.aggregate(
                total=models.Sum('estimated_cost')
            )['total'] or 0
            
            city_stats.append({
                'city': city_data['name'],
                'permit_count': city_count,
                'total_value': str(city_value)
            })
        
        return Response({
            'total_permits': total_permits,
            'total_value': str(total_value),
            'city_stats': city_stats,
            'recent_runs': ScraperRunSerializer(recent_runs, many=True).data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get dashboard stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
