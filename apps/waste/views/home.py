from django.views.generic import TemplateView
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from apps.waste.models import WasteCategory, ImpactMetric
from apps.recycling_points.models import RecyclingPoint
from django.http import HttpResponseRedirect
from django.urls import reverse

class HomeView(TemplateView, LoginRequiredMixin):
    template_name = 'home.html'
    
    # Redirigir si no está autenticado
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('security:login'))  # Redirige explícitamente a la página de login
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all waste categories with their icons
        context['categories'] = WasteCategory.objects.all()
        
        # Get nearby recycling points
        context['recycling_points_count'] = RecyclingPoint.objects.filter(
            is_active=True
        ).count()
        
        # Solo si el usuario está logueado, obtén las métricas de impacto
        if self.request.user.is_authenticated:
            # Get user's impact metrics for the last 30 days
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            user_metrics = ImpactMetric.objects.filter(
                user=self.request.user,
                date__gte=thirty_days_ago
            )
            
            context['user_stats'] = {
                'total_items': user_metrics.aggregate(total=Sum('quantity'))['total'] or 0,
                'co2_saved': user_metrics.aggregate(total=Sum('co2_saved'))['total'] or 0,
                'water_saved': user_metrics.aggregate(total=Sum('water_saved'))['total'] or 0,
                'categories_recycled': user_metrics.values('waste_category').distinct().count()
            }
        
        return context
