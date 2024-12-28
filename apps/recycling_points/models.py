from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.waste.models import WasteCategory

# Create your models here.
class RecyclingPoint(models.Model):
    """Puntos de reciclaje"""
    name = models.CharField(_('name'), max_length=100)
    address = models.CharField(_('address'), max_length=255)
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    accepted_categories = models.ManyToManyField(
        WasteCategory,
        verbose_name=_('accepted categories'),
        related_name='recycling_points'
    )
    is_active = models.BooleanField(_('is active'), default=True)
    opening_hours = models.JSONField(_('opening hours'), default=dict)
    contact_info = models.JSONField(_('contact info'), default=dict)
    
    class Meta:
        verbose_name = _('recycling point')
        verbose_name_plural = _('recycling points')
        
    def __str__(self):
        return self.name