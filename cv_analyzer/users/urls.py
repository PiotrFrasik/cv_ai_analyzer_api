from django.urls import path 
from .views import RegisterAPIView, UserProfileAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register_users'),
    path('profile/', UserProfileAPIView.as_view(), name='profile_user')
]