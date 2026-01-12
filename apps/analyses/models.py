from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Analysis(models.Model):
    """Model for storing patient analysis records."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name=_('user')
    )
    
    patient_id = models.CharField(
        _('patient ID'),
        max_length=255,
        help_text=_('Used to link records for longitudinal view')
    )
    
    # Patient Data
    patient_data = models.JSONField(_('patient data'))
    
    # Analysis Results
    debate_history = models.JSONField(_('debate history'), default=list)
    final_report = models.JSONField(_('final report'), null=True, blank=True)
    differential_diagnoses = models.JSONField(_('differential diagnoses'), default=list)
    
    # Metadata
    selected_specialists = models.JSONField(_('selected specialists'), default=list)
    follow_up_history = models.JSONField(_('follow-up history'), default=list)
    detected_medications = models.JSONField(_('detected medications'), null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(_('is completed'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('analysis')
        verbose_name_plural = _('analyses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['patient_id']),
        ]
    
    def __str__(self):
        return f"Analysis #{self.id} - {self.patient_id} ({self.created_at.date()})"
    
    def save(self, *args, **kwargs):
        """Override save to update user statistics."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.user.update_stats()


class CaseLibrary(models.Model):
    """Model for anonymized cases in the case library."""
    
    analysis = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        related_name='case_library_entry',
        verbose_name=_('analysis')
    )
    
    tags = models.JSONField(_('tags'), default=list)
    final_diagnosis = models.TextField(_('final diagnosis'))
    outcome = models.TextField(_('outcome'), blank=True)
    
    # Privacy
    is_anonymous = models.BooleanField(_('is anonymous'), default=True)
    is_public = models.BooleanField(_('is public'), default=False)
    
    # Statistics
    view_count = models.IntegerField(_('view count'), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('case library entry')
        verbose_name_plural = _('case library entries')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Case #{self.id} - {self.final_diagnosis[:50]}"


class CMETopic(models.Model):
    """Model for Continuing Medical Education topics."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cme_topics',
        verbose_name=_('user')
    )
    
    topic = models.CharField(_('topic'), max_length=500)
    relevance = models.TextField(_('relevance'))
    
    # Status
    is_completed = models.BooleanField(_('is completed'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('CME topic')
        verbose_name_plural = _('CME topics')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic} - {self.user.name}"
