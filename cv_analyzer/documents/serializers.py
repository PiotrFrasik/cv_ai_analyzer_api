from rest_framework import serializers
from .models import CV, JobOffer

class CVCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['file']

    def validate(self, data):
        request = self.context.get('request')
        if CV.objects.filter(owner=request.user).exists():
            raise serializers.ValidationError("You already have a CV uploaded.")
        return data


class JobOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = ['raw_text','title', 'skills']

class CVDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['owner', 'uploaded_at', 'status']

class JobOfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model= JobOffer
        fields = ['owner', 'title', 'created_at', 'skills']