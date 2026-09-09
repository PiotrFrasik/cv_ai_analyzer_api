from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CandidateProfile, RecruiterProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'role', 'is_staff']
    search_fields = ['username', 'email', 'phone_number', 'role']
    fieldsets = UserAdmin.fieldsets + (('Additional Info', {'fields': ('phone_number', 'role')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Additional Info', {'fields': ('phone_number', 'role')}),)
   
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'salary_min', 'salary_max', 'city', 'country']
    search_fields = ['user__username', 'city', 'country']

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    search_fields = ['user__username', 'department']