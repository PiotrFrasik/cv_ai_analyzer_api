from django.contrib import admin
from .models import Analysis

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['cv', 'job_offer', 'status', 'match_score']
    search_fields = ['cv__owner__username', 'job_offer__title']

