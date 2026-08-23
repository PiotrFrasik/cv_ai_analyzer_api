from django.urls import path
from .views import CVCreateAPIView, JobOfferCreateAPIView

urlpatterns = [
    path('cv/create/', CVCreateAPIView.as_view(), name='upload_cv'),
    path('job_offer/create/', JobOfferCreateAPIView.as_view(), name='create_job_offer'),
]