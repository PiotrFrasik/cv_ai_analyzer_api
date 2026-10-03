from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from .models import CV, JobOffer

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_file_size(file):
    if file.size > MAX_FILE_SIZE_BYTES:
        raise serializers.ValidationError("File size must not exceed 5 MB.")
    return file


class CVCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            validate_file_size
        ]
    )

    class Meta:
        model = CV
        fields = ['file']

class JobOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = ['raw_text','title', 'skills']

class CVDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = ['id', 'owner', 'uploaded_at', 'status']

class JobOfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model= JobOffer
        fields = ['id', 'owner', 'title', 'created_at', 'skills']