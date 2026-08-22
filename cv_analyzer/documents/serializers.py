from rest_framework import serializers
from .models import CV, JobOffer

class CVCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['file']

class JobOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = ['raw_text','title']

class CVDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['owner', 'uploaded_at', 'status']

class JobOfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model= JobOffer
        fields = ['owner', 'title', 'created_at']