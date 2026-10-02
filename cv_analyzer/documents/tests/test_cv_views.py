import tempfile
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.models import Analysis
from documents.models import CV, JobOffer
from users.models import CustomUser


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CVCreateAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("upload_cv")

        self.candidate = CustomUser.objects.create_user(
            username="john",
            password="PAAAassword!2@",
            email="example@example.com",
            phone_number="1234567879",
            role=CustomUser.Role.CANDIDATE
        )

        self.fake_pdf = SimpleUploadedFile(
            "cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )

    @patch('documents.views.extract_text_from_pdf', return_value="mocked text")
    def test_create_cv_unauthenticated_returns_401(self, mock_extract):
        # No credentials — upload should be rejected
        response = self.client.post(self.url, {"file": self.fake_pdf}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('documents.views.extract_text_from_pdf', return_value="mocked text")
    def test_create_cv_authenticated_returns_201(self, mock_extract):
        # Valid PDF upload by authenticated user should create CV
        self.client.force_authenticate(user=self.candidate)
        response = self.client.post(self.url, {"file": self.fake_pdf}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cv_without_file_returns_400(self):
        # Missing file field should fail validation
        self.client.force_authenticate(user=self.candidate)
        response = self.client.post(self.url, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CVListAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("list_cvs")

        self.candidate = CustomUser.objects.create_user(
            username="john",
            password="PAAAassword!2@",
            email="example@example.com",
            phone_number="1234567879",
            role=CustomUser.Role.CANDIDATE
        )

        self.cv = CV.objects.create(owner=self.candidate, raw_text="test", status=CV.Status.PROCESSED)

    def test_list_cv_authenticated_returns_200(self):
        # Authenticated user should receive a list of their CVs
        self.client.force_authenticate(user=self.candidate)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cv_unauthenticated_returns_401(self):
        # No credentials — list should be rejected
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CVDetailAPITests(APITestCase):
    def setUp(self):
        self.candidate = CustomUser.objects.create_user(
            username="john",
            password="PAAAassword!2@",
            email="example@example.com",
            phone_number="1234567879",
            role=CustomUser.Role.CANDIDATE
        )

        self.recruiter = CustomUser.objects.create_user(
            username="kate",
            password="PAAAassword!2@",
            email="example@examp.com",
            phone_number="1234567878",
            role=CustomUser.Role.RECRUITER
        )

        self.job_offer = JobOffer.objects.create(
            owner=self.recruiter,
            title="Junior Python Developer",
            skills="Python, Django, DRF, SQL, Git",
            raw_text="We are looking for a motivated Junior Python Developer."
        )

        self.cv = CV.objects.create(owner=self.candidate, raw_text="test", status=CV.Status.PROCESSED)
        self.url = reverse("cv_detail", kwargs={"pk": self.cv.id})
        self.analysis = Analysis.objects.create(cv=self.cv, job_offer=self.job_offer)

        self.fake_pdf = SimpleUploadedFile(
            "cv.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )

        self.other_candidate = CustomUser.objects.create_user(
            username="john2",
            password="PAAAassword!2@",
            email="example@example2.com",
            phone_number="1234567872",
            role=CustomUser.Role.CANDIDATE
        )

    def test_detail_cv_unauthenticated_returns_401(self):
        # No credentials — should be rejected
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_cv_owner_returns_200(self):
        # CV owner should be able to view their CV
        self.client.force_authenticate(user=self.candidate)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_cv_recruiter_returns_200(self):
        # Recruiter with a linked job offer should have read access
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_cv_stranger_returns_403(self):
        # Unrelated user should be denied access
        self.client.force_authenticate(user=self.other_candidate)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_cv_owner_returns_204(self):
        # Owner should be able to delete their CV
        self.client.force_authenticate(user=self.candidate)
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch('documents.views.extract_text_from_pdf', return_value="mocked text")
    def test_update_cv_owner_returns_200(self, mock_extract):
        # Owner uploading a new file should re-process and return updated CV
        self.client.force_authenticate(user=self.candidate)
        response = self.client.patch(
            self.url, {"file": self.fake_pdf}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
