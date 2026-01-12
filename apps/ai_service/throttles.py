"""
Custom throttling classes for AI service endpoints.
"""
from rest_framework.throttling import UserRateThrottle


class AIServiceThrottle(UserRateThrottle):
    """
    Throttle class for AI service endpoints.
    More restrictive than general user throttling to prevent abuse.
    """
    scope = 'ai_service'
    
    def allow_request(self, request, view):
        """
        Implement the throttling logic.
        """
        if request.user and request.user.is_staff:
            # Allow staff users to bypass throttling
            return True
        return super().allow_request(request, view)
