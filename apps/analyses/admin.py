from django.contrib import admin
from .models import Analysis, CaseLibrary, CMETopic


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    """Admin interface for Analysis model."""
    
    list_display = ('id', 'user', 'patient_id', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('patient_id', 'user__name', 'user__phone')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(CaseLibrary)
class CaseLibraryAdmin(admin.ModelAdmin):
    """Admin interface for CaseLibrary model."""
    
    list_display = ('id', 'final_diagnosis', 'is_public', 'view_count', 'created_at')
    list_filter = ('is_public', 'is_anonymous', 'created_at')
    search_fields = ('final_diagnosis', 'outcome', 'tags')
    readonly_fields = ('view_count', 'created_at', 'updated_at')


@admin.register(CMETopic)
class CMETopicAdmin(admin.ModelAdmin):
    """Admin interface for CMETopic model."""
    
    list_display = ('id', 'user', 'topic', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('topic', 'relevance', 'user__name')
    readonly_fields = ('created_at',)
