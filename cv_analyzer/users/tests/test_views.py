from rest_framework.test import APITestCase
from users.models import CustomUser, RecruiterProfile
from rest_framework import status
from django.urls import reverse


class UserRegisterAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("register_users")
        # Base valid payload reused across tests
        self.data = {
            "username": "john",
            "password": "PAAAassword!2@",
            "email": "example@example.com",
            "phone_number": "1234567879"
        }

    def test_register_with_weak_password_returns_400(self):
        # Password without special character should fail validation
        data = {**self.data, "password": "password"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_with_valid_data_returns_201(self):
        # Valid payload should create a user successfully
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_without_phone_number_returns_400(self):
        # phone_number is required — omitting it should fail
        data = {**self.data}
        data.pop("phone_number")
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_username_returns_400(self):
        # username is required — omitting it should fail
        data = {**self.data}
        data.pop("username")
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username_returns_400(self):
        # Registering twice with the same username should fail
        self.client.post(self.url, self.data, format='json')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_phone_number_returns_400(self):
        # phone_number has unique=True — second registration with same number should fail
        self.client.post(self.url, self.data, format='json')
        data = {**self.data, "username": "jane"}  # different username, same phone
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserProfileAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("profile_user")
        # Create a user directly in DB (bypasses registration endpoint)
        self.user = CustomUser.objects.create_user(
            username="john",
            password="PAAAassword!2@",
            email="example@example.com",
            phone_number="1234567879",
            role=CustomUser.Role.CANDIDATE
        )

    def test_profile_unauthenticated_returns_401(self):
        # No credentials — should be rejected
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_authenticated_returns_200(self):
        # Authenticated user should receive their profile data
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserUpdateAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("update_user")
        self.user = CustomUser.objects.create_user(
            username="john",
            password="PAAAassword!2@",
            email="example@example.com",
            phone_number="1234567879",
            role=CustomUser.Role.CANDIDATE
        )

    def test_update_unauthenticated_returns_401(self):
        # No credentials — PATCH should be rejected
        response = self.client.patch(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_authenticated_returns_200(self):
        # Authenticated user should be able to update their own data
        self.client.force_authenticate(user=self.user)
        data = {
            "username": "kate",
            "password": "PAAAassword!2@",
            "email": "example@example.com",
            "phone_number": "1234567879"
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the username was actually changed
        self.assertEqual(response.data['username'], 'kate')

    def test_candidate_cannot_update_recruiter_profile(self):
        # Candidate sending recruiter_profile data — should be silently ignored
        self.client.force_authenticate(user=self.user)
        data = {
            "username": "kate",
            "password": "PAAAassword!2@",
            "email": "example@example.com",
            "phone_number": "1234567879",
            "recruiter_profile": {"department": "it"},
        }
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(hasattr(self.user, 'recruiter_profile'))

    def test_recruiter_can_update_recruiter_profile(self):
        # Recruiter should be able to update their own department
        recruiter = CustomUser.objects.create_user(
            username="recruiter1",
            password="PAAAassword!2@",
            email="recruiter@example.com",
            phone_number="9876543210",
            role=CustomUser.Role.RECRUITER
        )
        RecruiterProfile.objects.create(user=recruiter, department="it")
        self.client.force_authenticate(user=recruiter)
        data = {"recruiter_profile": {"department": "marketing"}}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recruiter.recruiter_profile.refresh_from_db()
        self.assertEqual(recruiter.recruiter_profile.department, "marketing")
