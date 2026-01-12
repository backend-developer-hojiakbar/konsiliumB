from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .gemini_service import gemini_service
from .throttles import AIServiceThrottle
from .serializers import (
    ClarifyingQuestionsRequestSerializer,
    ClarifyingQuestionsResponseSerializer,
    SpecialistRecommendationRequestSerializer,
    SpecialistRecommendationResponseSerializer,
    InitialDiagnosesRequestSerializer,
    InitialDiagnosesResponseSerializer,
    FinalReportRequestSerializer,
    FinalReportSerializer,
    DrugInteractionRequestSerializer,
    DrugInteractionResponseSerializer,
    CMETopicRequestSerializer,
    CMETopicResponseSerializer,
)


@swagger_auto_schema(
    method='post',
    request_body=ClarifyingQuestionsRequestSerializer,
    responses={200: ClarifyingQuestionsResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIServiceThrottle])
def generate_clarifying_questions(request):
    """
    Generate clarifying questions based on patient data.
    Includes comprehensive error handling and input validation.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    serializer = ClarifyingQuestionsRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        patient_data = serializer.validated_data['patient_data']
        language = serializer.validated_data.get('language', 'en')
        
        # Validate language parameter
        valid_languages = ['en', 'uz-L', 'uz-C', 'ru']
        if language not in valid_languages:
            language = 'en'
        
        # Validate patient data structure (basic checks)
        if not isinstance(patient_data, dict):
            return Response(
                {'error': 'Invalid patient data format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        questions = gemini_service.generate_clarifying_questions(
            patient_data=patient_data,
            language=language
        )
        
        # Validate response
        if not isinstance(questions, list):
            logger.warning(f"Unexpected response format from Gemini service: {type(questions)}")
            questions = []
        
        return Response({'questions': questions[:10]})  # Limit to 10 questions max
    
    except ValueError as e:
        logger.warning(f"Validation error in generate_clarifying_questions: {str(e)}")
        return Response(
            {'error': 'Invalid input data. Please check your request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error generating clarifying questions: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to generate clarifying questions. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    request_body=SpecialistRecommendationRequestSerializer,
    responses={200: SpecialistRecommendationResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIServiceThrottle])
def recommend_specialists(request):
    """
    Recommend specialists based on patient data.
    """
    serializer = SpecialistRecommendationRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        patient_data = serializer.validated_data['patient_data']
        language = serializer.validated_data.get('language', 'en')
        
        recommendations = gemini_service.recommend_specialists(
            patient_data=patient_data,
            language=language
        )
        
        return Response(recommendations)
    
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Validation error: {str(e)}")
        return Response(
            {'error': 'Invalid input data. Please check your request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in AI service: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Service temporarily unavailable. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    request_body=InitialDiagnosesRequestSerializer,
    responses={200: InitialDiagnosesResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIServiceThrottle])
def generate_initial_diagnoses(request):
    """
    Generate initial differential diagnoses.
    """
    serializer = InitialDiagnosesRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        patient_data = serializer.validated_data['patient_data']
        language = serializer.validated_data.get('language', 'en')
        
        diagnoses = gemini_service.generate_initial_diagnoses(
            patient_data=patient_data,
            language=language
        )
        
        return Response({'diagnoses': diagnoses})
    
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Validation error: {str(e)}")
        return Response(
            {'error': 'Invalid input data. Please check your request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in AI service: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Service temporarily unavailable. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    request_body=FinalReportRequestSerializer,
    responses={200: FinalReportSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIServiceThrottle])
def generate_final_report(request):
    """
    Generate final medical report.
    """
    serializer = FinalReportRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        patient_data = serializer.validated_data['patient_data']
        debate_history = serializer.validated_data['debate_history']
        diagnoses = serializer.validated_data['diagnoses']
        language = serializer.validated_data.get('language', 'en')
        
        report = gemini_service.generate_final_report(
            patient_data=patient_data,
            debate_history=debate_history,
            diagnoses=diagnoses,
            language=language
        )
        
        return Response(report)
    
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Validation error: {str(e)}")
        return Response(
            {'error': 'Invalid input data. Please check your request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in AI service: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Service temporarily unavailable. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    request_body=DrugInteractionRequestSerializer,
    responses={200: DrugInteractionResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIServiceThrottle])
def check_drug_interactions(request):
    """
    Check for drug interactions.
    """
    serializer = DrugInteractionRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        medications = serializer.validated_data['medications']
        language = serializer.validated_data.get('language', 'en')
        
        interactions = gemini_service.check_drug_interactions(
            medications=medications,
            language=language
        )
        
        return Response({'interactions': interactions})
    
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Validation error: {str(e)}")
        return Response(
            {'error': 'Invalid input data. Please check your request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in AI service: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Service temporarily unavailable. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    request_body=CMETopicRequestSerializer,
    responses={200: CMETopicResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIServiceThrottle])
def suggest_cme_topics(request):
    """
    Suggest CME topics based on user's case history.
    """
    serializer = CMETopicRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        analyses = serializer.validated_data['analyses']
        language = serializer.validated_data.get('language', 'en')
        
        topics = gemini_service.suggest_cme_topics(
            analyses=analyses,
            language=language
        )
        
        return Response({'topics': topics})
    
    except ValueError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Validation error: {str(e)}")
        return Response(
            {'error': 'Invalid input data. Please check your request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in AI service: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Service temporarily unavailable. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
