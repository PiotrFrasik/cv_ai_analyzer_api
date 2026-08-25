from django.urls import path
from .views import AnalysisDetailAPIView
urlpatterns = [
    path('analysis/<int:pk>/', AnalysisDetailAPIView.as_view(), name='analysis_detail'),
]