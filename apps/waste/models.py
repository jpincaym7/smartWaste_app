from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
import uuid

class WasteCategory(models.Model):
    """Categorías de residuos (plástico, vidrio, papel, etc.)"""
    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.TextField(_('description'))
    recycling_instructions = models.TextField(_('recycling instructions'))
    icon = models.ImageField(_('icon'), upload_to='waste_categories/icons/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('waste category')
        verbose_name_plural = _('waste categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class ImpactMetric(models.Model):
    """Métricas de impacto ambiental"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impact_metrics',
        verbose_name=_('user')
    )
    waste_category = models.ForeignKey(
        WasteCategory,
        on_delete=models.CASCADE,
        related_name='impact_metrics',
        verbose_name=_('waste category')
    )
    quantity = models.PositiveIntegerField(_('quantity'))
    co2_saved = models.DecimalField(
        _('CO2 saved (kg)'),
        max_digits=10,
        decimal_places=2
    )
    water_saved = models.DecimalField(
        _('water saved (L)'),
        max_digits=10,
        decimal_places=2
    )
    date = models.DateField(_('date'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('impact metric')
        verbose_name_plural = _('impact metrics')
        ordering = ['-date']