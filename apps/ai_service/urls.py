from django.urls import path
from . import views

app_name = 'ai_service'

urlpatterns = [
    path('clarifying-questions/', views.generate_clarifying_questions, name='clarifying-questions'),
    path('recommend-specialists/', views.recommend_specialists, name='recommend-specialists'),
    path('initial-diagnoses/', views.generate_initial_diagnoses, name='initial-diagnoses'),
    path('final-report/', views.generate_final_report, name='final-report'),
    path('drug-interactions/', views.check_drug_interactions, name='drug-interactions'),
    path('cme-topics/', views.suggest_cme_topics, name='cme-topics'),
]
