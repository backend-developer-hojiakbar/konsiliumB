from rest_framework import serializers
from .models import Analysis, CaseLibrary, CMETopic
from .validators import validate_patient_id, validate_json_structure, sanitize_text_input


class AnalysisSerializer(serializers.ModelSerializer):
    """Serializer for Analysis model."""
    
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id',
            'user',
            'user_name',
            'patient_id',
            'patient_data',
            'debate_history',
            'final_report',
            'differential_diagnoses',
            'selected_specialists',
            'follow_up_history',
            'detected_medications',
            'is_completed',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def validate_patient_id(self, value):
        """Validate patient ID."""
        validate_patient_id(value)
        return value
    
    def validate_patient_data(self, value):
        """Validate patient data structure."""
        validate_json_structure(value, max_size_mb=5)
        return value
    
    def validate_debate_history(self, value):
        """Validate debate history."""
        if not isinstance(value, list):
            raise serializers.ValidationError('Debate history must be a list.')
        if len(value) > 1000:  # Reasonable limit
            raise serializers.ValidationError('Debate history is too large.')
        return value
    
    def create(self, validated_data):
        """Create a new analysis with validation."""
        validated_data['user'] = self.context['request'].user
        # Always mark newly created analyses as completed
        validated_data['is_completed'] = True
        return super().create(validated_data)


class AnalysisListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing analyses."""
    
    user_name = serializers.CharField(source='user.name', read_only=True)
    patient_name = serializers.SerializerMethodField()
    diagnosis_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Analysis
        fields = [
            'id',
            'user_name',
            'patient_id',
            'patient_name',
            'diagnosis_summary',
            'is_completed',
            'created_at',
        ]
    
    def get_patient_name(self, obj):
        """Get patient name from patient data."""
        patient_data = obj.patient_data
        if isinstance(patient_data, dict):
            first_name = patient_data.get('firstName', '')
            last_name = patient_data.get('lastName', '')
            return f"{first_name} {last_name}".strip()
        return "Unknown"
    
    def get_diagnosis_summary(self, obj):
        """Get summary of diagnoses."""
        if obj.final_report and isinstance(obj.final_report, dict):
            consensus = obj.final_report.get('consensusDiagnosis', [])
            if consensus:
                return consensus[0].get('name', 'No diagnosis') if isinstance(consensus, list) else 'No diagnosis'
        return "In progress"


class CaseLibrarySerializer(serializers.ModelSerializer):
    """Serializer for CaseLibrary model."""
    
    analysis_data = AnalysisListSerializer(source='analysis', read_only=True)
    
    class Meta:
        model = CaseLibrary
        fields = [
            'id',
            'analysis',
            'analysis_data',
            'tags',
            'final_diagnosis',
            'outcome',
            'is_anonymous',
            'is_public',
            'view_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('id', 'view_count', 'created_at', 'updated_at')


class CMETopicSerializer(serializers.ModelSerializer):
    """Serializer for CMETopic model."""
    
    class Meta:
        model = CMETopic
        fields = [
            'id',
            'user',
            'topic',
            'relevance',
            'is_completed',
            'created_at',
        ]
        read_only_fields = ('id', 'user', 'created_at')
    
    def create(self, validated_data):
        """Create a new CME topic."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    
    total_analyses = serializers.IntegerField()
    common_diagnoses = serializers.ListField(
        child=serializers.DictField()
    )
    feedback_accuracy = serializers.FloatField()
    recent_analyses = AnalysisListSerializer(many=True)
