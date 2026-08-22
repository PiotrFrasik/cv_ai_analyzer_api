from rest_framework import serializers
from .models import Analysis

class AnalysisDetailSerializer(serializers.ModelSerializer):
    """
    Displaying CV analysis results.
    """
    class Meta:
        model = Analysis
        fields = ['cv', 'job_offer', 'status', 'match_score']
