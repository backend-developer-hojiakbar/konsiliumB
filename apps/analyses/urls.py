from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'analyses'

router = DefaultRouter()
# Register nested viewsets first
router.register(r'case-library', views.CaseLibraryViewSet, basename='case-library')
router.register(r'cme-topics', views.CMETopicViewSet, basename='cme-topic')
# Register main viewset last to avoid URL conflicts
router.register(r'', views.AnalysisViewSet, basename='analysis')

urlpatterns = [
    path('dashboard-stats/', views.dashboard_stats_view, name='dashboard-stats'),
    path('', include(router.urls)),
]
