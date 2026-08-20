from django.contrib import admin
from .models import CustomUser, CandidateProfile, RecruiterProfile

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'role']
    search_fields = ['role']

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'salary_min', 'salary_max', 'city', 'country']
    search_fields = ['user__username', 'city', 'country']

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    search_fields = ['user__username', 'department']