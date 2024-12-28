from rest_framework import serializers
from apps.gamification.models import TrashReport, ReportComment

class TrashReportSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = TrashReport
        fields = [
            'id', 'user', 'latitude', 'longitude', 'image', 'description',
            'severity', 'severity_display', 'is_recurring', 'status',
            'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

class TrashReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrashReport
        fields = ['latitude', 'longitude', 'image', 'description', 'severity', 'is_recurring']

class NearbyTrashReportSerializer(TrashReportSerializer):
    distance = serializers.FloatField(read_only=True)
    
    class Meta(TrashReportSerializer.Meta):
        fields = TrashReportSerializer.Meta.fields + ['distance']

class ReportCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = ReportComment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']