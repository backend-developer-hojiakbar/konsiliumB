from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from collections import Counter

from .models import Analysis, CaseLibrary, CMETopic
from .serializers import (
    AnalysisSerializer,
    AnalysisListSerializer,
    CaseLibrarySerializer,
    CMETopicSerializer,
    DashboardStatsSerializer
)


class AnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for managing analyses with pagination and filtering."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return AnalysisListSerializer
        return AnalysisSerializer
    
    def get_queryset(self):
        """Return analyses for the current user with optional filtering."""
        queryset = Analysis.objects.filter(user=self.request.user).select_related('user')
        
        # Filter by completion status
        is_completed = self.request.query_params.get('is_completed')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        # Filter by patient_id
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Search by patient name (from patient_data JSON)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(patient_data__icontains=search)
        
        # Order by date (default: newest first)
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a new analysis with validation."""
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating analysis: {str(e)}", exc_info=True)
            raise
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark analysis as completed."""
        analysis = self.get_object()
        analysis.is_completed = True
        analysis.save()
        serializer = self.get_serializer(analysis)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def longitudinal(self, request, pk=None):
        """Get longitudinal view of patient analyses."""
        try:
            analysis = self.get_object()
            patient_analyses = Analysis.objects.filter(
                user=request.user,
                patient_id=analysis.patient_id
            ).select_related('user').only(
                'id', 'patient_id', 'patient_data', 'final_report', 
                'is_completed', 'created_at'
            ).order_by('created_at')
            serializer = AnalysisListSerializer(patient_analyses, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching longitudinal view: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch longitudinal view'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent analyses with optimized query."""
        try:
            analyses = self.get_queryset().only(
                'id', 'patient_id', 'patient_data', 'final_report', 
                'is_completed', 'created_at'
            )[:5]
            serializer = AnalysisListSerializer(analyses, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching recent analyses: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch recent analyses'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CaseLibraryViewSet(viewsets.ModelViewSet):
    """ViewSet for case library."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CaseLibrarySerializer
    
    def get_queryset(self):
        """Return case library entries."""
        # Users can see their own cases and public cases
        return CaseLibrary.objects.filter(
            Q(analysis__user=self.request.user) | Q(is_public=True)
        ).select_related('analysis', 'analysis__user')
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count."""
        case = self.get_object()
        case.view_count += 1
        case.save()
        return Response({'view_count': case.view_count})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search cases by tags or diagnosis with input validation and limits."""
        try:
            query = request.query_params.get('q', '').strip()
            
            # Input validation
            if not query:
                return Response([])
            
            # Limit query length to prevent abuse
            if len(query) > 200:
                return Response(
                    {'error': 'Search query too long. Maximum 200 characters allowed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Escape special characters for safety (Django ORM handles this, but extra safety)
            # Limit results to prevent large responses
            cases = self.get_queryset().filter(
                Q(tags__icontains=query) |
                Q(final_diagnosis__icontains=query) |
                Q(outcome__icontains=query)
            )[:50]  # Limit to 50 results
            
            serializer = self.get_serializer(cases, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in case library search: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Search failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CMETopicViewSet(viewsets.ModelViewSet):
    """ViewSet for CME topics."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CMETopicSerializer
    
    def get_queryset(self):
        """Return CME topics for the current user."""
        return CMETopic.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a new CME topic."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark CME topic as completed."""
        topic = self.get_object()
        topic.is_completed = True
        topic.save()
        serializer = self.get_serializer(topic)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_view(request):
    """Get dashboard statistics for the user. Optimized with efficient queries."""
    from django.db.models import Count, Prefetch
    from django.core.cache import cache
    
    user = request.user
    cache_key = f'dashboard_stats_{user.id}'
    
    # Try to get from cache (5 minute TTL)
    cached_stats = cache.get(cache_key)
    if cached_stats:
        serializer = DashboardStatsSerializer(cached_stats, context={'request': request})
        return Response(serializer.data)
    
    try:
        # Optimized query: only fetch necessary fields
        analyses = Analysis.objects.filter(user=user).only(
            'id', 'final_report', 'created_at', 'patient_id', 'patient_data'
        ).order_by('-created_at')
        
        total_count = analyses.count()
        
        # Efficiently calculate common diagnoses using database aggregation where possible
        # For JSON fields, we still need Python processing, but we limit the dataset
        all_diagnoses = []
        recent_analyses_list = []
        
        # Process only completed analyses with final reports (most recent 100 for efficiency)
        completed_analyses = analyses.filter(is_completed=True)[:100]
        
        for analysis in completed_analyses:
            # Extract diagnoses
            if analysis.final_report and isinstance(analysis.final_report, dict):
                consensus = analysis.final_report.get('consensusDiagnosis', [])
                if isinstance(consensus, list):
                    for dx in consensus:
                        if isinstance(dx, dict) and 'name' in dx:
                            all_diagnoses.append(dx['name'])
            
            # Collect recent analyses (limit to 5)
            if len(recent_analyses_list) < 5:
                recent_analyses_list.append(analysis)
        
        diagnosis_counts = Counter(all_diagnoses)
        common_diagnoses = [
            {'name': name, 'count': count}
            for name, count in diagnosis_counts.most_common(5)
        ]
        
        # Calculate feedback accuracy (placeholder - can be enhanced with actual feedback data)
        feedback_accuracy = 0.85
        
        # Get remaining recent analyses if needed
        if len(recent_analyses_list) < 5:
            remaining = list(analyses[:5 - len(recent_analyses_list)])
            recent_analyses_list.extend(remaining)
            recent_analyses_list = recent_analyses_list[:5]
        
        stats = {
            'total_analyses': total_count,
            'common_diagnoses': common_diagnoses,
            'feedback_accuracy': feedback_accuracy,
            'recent_analyses': recent_analyses_list,
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, stats, 300)
        
        serializer = DashboardStatsSerializer(stats, context={'request': request})
        return Response(serializer.data)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calculating dashboard stats for user {user.id}: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to calculate dashboard statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
