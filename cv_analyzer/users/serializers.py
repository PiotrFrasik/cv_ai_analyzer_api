from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser, CandidateProfile, RecruiterProfile

class RegisterSerializer(serializers.ModelSerializer):
    """
    User registration. Creates a CustomUser with a hashed password
    and assigns the default role of 'candidate'.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as err:
            raise serializers.ValidationError(err.messages)

        special_characters = "!@#$%^&*()_+-="
        has_special = any(char in special_characters for char in value)
        if not has_special:
            raise serializers.ValidationError("Password must contain at least one special character.")
            
        return value 

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

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for displaying user profile data.
    """
    candidate_profile = CandidateProfileSerializer(read_only=True)
    recruiter_profile = RecruiterProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'candidate_profile', 'recruiter_profile']

    def to_representation(self, instance):

        if instance.role == CustomUser.Role.CANDIDATE:
            return {
                'username': instance.username,
                'email': instance.email,
                'phone_number': instance.phone_number,
                'candidate_profile': CandidateProfileSerializer(instance.candidate_profile).data 
                if hasattr(instance, 'candidate_profile') else None
            }


        elif instance.role == CustomUser.Role.RECRUITER:
            return {
                'username': instance.username,
                'email': instance.email,
                'phone_number': instance.phone_number,
                'recruiter_profile': RecruiterProfileSerializer(instance.recruiter_profile).data
                if hasattr(instance, 'recruiter_profile') else None
            }

        return super().to_representation(instance)