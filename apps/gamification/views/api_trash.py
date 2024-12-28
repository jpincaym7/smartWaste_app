import math
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from apps.gamification.models import TrashReport, ReportComment

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on Earth."""
    R = 6371  # Radio de la Tierra en km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

@login_required
def trash_report_list(request):
    """Vista para listar todos los reportes de basura."""
    reports = TrashReport.objects.all().order_by('-created_at')
    # Filtrado por estado
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Búsqueda por descripción
    search_query = request.GET.get('search')
    if search_query:
        reports = reports.filter(description__icontains=search_query)
    
    # Ordenamiento
    order_by = request.GET.get('order_by', '-created_at')
    if order_by in ['created_at', '-created_at', 'severity', '-severity']:
        reports = reports.order_by(order_by)
    
    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(reports, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'severity_choices': TrashReport.SEVERITY_CHOICES,
        'current_status': status_filter,
        'search_query': search_query,
        'order_by': order_by,
    }
    context['maptiler_key'] = "eOJz2rYdmVnQEiFjpgcP"
    return render(request, 'report.html', context)

@login_required
def trash_view(request):
    """Vista para listar todos los reportes de basura."""
    reports = TrashReport.objects.all().order_by('-created_at')
    # Filtrado por estado
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Búsqueda por descripción
    search_query = request.GET.get('search')
    if search_query:
        reports = reports.filter(description__icontains=search_query)
    
    # Ordenamiento
    order_by = request.GET.get('order_by', '-created_at')
    if order_by in ['created_at', '-created_at', 'severity', '-severity']:
        reports = reports.order_by(order_by)
    
    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(reports, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'severity_choices': TrashReport.SEVERITY_CHOICES,
        'current_status': status_filter,
        'search_query': search_query,
        'order_by': order_by,
    }
    context['maptiler_key'] = "eOJz2rYdmVnQEiFjpgcP"
    return render(request, 'list_report.html', context)

@login_required
def list_reports(request):
    reports = TrashReport.objects.all()  # O puedes filtrar según la lógica que desees
    report_data = []
    
    for report in reports:
        report_data.append({
            'description': report.description,
            'location': report.longitude,  # Asegúrate de tener esta información en el modelo
            'severity': report.severity,
            'status': report.status,
            'image_url': report.image.url if report.image else '',  # Ajusta el campo de imagen
        })
    
    return JsonResponse(report_data, safe=False)

@login_required
def trash_report_detail(request, pk):
    """Vista para ver el detalle de un reporte específico."""
    report = get_object_or_404(TrashReport, pk=pk)
    comments = report.comments.all().order_by('-created_at')
    
    context = {
        'report': report,
        'comments': comments,
    }
    
    return render(request, 'trash_reports/detail.html', context)

@login_required
@require_http_methods(["POST"])
def trash_report_create(request):
    """Vista para crear un nuevo reporte."""
    try:
        image = request.FILES.get('image')
        if not image:
            return HttpResponseBadRequest('La imagen es requerida')
        
        report = TrashReport.objects.create(
            user=request.user,
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            image=image,
            description=request.POST.get('description'),
            severity=request.POST.get('severity'),
            is_recurring=request.POST.get('is_recurring') == 'true'
        )
        
        return JsonResponse({
            'id': report.id,
            'message': 'Reporte creado exitosamente'
        })
    except Exception as e:
        return HttpResponseBadRequest(str(e))

@login_required
@require_http_methods(["GET"])
def nearby_reports(request):
    """Vista para encontrar reportes cercanos a una ubicación."""
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        radius = float(request.GET.get('radius', 5.0))
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Parámetros de ubicación inválidos')

    reports = TrashReport.objects.all()
    nearby_reports = []

    for report in reports:
        distance = haversine(lat, lng, float(report.latitude), float(report.longitude))
        if distance <= radius:
            nearby_reports.append({
                'id': report.id,
                'latitude': float(report.latitude),
                'longitude': float(report.longitude),
                'description': report.description,
                'severity': report.severity,
                'status': report.status,
                'distance': round(distance, 2)
            })

    return JsonResponse({'reports': nearby_reports})

@login_required
@require_http_methods(["POST"])
def change_report_status(request, pk):
    """Vista para cambiar el estado de un reporte."""
    report = get_object_or_404(TrashReport, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status not in dict(TrashReport.STATUS_CHOICES):
        return HttpResponseBadRequest('Estado inválido')
    
    report.status = new_status
    report.save()
    
    return JsonResponse({
        'id': report.id,
        'status': report.status,
        'message': 'Estado actualizado exitosamente'
    })

@login_required
@require_http_methods(["POST"])
def add_comment(request, report_pk):
    """Vista para agregar un comentario a un reporte."""
    report = get_object_or_404(TrashReport, pk=report_pk)
    content = request.POST.get('content')
    
    if not content:
        return HttpResponseBadRequest('El contenido del comentario es requerido')
    
    comment = ReportComment.objects.create(
        report=report,
        user=request.user,
        content=content
    )
    
    return JsonResponse({
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'user': comment.user.username
    })
    
class EducationView(TemplateView):
    template_name = 'education.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Datos de videos educativos
        context['education_videos'] = [
            {
                'title': '¿Que es el reciclaje?',
                'thumbnail_url': '/static/img/reciclaje_1.png',
                'video_url': settings.STATIC_VIDEO_URL + 'reciclaje_1.mp4',
                'duration': '2:30'
            },
            {
                'title': '¿Cómo reciclar?',
                'thumbnail_url': '/static/img/reciclaje_2.png',
                'video_url': settings.STATIC_VIDEO_URL + 'como_reciclar_2.mp4',
                'duration': '4:22'
            },
            {
                'title': 'IMPORTANCIA DEL RECICLAJE',
                'thumbnail_url': '/static/img/importancia_1.png',
                'video_url': settings.STATIC_VIDEO_URL + 'importancia_1.mp4',
                'duration': '4:22'
            },
        ]
        print(context)
        return context