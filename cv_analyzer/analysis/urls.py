from django.urls import path
from .views import AnalysisDetailAPIView, AnalysisListAPIVIew
urlpatterns = [
    path('<int:pk>/', AnalysisDetailAPIView.as_view(), name='analysis_detail'),
    path('', AnalysisListAPIVIew.as_view(), name='analysis_list'),
]