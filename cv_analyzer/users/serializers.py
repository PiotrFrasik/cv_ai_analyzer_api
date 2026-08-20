from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser, CandidateProfile, RecruiterProfile

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data) # Create new CustomUser object with validate data
        user.password = make_password(password)
        user.role = CustomUser.Role.CANDIDATE # Default role is candidate; an admin can change it to recruiter
        user.save()
        return user
