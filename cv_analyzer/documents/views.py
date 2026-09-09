from rest_framework import generics
from rest_framework.permissions import IsAuthenticated 

from .models import CV, JobOffer
from .serializers import CVCreateSerializer, JobOfferCreateSerializer, CVDetailSerializer, JobOfferDetailSerializer
from .permissions import IsCVOwnerOrRecruiter
from .utils import extract_text_from_pdf, get_ai_analysis

from analysis.models import Analysis

class CVCreateAPIView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cv = serializer.save(owner=self.request.user)
        cv.raw_text = extract_text_from_pdf(cv.file)
        if hasattr(self.request.user, 'candidate_profile'):
            preferred_department = self.request.user.candidate_profile.preferred_department
            offers = JobOffer.objects.filter(owner__recruiter_profile__department=preferred_department)

            analyses = []
            for offer in offers:
                score, missing = get_ai_analysis(cv.raw_text, offer)
                analyses.append(Analysis(
                    cv=cv, 
                    job_offer=offer, 
                    match_score=score, 
                    missing_skills=missing,
                    status=Analysis.Status.PROCESSING
                ))
                
            Analysis.objects.bulk_create(analyses)
        cv.save()

class JobOfferCreateAPIView(generics.CreateAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        job_offer = serializer.save(owner=self.request.user)
        if hasattr(self.request.user, 'recruiter_profile'):
            department = self.request.user.recruiter_profile.department
            cvs = CV.objects.filter(owner__candidate_profile__preferred_department=department)

            analyses = []
            for cv in cvs:
                score, missing = get_ai_analysis(cv.raw_text, job_offer)
                analyses.append(Analysis(
                    cv=cv, 
                    job_offer=job_offer, 
                    match_score=score, 
                    missing_skills=missing,
                    status=Analysis.Status.PROCESSING
                ))
            
            Analysis.objects.bulk_create(analyses)
        job_offer.save()
        
class CVDetailAPIView(generics.RetrieveAPIView):
    queryset = CV.objects.all()
    serializer_class = CVDetailSerializer
    permission_classes = [IsAuthenticated, IsCVOwnerOrRecruiter]

class JobOfferDetailAPIView(generics.RetrieveAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferDetailSerializer
    permission_classes = [IsAuthenticated]