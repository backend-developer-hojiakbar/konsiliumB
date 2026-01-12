from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication."""
    
    def create_user(self, phone, password=None, **extra_fields):
        """Create and save a regular user with the given phone and password."""
        if not phone:
            raise ValueError(_('The Phone field must be set'))
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        """Create and save a superuser with the given phone and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """Custom user model using phone as the unique identifier."""
    
    username = None
    phone = models.CharField(_('phone number'), max_length=20, unique=True)
    name = models.CharField(_('full name'), max_length=255)
    email = models.EmailField(_('email address'), blank=True, null=True)
    
    # Statistics
    total_analyses = models.IntegerField(_('total analyses'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.phone})"
    
    def update_stats(self):
        """Update user statistics."""
        from apps.analyses.models import Analysis
        self.total_analyses = Analysis.objects.filter(user=self).count()
        self.save(update_fields=['total_analyses'])
