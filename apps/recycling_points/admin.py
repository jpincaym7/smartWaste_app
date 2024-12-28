from django.contrib import admin
from apps.recycling_points.models import RecyclingPoint

class RecyclingPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude', 'is_active')  # Campos a mostrar en la lista
    list_filter = ('is_active', 'accepted_categories')  # Filtros en la barra lateral
    search_fields = ('name', 'address')  # Campos por los cuales se puede buscar
    ordering = ('name',)  # Orden de la lista por defecto
    filter_horizontal = ('accepted_categories',)  # Para ManyToManyField, un selector más limpio
    fieldsets = (
        (None, {
            'fields': ('name', 'address', 'latitude', 'longitude', 'is_active')
        }),
        ('Hours and Contact', {
            'fields': ('opening_hours', 'contact_info')
        }),
        ('Categories', {
            'fields': ('accepted_categories',)
        }),
    )  # División de campos en la vista de detalle

admin.site.register(RecyclingPoint, RecyclingPointAdmin)
