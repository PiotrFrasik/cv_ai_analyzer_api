from rest_framework import serializers
from .models import Analysis

class AnalysisDetailSerializer(serializers.ModelSerializer):
    """
    Displaying CV analysis results.
    """
    
    class Meta:
        model = Analysis
        fields = ['cv', 'job_offer', 'status', 'match_score', 'missing_skills']

    def to_representation(self, instance):
        return{
            'CV': instance.cv.owner.username,
            'job_offer': instance.job_offer.title,
            'status': instance.status,
            'match_score': instance.match_score,
            'missing_skills': instance.missing_skills,
        }