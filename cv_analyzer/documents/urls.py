from django.urls import path
from .views import CVCreateAPIView, JobOfferCreateAPIView, CVDetailAPIView, JobOfferDetailAPIView

urlpatterns = [
    path('cv/create/', CVCreateAPIView.as_view(), name='upload_cv'),
    path('job_offer/create/', JobOfferCreateAPIView.as_view(), name='create_job_offer'),

    path('cv/<int:pk>/', CVDetailAPIView.as_view(), name='cv_detail'),
    path('job_offer/<int:pk>/', JobOfferDetailAPIView.as_view(), name='job_offer_detail'),
]