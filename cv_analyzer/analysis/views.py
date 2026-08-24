from rest_framework import generics
from rest_framework.permissions import IsAuthenticated 

from .models import Analysis
from .serializers import AnalysisDetailSerializer
from .permissions import IsRecruiterOrCVOwner

class AnalysisDetailAPIView(generics.RetrieveAPIView):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisDetailSerializer
    permission_classes = [IsAuthenticated, IsRecruiterOrCVOwner]
