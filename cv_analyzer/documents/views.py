from rest_framework import generics
from .models import CV, JobOffer
from .serializers import CVCreateSerializer, JobOfferCreateSerializer, CVDetailSerializer, JobOfferDetailSerializer
from rest_framework.permissions import IsAuthenticated 

class CVCreateAPIView(generics.CreateAPIView):
    queryset = CV.objects.all()
    serializer_class = CVCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class JobOfferCreateAPIView(generics.CreateAPIView):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)