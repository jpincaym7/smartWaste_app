from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.security.models import User

# Create your models here.
class UserProfile(models.Model):
    """Perfil extendido del usuario con gamificación"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    points = models.PositiveIntegerField(_('points'), default=0)
    level = models.PositiveIntegerField(_('level'), default=1)
    total_detections = models.PositiveIntegerField(_('total detections'), default=0)
    badges = models.JSONField(_('badges'), default=list)
    preferences = models.JSONField(_('preferences'), default=dict)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f'{self.user.username} Profile'


class TrashReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_review', 'En Revisión'),
        ('verified', 'Verificado'),
        ('solved', 'Resuelto'),
        ('rejected', 'Rechazado'),
    ]

    SEVERITY_CHOICES = [
        (1, 'Baja'),
        (2, 'Media'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    image = models.ImageField(upload_to='trash_reports/')
    description = models.TextField()
    severity = models.IntegerField(choices=SEVERITY_CHOICES)
    is_recurring = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reporte #{self.id} - {self.get_status_display()}"

class ReportComment(models.Model):
    report = models.ForeignKey(TrashReport, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Badge(models.Model):
    """Insignias que pueden ganar los usuarios"""
    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.TextField(_('description'))
    icon = models.ImageField(_('icon'), upload_to='badges/')
    points_required = models.PositiveIntegerField(_('points required'))
    category = models.CharField(_('category'), max_length=50)
    
    class Meta:
        verbose_name = _('badge')
        verbose_name_plural = _('badges')
        ordering = ['points_required']

    def __str__(self):
        return self.name