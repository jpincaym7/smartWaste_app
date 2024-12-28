from django.contrib import admin

from apps.gamification.models import UserProfile, TrashReport, ReportComment, Badge

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'level', 'total_detections')
    search_fields = ('user__username', 'user__email')
    list_filter = ('level',)
    ordering = ('-points',)

@admin.register(TrashReport)
class TrashReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'severity', 'status', 'created_at')
    search_fields = ('description', 'user__username', 'user__email')
    list_filter = ('status', 'severity', 'is_recurring', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'latitude', 'longitude', 'image', 'description')}),
        ('Detalles', {'fields': ('severity', 'is_recurring', 'status')}),
        ('Tiempos', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ('report', 'user', 'content', 'created_at')
    search_fields = ('report__id', 'user__username', 'content')
    ordering = ('-created_at',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'category')
    search_fields = ('name', 'description', 'category')
    list_filter = ('category',)
    ordering = ('points_required',)
