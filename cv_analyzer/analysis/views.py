from rest_framework import generics
from rest_framework.permissions import IsAuthenticated 
from django.db.models import Q

from .models import Analysis
from .serializers import AnalysisDetailSerializer
from .permissions import IsRecruiterOrCVOwner

class AnalysisDetailAPIView(generics.RetrieveAPIView):
    """Retrieves a single analysis instance for the CV owner or the associated recruiter."""
    queryset = Analysis.objects.all()
    serializer_class = AnalysisDetailSerializer
    permission_classes = [IsAuthenticated, IsRecruiterOrCVOwner]

class AnalysisListAPIVIew(generics.ListAPIView):
    """Lists all analyses where the authenticated user is either the CV owner or the job offer owner."""
    serializer_class = AnalysisDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Analysis.objects.filter(Q(cv__owner=user) | Q(job_offer__owner=user))