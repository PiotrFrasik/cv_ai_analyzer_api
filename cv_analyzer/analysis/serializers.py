from rest_framework import serializers
from .models import Analysis

class AnalysisDetailSerializer(serializers.ModelSerializer):
    """
    Displaying CV analysis results.
    """
    cv_owner = serializers.CharField(source='cv.owner.username', read_only=True)
    job_offer = serializers.CharField(source='job_offer.title', read_only=True)

    class Meta:
        model = Analysis
        fields = ['cv_owner', 'job_offer', 'status', 'match_score', 'missing_skills']