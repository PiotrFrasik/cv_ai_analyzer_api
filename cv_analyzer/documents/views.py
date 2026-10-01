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
    scope = 'cv'

class JobOfferThrottle(UserRateThrottle):
    scope = 'job_offer'

class CVCreateAPIView(generics.CreateAPIView):
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
    throttle_classes = [JobOfferThrottle]

    def perform_create(self, serializer):
        job_offer = serializer.save(owner=self.request.user)

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

class CVListAPIView(generics.ListAPIView):
    queryset = CV.objects.all()
    serializer_class = CVDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CV.objects.filter(owner=user)

class JobOfferListAPIView(generics.ListAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return JobOffer.objects.filter(owner=user)

class CVDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
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

        cv.analysis_cvs.all().delete()

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

class JobOfferDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
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

        job_offer.analysis_job_offers.all().delete()

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