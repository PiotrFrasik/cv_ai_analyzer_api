from rest_framework import generics
from rest_framework.permissions import IsAuthenticated 

from .models import CV, JobOffer
from .serializers import CVCreateSerializer, JobOfferCreateSerializer, CVDetailSerializer, JobOfferDetailSerializer
from .permissions import IsCVOwnerOrRecruiter
from .utils import extract_text_from_pdf

from analysis.models import Analysis
from analysis.tasks import run_ai_analysis
class CVCreateAPIView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cv = serializer.save(owner=self.request.user)
        cv.raw_text = extract_text_from_pdf(cv.file)
        cv.status = CV.Status.PROCESSED
        cv.save()
        
        if hasattr(self.request.user, 'candidate_profile'):
            preferred_department = self.request.user.candidate_profile.preferred_department
            offers = JobOffer.objects.filter(owner__recruiter_profile__department=preferred_department)
            for offer in offers:
                analysis = Analysis.objects.create(
                    cv=cv, 
                    job_offer=offer, 
                    status=Analysis.Status.PROCESSING
                )
                run_ai_analysis.delay(analysis.id)
                
class JobOfferCreateAPIView(generics.CreateAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        job_offer = serializer.save(owner=self.request.user)
        job_offer.save()

        if hasattr(self.request.user, 'recruiter_profile'):
            department = self.request.user.recruiter_profile.department
            cvs = CV.objects.filter(owner__candidate_profile__preferred_department=department)

            for cv in cvs:
                analysis = Analysis.objects.create(
                    cv=cv, 
                    job_offer=job_offer, 
                    status=Analysis.Status.PROCESSING
                )
                run_ai_analysis.delay(analysis.id)
        
class CVDetailAPIView(generics.RetrieveAPIView):
    queryset = CV.objects.all()
    serializer_class = CVDetailSerializer
    permission_classes = [IsAuthenticated, IsCVOwnerOrRecruiter]

class JobOfferDetailAPIView(generics.RetrieveAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferDetailSerializer
    permission_classes = [IsAuthenticated]