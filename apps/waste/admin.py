from django.contrib import admin
from apps.waste.models import WasteCategory, ImpactMetric

@admin.register(WasteCategory)
class WasteCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'recycling_instructions', 'icon')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    ordering = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'recycling_instructions', 'icon')
        }),
    )

@admin.register(ImpactMetric)
class ImpactMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'waste_category', 'quantity', 'co2_saved', 'water_saved', 'date')
    search_fields = ('user__username', 'waste_category__name')
    list_filter = ('waste_category', 'date')
    ordering = ['-date']
    fieldsets = (
        (None, {
            'fields': ('user', 'waste_category', 'quantity', 'co2_saved', 'water_saved', 'date')
        }),
    )
