from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

from apps.security.managers import CustomUserManager

class User(AbstractUser):
    """
    Custom User Model for the recycling app.
    Uses email as the unique identifier instead of username.
    """
    # Override username to make it optional and email as main identifier
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )
    email = models.EmailField(_('email address'), unique=True)
    
    # Additional fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        blank=True,
        validators=[MinLengthValidator(10)]
    )
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    avatar = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True, 
        help_text=_('A profile picture up to 5MB')
    )
    bio = models.TextField(_('biography'), max_length=500, blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    
    # Privacy and notifications settings
    privacy_settings = models.JSONField(
        _('privacy settings'),
        default=dict,
        help_text=_('User privacy preferences')
    )
    notification_settings = models.JSONField(
        _('notification settings'),
        default=dict,
        help_text=_('User notification preferences')
    )
    
    # Account status and security
    last_password_change = models.DateTimeField(
        _('last password change'),
        default=timezone.now
    )
    account_verified = models.BooleanField(_('account verified'), default=False)
    two_factor_enabled = models.BooleanField(
        _('two factor authentication enabled'),
        default=False
    )
    
    # Activity tracking
    last_login_ip = models.GenericIPAddressField(
        _('last login IP'),
        null=True,
        blank=True
    )
    login_count = models.PositiveIntegerField(_('login count'), default=0)
    
    # Use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Use custom manager
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def clean(self):
        super().clean()
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError({
                'date_of_birth': _('Date of birth cannot be in the future')
            })
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    @property
    def age(self):
        """Calculate user's age."""
        if self.date_of_birth:
            today = timezone.now().date()
            return (today.year - self.date_of_birth.year -
                   ((today.month, today.day) <
                    (self.date_of_birth.month, self.date_of_birth.day)))
        return None
    
    def increment_login_count(self, ip_address=None):
        """Increment login count and update last login IP."""
        self.login_count += 1
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=['login_count', 'last_login_ip'])
    
    def update_password(self, password):
        """Update user password and record the change time."""
        self.set_password(password)
        self.last_password_change = timezone.now()
        self.save(update_fields=['password', 'last_password_change'])
    
    def get_impact_metrics(self):
        """Get user's environmental impact metrics."""
        return self.impact_metrics.all()
    
    def get_total_points(self):
        """Get total points from user profile."""
        return self.profile.points if hasattr(self, 'profile') else 0
    
    def get_active_badges(self):
        """Get user's earned badges."""
        return self.profile.badges if hasattr(self, 'profile') else []