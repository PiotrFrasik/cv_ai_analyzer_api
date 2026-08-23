from django.urls import path 
from .views import UserRegisterAPIView, UserProfileAPIView, UserUpdateAPIView

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='register_users'),
    path('profile/', UserProfileAPIView.as_view(), name='profile_user'),
    path('update/', UserUpdateAPIView.as_view(), name='update_user'),
]