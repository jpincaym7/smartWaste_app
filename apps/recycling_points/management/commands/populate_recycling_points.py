# apps/recycling_points/management/commands/populate_recycling_points.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.recycling_points.models import RecyclingPoint
from apps.waste.models import WasteCategory
import requests
import logging
from time import sleep

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populate reciclaje from OpenStreetMap data'

    def add_arguments(self, parser):
        parser.add_argument('--area', type=str, help='Area to search (e.g., "Guayaquil, Ecuador")')
        parser.add_argument('--radius', type=float, default=10.0, help='Search radius in km')
        
    def handle(self, *args, **options):
        area = options['area']
        radius = options['radius']
        
        # First, get area coordinates using Nominatim
        area_coords = self.get_area_coordinates(area)
        if not area_coords:
            self.stdout.write(self.style.ERROR(f'Could not find coordinates for {area}'))
            return
            
        # Search for recycling points using Overpass API
        points = self.get_recycling_points(area_coords, radius)
        
        # Create default waste categories if they don't exist
        waste_categories = self.ensure_waste_categories()
        
        # Save points to database
        created_count = self.save_points(points, waste_categories)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} recycling points')
        )
    
    def get_area_coordinates(self, area):
        """Get coordinates for an area using Nominatim"""
        nominatim_url = f"https://nominatim.openstreetmap.org/search"
        params = {
            'q': area,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'RecyclingPointsPopulator/1.0'}
        
        try:
            response = requests.get(nominatim_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    'lat': float(data[0]['lat']),
                    'lon': float(data[0]['lon'])
                }
        except Exception as e:
            logger.error(f"Error getting coordinates for {area}: {str(e)}")
        
        return None
    
    def get_recycling_points(self, coords, radius):
        """Get recycling points using Overpass API"""
        overpass_url = "http://overpass-api.de/api/interpreter"
        
        # Query for recycling points and industrial facilities that might handle recycling
        query = f"""
            [out:json][timeout:25];
            (
            node["amenity"="recycling"](around:{radius*1000},{coords['lat']},{coords['lon']});
            way["amenity"="recycling"](around:{radius*1000},{coords['lat']},{coords['lon']});
            );
            out body;
            >;
            out skel qt;
            """

        
        try:
            response = requests.post(overpass_url, data={'data': query})
            response.raise_for_status()
            data = response.json()
            
            return data.get('elements', [])
        except Exception as e:
            logger.error(f"Error fetching recycling points: {str(e)}")
            return []
    
    def ensure_waste_categories(self):
        """Ensure default waste categories exist"""
        default_categories = [
            {
                'name': 'Plastic',
                'description': 'Plastic containers and packaging',
                'recycling_instructions': 'Clean and dry before recycling'
            },
            {
                'name': 'Glass',
                'description': 'Glass bottles and containers',
                'recycling_instructions': 'Remove caps and rinse'
            },
            {
                'name': 'Paper',
                'description': 'Paper and cardboard',
                'recycling_instructions': 'Flatten boxes and remove tape'
            },
            {
                'name': 'Metal',
                'description': 'Metal containers and scrap',
                'recycling_instructions': 'Clean and separate by type'
            },
            {
                'name': 'Electronics',
                'description': 'Electronic waste and devices',
                'recycling_instructions': 'Remove batteries and personal data'
            }
        ]
        
        categories = {}
        for cat_data in default_categories:
            cat, _ = WasteCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'recycling_instructions': cat_data['recycling_instructions']
                }
            )
            categories[cat.name.lower()] = cat
        
        return categories
    
    @transaction.atomic
    def save_points(self, points, waste_categories):
        """Save recycling points to database"""
        created_count = 0
        
        for point in points:
            if point.get('type') != 'node':
                continue
                
            tags = point.get('tags', {})
            if not tags:
                continue
            
            # Extract point data
            name = tags.get('name', f"Recycling Point {point['id']}")
            
            # Create or update recycling point
            try:
                recycling_point, created = RecyclingPoint.objects.get_or_create(
                    latitude=point['lat'],
                    longitude=point['lon'],
                    defaults={
                        'name': name,
                        'address': tags.get('addr:full', tags.get('addr:street', '')),
                        'is_active': True
                    }
                )
                
                # Assign waste types based on tags
                if created:
                    self.assign_waste_types(recycling_point, tags, waste_categories)
                    created_count += 1
                    
            except Exception as e:
                logger.error(f"Error saving recycling point {name}: {str(e)}")
                continue
                
            # Respect API rate limits
            sleep(0.1)
        
        return created_count
    
    def assign_waste_types(self, point, tags, waste_categories):
        """Assign waste types to recycling point based on OSM tags"""
        materials = {
            'plastic': ['plastic'],
            'glass': ['glass', 'bottles'],
            'paper': ['paper', 'newspaper', 'cardboard'],
            'metal': ['metal', 'scrap_metal', 'cans'],
            'electronics': ['electronics', 'e-waste', 'batteries']
        }
        
        # Check tags for recycling materials
        for category, keywords in materials.items():
            if category in waste_categories:
                # Check if any keyword is in the tags
                for tag, value in tags.items():
                    if any(keyword in tag.lower() or keyword in value.lower() for keyword in keywords):
                        point.waste_types.add(waste_categories[category])
                        break