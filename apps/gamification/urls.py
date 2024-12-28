from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.gamification.views.api_trash import trash_report_list, EducationView, trash_view, list_reports, trash_report_detail, trash_report_create, nearby_reports, change_report_status, add_comment

app_name = 'gamification'

urlpatterns = [
    path('reports/', trash_report_list, name='report-form'),
    path('reports/view/', trash_view, name="reports-view"),
    path('reports/list/', list_reports, name='report-json'),
    path('reports/<int:pk>/', trash_report_detail, name='report-detail'),
    path('reports/create/', trash_report_create, name='report-create'),
    path('reports/nearby/',nearby_reports, name='nearby-reports'),
    path('reports/<int:pk>/status/', change_report_status, name='change-status'),
    path('reports/<int:report_pk>/comments/', add_comment, name='add-comment'),
    path('education/', EducationView.as_view(), name='education'),

]