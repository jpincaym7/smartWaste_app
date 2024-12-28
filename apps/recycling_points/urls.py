from django.urls import path
from apps.recycling_points.views.points import RecyclingMapView, RecyclingPointsAPIView

app_name = 'recycling_points'

urlpatterns = [
    path('points/', RecyclingMapView.as_view(), name='points'),
    path('api/recycling-points/', RecyclingPointsAPIView.as_view(), name='api-points'),
]