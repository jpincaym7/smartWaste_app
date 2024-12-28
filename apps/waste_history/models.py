import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.waste.models import WasteCategory

# Create your models here.
class WasteDetection(models.Model):
    """Registro de detecciones de residuos"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waste_detections',
        verbose_name=_('user')
    )
    category = models.ForeignKey(
        WasteCategory,
        on_delete=models.PROTECT,
        related_name='detections',
        verbose_name=_('category')
    )
    image = models.ImageField(_('image'), upload_to='detections/')
    confidence_score = models.FloatField(
        _('confidence score'),
        validators=[MinValueValidator(0.0)],
        help_text=_('ML model confidence score for the detection')
    )
    location_latitude = models.DecimalField(
        _('latitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    location_longitude = models.DecimalField(
        _('longitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('waste detection')
        verbose_name_plural = _('waste detections')
        ordering = ['-created_at']