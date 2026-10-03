from django.urls import path
from .views import CVCreateAPIView, JobOfferCreateAPIView, CVDetailAPIView, JobOfferDetailAPIView
from .views import JobOfferListAPIView, CVListAPIView

urlpatterns = [
    path('cv/create/', CVCreateAPIView.as_view(), name='upload_cv'),
    path('job-offer/create/', JobOfferCreateAPIView.as_view(), name='create_job_offer'),

    path('cv/<int:pk>/', CVDetailAPIView.as_view(), name='cv_detail'),
    path('job-offer/<int:pk>/', JobOfferDetailAPIView.as_view(), name='job_offer_detail'),

    path('cv/', CVListAPIView.as_view(), name='list_cvs'),
    path('job-offer/', JobOfferListAPIView.as_view(), name='list_job_offers'),
]