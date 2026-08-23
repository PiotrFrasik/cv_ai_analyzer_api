from rest_framework import generics
from .models import CustomUser
from .serializers import RegisterSerializer, UserProfileSerializer, UserUpdateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated 

class UserRegisterAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserProfileAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Override to return the currently authenticated user instead of a URL lookup
        return self.request.user

class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Override to return the currently authenticated user instead of a URL lookup
        return self.request.user
