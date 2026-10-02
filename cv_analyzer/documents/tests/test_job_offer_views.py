from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import JobOffer
from users.models import CustomUser

JOB_DATA = {
    "title": "Junior Python Developer",
    "raw_text": "We are looking for a Python developer.",
    "skills": "Python, Django",
}


class JobOfferCreateAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("create_job_offer")
        self.recruiter = CustomUser.objects.create_user(
            username="kate",
            password="PAAAassword!2@",
            email="recruiter@example.com",
            phone_number="1234567878",
            role=CustomUser.Role.RECRUITER,
        )

    def test_create_job_offer_unauthenticated_returns_401(self):
        # No credentials — should be rejected
        response = self.client.post(self.url, JOB_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_job_offer_authenticated_returns_201(self):
        # Valid payload from authenticated recruiter should create a job offer
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.post(self.url, JOB_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_job_offer_without_title_returns_400(self):
        # title is required — omitting it should fail
        self.client.force_authenticate(user=self.recruiter)
        data = {**JOB_DATA}
        data.pop("title")
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_job_offer_without_raw_text_returns_400(self):
        # raw_text is required — omitting it should fail
        self.client.force_authenticate(user=self.recruiter)
        data = {**JOB_DATA}
        data.pop("raw_text")
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JobOfferListAPITests(APITestCase):

    def setUp(self):
        self.url = reverse("list_job_offers")
        self.recruiter = CustomUser.objects.create_user(
            username="kate",
            password="PAAAassword!2@",
            email="recruiter@example.com",
            phone_number="1234567878",
            role=CustomUser.Role.RECRUITER,
        )
        self.job_offer = JobOffer.objects.create(owner=self.recruiter, **JOB_DATA)

    def test_list_job_offers_authenticated_returns_200(self):
        # Authenticated recruiter should receive their job offers
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_job_offers_unauthenticated_returns_401(self):
        # No credentials — list should be rejected
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JobOfferDetailAPITests(APITestCase):

    def setUp(self):
        self.recruiter = CustomUser.objects.create_user(
            username="kate",
            password="PAAAassword!2@",
            email="recruiter@example.com",
            phone_number="1234567878",
            role=CustomUser.Role.RECRUITER,
        )
        self.other_user = CustomUser.objects.create_user(
            username="john",
            password="PAAAassword!2@",
            email="other@example.com",
            phone_number="9876543210",
            role=CustomUser.Role.CANDIDATE,
        )
        self.job_offer = JobOffer.objects.create(owner=self.recruiter, **JOB_DATA)
        self.url = reverse("job_offer_detail", kwargs={"pk": self.job_offer.id})

    def test_detail_job_offer_unauthenticated_returns_401(self):
        # No credentials — should be rejected
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_job_offer_authenticated_returns_200(self):
        # Any authenticated user can view a job offer
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_job_offer_owner_returns_204(self):
        # Owner should be able to delete their job offer
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_job_offer_stranger_returns_403(self):
        # Non-owner should be denied delete access
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_job_offer_owner_returns_200(self):
        # Owner should be able to update their job offer
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.patch(self.url, {"title": "Senior Dev"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Senior Dev')

    def test_update_job_offer_stranger_returns_403(self):
        # Non-owner should be denied update access
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.url, {"title": "Hacked"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
