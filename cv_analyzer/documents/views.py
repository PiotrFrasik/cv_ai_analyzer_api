from rest_framework import generics
from rest_framework.permissions import IsAuthenticated 

from .models import CV, JobOffer
from analysis.models import Analysis
from .serializers import CVCreateSerializer, JobOfferCreateSerializer, CVDetailSerializer, JobOfferDetailSerializer
from .permissions import IsCVOwnerOrRecruiter

class CVCreateAPIView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cv = serializer.save(owner=self.request.user)
        if hasattr(self.request.user, 'candidate_profile'):
            preferred_department = self.request.user.candidate_profile.preferred_department
            offers = JobOffer.objects.filter(owner__recruiter_profile__department=preferred_department)
            analyses = [Analysis(cv=cv, job_offer=offer) for offer in offers]
            Analysis.objects.bulk_create(analyses)

class JobOfferCreateAPIView(generics.CreateAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        job_offer = serializer.save(owner=self.request.user)
        if hasattr(self.request.user, 'recruiter_profile'):
            department = self.request.user.recruiter_profile.department
            cvs = CV.objects.filter(owner__candidate_profile__preferred_department=department)
            analyses = [Analysis(cv=cv, job_offer=job_offer) for cv in cvs]
            Analysis.objects.bulk_create(analyses)

class CVDetailAPIView(generics.RetrieveAPIView):
    queryset = CV.objects.all()
    serializer_class = CVDetailSerializer
    permission_classes = [IsAuthenticated, IsCVOwnerOrRecruiter]

class JobOfferDetailAPIView(generics.RetrieveAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferDetailSerializer
    permission_classes = [IsAuthenticated]