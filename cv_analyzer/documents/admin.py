from django.contrib import admin
from .models import CV, JobOffer

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ['owner', 'file', 'uploaded_at']
    search_fields = ['owner__username', 'status']

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'created_at']
    search_fields = ['owner__username', 'title', 'created_at']

