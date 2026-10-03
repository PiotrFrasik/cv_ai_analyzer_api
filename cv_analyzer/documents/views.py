from rest_framework import generics
from rest_framework.permissions import IsAuthenticated 
from rest_framework.throttling import UserRateThrottle

from .models import CV, JobOffer
from .serializers import CVCreateSerializer, JobOfferCreateSerializer, CVDetailSerializer, JobOfferDetailSerializer
from .permissions import IsCVOwnerOrRecruiter, IsOwner
from .utils import extract_text_from_pdf

from analysis.models import Analysis
from analysis.tasks import run_ai_analysis

class CVThrottle(UserRateThrottle):
    """Rate throttle for CV endpoints. Scope maps to DEFAULT_THROTTLE_RATES['cv']."""
    scope = 'cv'

class JobOfferThrottle(UserRateThrottle):
    """Rate throttle for JobOffer endpoints. Scope maps to DEFAULT_THROTTLE_RATES['job_offer']."""
    scope = 'job_offer'

class CVCreateAPIView(generics.CreateAPIView):
    """
    Create a new CV. Replaces any existing CV for the user.
    Extracts raw text from PDF and triggers AI analysis tasks for matching job offers.
    """
    queryset = CV.objects.all()
    serializer_class = CVCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CVThrottle]

    def perform_create(self, serializer):
        old_cv = CV.objects.filter(owner=self.request.user).first()
        if old_cv:
            old_cv.delete()

        cv = serializer.save(owner=self.request.user)
        cv.raw_text = extract_text_from_pdf(cv.file)
        cv.status = CV.Status.PROCESSED
        cv.save()
        
        if hasattr(self.request.user, 'candidate_profile'):
            preferred_department = self.request.user.candidate_profile.preferred_department
            offers = JobOffer.objects.filter(owner__recruiter_profile__department=preferred_department)
            for offer in offers:
                analysis, created = Analysis.objects.get_or_create(
                    cv=cv, 
                    job_offer=offer, 
                    defaults={'status': Analysis.Status.PROCESSING}
                )
                if created:
                    run_ai_analysis.delay(analysis.id)
                
class JobOfferCreateAPIView(generics.CreateAPIView):
    """
    Create a new job offer and trigger AI analysis tasks for matching candidate CVs.
    """
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [JobOfferThrottle]

    def perform_create(self, serializer):
        job_offer = serializer.save(owner=self.request.user)

        if hasattr(self.request.user, 'recruiter_profile'):
            department = self.request.user.recruiter_profile.department
            cvs = CV.objects.filter(owner__candidate_profile__preferred_department=department)

            for cv in cvs:
                analysis, created = Analysis.objects.get_or_create(
                    cv=cv, 
                    job_offer=job_offer, 
                    defaults={'status': Analysis.Status.PROCESSING}
                )
                if created:
                    run_ai_analysis.delay(analysis.id)

class CVListAPIView(generics.ListAPIView):
    """List CVs belonging to the authenticated user."""
    queryset = CV.objects.all()
    serializer_class = CVDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CV.objects.filter(owner=user)

class JobOfferListAPIView(generics.ListAPIView):
    """List job offers belonging to the authenticated user."""
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return JobOffer.objects.filter(owner=user)

class CVDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a CV.
    GET allows owner or recruiter; PUT/PATCH/DELETE restricted to owner only.
    On update, replaces the file, re-extracts text, and re-runs AI analysis tasks.
    """
    queryset = CV.objects.all()

    def get_throttles(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [CVThrottle()]
        return super().get_throttles()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsCVOwnerOrRecruiter()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CVCreateSerializer
        return CVDetailSerializer

    def perform_update(self, serializer):
        # Delete old cv
        serializer.instance.file.delete(save=False)

        cv = serializer.save()
        cv.raw_text = extract_text_from_pdf(cv.file)
        cv.status = CV.Status.PROCESSED
        cv.save()

        cv.analyses.all().delete()

        if hasattr(self.request.user, 'candidate_profile'):
            preferred_department = self.request.user.candidate_profile.preferred_department
            offers = JobOffer.objects.filter(owner__recruiter_profile__department=preferred_department)
            for offer in offers:
                analysis, created = Analysis.objects.get_or_create(
                    cv=cv,
                    job_offer=offer,
                    defaults={'status': Analysis.Status.PROCESSING}
                )
                if created:
                    run_ai_analysis.delay(analysis.id)

class JobOfferDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a job offer.
    PUT/PATCH/DELETE restricted to owner only.
    On update, drops existing analyses and re-runs AI tasks for matching CVs.
    """
    queryset = JobOffer.objects.all()

    def get_throttles(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [JobOfferThrottle()]
        return super().get_throttles()


    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobOfferCreateSerializer
        return JobOfferDetailSerializer

    def perform_update(self, serializer):
        job_offer = serializer.save()

        job_offer.analyses.all().delete()

        if hasattr(self.request.user, 'recruiter_profile'):
            department = self.request.user.recruiter_profile.department
            cvs = CV.objects.filter(owner__candidate_profile__preferred_department=department)
            for cv in cvs:
                analysis, created = Analysis.objects.get_or_create(
                    cv=cv,
                    job_offer=job_offer,
                    defaults={'status': Analysis.Status.PROCESSING}
                )
                if created:
                    run_ai_analysis.delay(analysis.id)