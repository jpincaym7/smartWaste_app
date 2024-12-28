from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Optional, Union
from urllib.parse import urljoin

from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse, HttpRequest
from django.db.models import Q, QuerySet
from django.conf import settings
from django.urls import reverse

from apps.recycling_points.models import RecyclingPoint
from apps.waste.models import WasteCategory

class RecyclingMapView(TemplateView):
    """View for rendering the recycling points map page."""
    
    template_name = 'explore.html'
    
    def get_context_data(self, **kwargs) -> Dict:
        """Add API URL to template context."""
        context = super().get_context_data(**kwargs)
        
        # Get the current scheme (http or https)
        scheme = self.request.is_secure() and 'https' or 'http'
        
        # Build the API URL using reverse to get the path
        api_path = reverse('recycling_points:api-points')  # Asegúrate de tener este name en urls.py
        
        # Construct the full URL ensuring HTTPS
        api_url = f'{scheme}://{self.request.get_host()}{api_path}'
        
        # Force HTTPS if we're in production
        if not settings.DEBUG:
            api_url = api_url.replace('http://', 'https://')
        
        context['recycling_points_api_url'] = api_url
        context['maptiler_key'] = "eOJz2rYdmVnQEiFjpgcP" # Mejor mover esto a settings.py
        return context

class RecyclingPointsAPIView(View):
    def dispatch(self, request, *args, **kwargs):
        """Ensure HTTPS in production"""
        if not settings.DEBUG and not request.is_secure():
            # Redirect to HTTPS if accessed via HTTP
            return JsonResponse({
                'error': 'HTTPS is required',
                'details': 'Please use HTTPS to access this API'
            }, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request) -> JsonResponse:
        try:
            # Get all active recycling points
            points = RecyclingPoint.objects.filter(is_active=True)
            
            # Format points for response
            formatted_points = []
            for point in points:
                if point.latitude and point.longitude:
                    try:
                        formatted_points.append({
                            'id': point.id,
                            'name': point.name,
                            'latitude': float(point.latitude),
                            'longitude': float(point.longitude),
                            'address': point.address,
                            'waste_types': list(point.accepted_categories.values_list('name', flat=True)),
                            'contact_info': point.contact_info,
                            'opening_hours': point.opening_hours.get(
                                datetime.now().strftime('%A').lower(), 
                                'closed'
                            )
                        })
                    except (ValueError, TypeError, AttributeError) as e:
                        # Log error but continue processing other points
                        print(f"Error processing point {point.id}: {str(e)}")
                        continue

            return JsonResponse(formatted_points, safe=False)

        except Exception as e:
            return JsonResponse({
                'error': 'An error occurred while retrieving recycling points',
                'details': str(e)
            }, status=500)