from django.urls import path
from .views import AnalysisDetailAPIView, AnalysisListAPIVIew
urlpatterns = [
    path('analysis/<int:pk>/', AnalysisDetailAPIView.as_view(), name='analysis_detail'),
    path('analysis', AnalysisListAPIVIew.as_view(), name='analysis_list'),
]