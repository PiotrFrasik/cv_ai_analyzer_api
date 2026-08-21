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

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ['salary_min', 'salary_max', 'city', 'country']

class RecruiterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterProfile
        fields = ['department']

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Universal serializer for updating user data.
    Handles both candidate and recruiter profiles based on instance.role.
    """
    candidate_profile = CandidateProfileSerializer(required=False)
    recruiter_profile = RecruiterProfileSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'candidate_profile', 'recruiter_profile']

    def update(self, instance, validated_data):
        # Pop nested data — None if not sent in the request
        candidate_data = validated_data.pop('candidate_profile', None)
        recruiter_data = validated_data.pop('recruiter_profile', None)

        # Update base user fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        # Update only the profile matching the user's role
        if instance.role == CustomUser.Role.CANDIDATE and candidate_data:
            if hasattr(instance, 'candidate_profile'):  # Profile may not exist yet
                profile = instance.candidate_profile
                profile.salary_min = candidate_data.get('salary_min', profile.salary_min)
                profile.salary_max = candidate_data.get('salary_max', profile.salary_max)
                profile.city = candidate_data.get('city', profile.city)
                profile.country = candidate_data.get('country', profile.country)
                profile.save()

        elif instance.role == CustomUser.Role.RECRUITER and recruiter_data:
            if hasattr(instance, 'recruiter_profile'):  # Profile may not exist yet
                profile = instance.recruiter_profile
                profile.department = recruiter_data.get('department', profile.department)
                profile.save()
            
        return instance