from rest_framework import serializers


class ClarifyingQuestionsRequestSerializer(serializers.Serializer):
    """Serializer for clarifying questions request."""
    patient_data = serializers.JSONField()
    language = serializers.CharField(default='en', max_length=10)
    
    def validate_language(self, value):
        """Validate language parameter."""
        valid_languages = ['en', 'uz-L', 'uz-C', 'ru']
        if value not in valid_languages:
            raise serializers.ValidationError(f'Invalid language. Must be one of: {", ".join(valid_languages)}')
        return value
    
    def validate_patient_data(self, value):
        """Validate patient data structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Patient data must be a dictionary.')
        return value


class ClarifyingQuestionsResponseSerializer(serializers.Serializer):
    """Serializer for clarifying questions response."""
    questions = serializers.ListField(child=serializers.CharField())


class SpecialistRecommendationRequestSerializer(serializers.Serializer):
    """Serializer for specialist recommendation request."""
    patient_data = serializers.JSONField()
    language = serializers.CharField(default='en', max_length=10)
    
    def validate_language(self, value):
        """Validate language parameter."""
        valid_languages = ['en', 'uz-L', 'uz-C', 'ru']
        if value not in valid_languages:
            raise serializers.ValidationError(f'Invalid language. Must be one of: {", ".join(valid_languages)}')
        return value
    
    def validate_patient_data(self, value):
        """Validate patient data structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Patient data must be a dictionary.')
        return value


class SpecialistRecommendationSerializer(serializers.Serializer):
    """Serializer for specialist recommendation."""
    specialty = serializers.CharField()
    reason = serializers.CharField()
    model = serializers.CharField(required=False)  # Optional, will be added by backend


class SpecialistRecommendationResponseSerializer(serializers.Serializer):
    """Serializer for specialist recommendation response."""
    recommendations = SpecialistRecommendationSerializer(many=True)


class DiagnosisSerializer(serializers.Serializer):
    """Serializer for diagnosis."""
    name = serializers.CharField()
    probability = serializers.FloatField()
    justification = serializers.CharField()
    evidenceLevel = serializers.CharField()


class InitialDiagnosesRequestSerializer(serializers.Serializer):
    """Serializer for initial diagnoses request."""
    patient_data = serializers.JSONField()
    language = serializers.CharField(default='en', max_length=10)
    
    def validate_language(self, value):
        """Validate language parameter."""
        valid_languages = ['en', 'uz-L', 'uz-C', 'ru']
        if value not in valid_languages:
            raise serializers.ValidationError(f'Invalid language. Must be one of: {", ".join(valid_languages)}')
        return value


class InitialDiagnosesResponseSerializer(serializers.Serializer):
    """Serializer for initial diagnoses response."""
    diagnoses = DiagnosisSerializer(many=True)


class FinalReportRequestSerializer(serializers.Serializer):
    """Serializer for final report request."""
    patient_data = serializers.JSONField()
    debate_history = serializers.ListField(child=serializers.JSONField())
    diagnoses = serializers.ListField(child=serializers.JSONField())
    language = serializers.CharField(default='en')


class MedicationRecommendationSerializer(serializers.Serializer):
    """Serializer for medication recommendation."""
    name = serializers.CharField()
    dosage = serializers.CharField()
    notes = serializers.CharField()


class RejectedHypothesisSerializer(serializers.Serializer):
    """Serializer for rejected hypothesis."""
    name = serializers.CharField()
    reason = serializers.CharField()


class FinalReportSerializer(serializers.Serializer):
    """Serializer for final report."""
    consensusDiagnosis = DiagnosisSerializer(many=True)
    rejectedHypotheses = RejectedHypothesisSerializer(many=True)
    recommendedTests = serializers.ListField(child=serializers.CharField())
    treatmentPlan = serializers.ListField(child=serializers.CharField())
    medicationRecommendations = MedicationRecommendationSerializer(many=True)
    unexpectedFindings = serializers.CharField()


class DrugInteractionRequestSerializer(serializers.Serializer):
    """Serializer for drug interaction request."""
    medications = serializers.ListField(child=serializers.CharField())
    language = serializers.CharField(default='en')


class DrugInteractionSerializer(serializers.Serializer):
    """Serializer for drug interaction."""
    interaction = serializers.CharField()
    severity = serializers.CharField()
    mechanism = serializers.CharField()
    management = serializers.CharField()


class DrugInteractionResponseSerializer(serializers.Serializer):
    """Serializer for drug interaction response."""
    interactions = DrugInteractionSerializer(many=True)


class CMETopicRequestSerializer(serializers.Serializer):
    """Serializer for CME topic request."""
    analyses = serializers.ListField(child=serializers.JSONField())
    language = serializers.CharField(default='en')


class CMETopicSerializer(serializers.Serializer):
    """Serializer for CME topic."""
    topic = serializers.CharField()
    relevance = serializers.CharField()


class CMETopicResponseSerializer(serializers.Serializer):
    """Serializer for CME topic response."""
    topics = CMETopicSerializer(many=True)
