from django.urls import path
from apps.waste.views.capture import  WasteDetectionView

app_name = 'waste'

urlpatterns = [
    path('capture/', WasteDetectionView.as_view(), name="capture"),
]
