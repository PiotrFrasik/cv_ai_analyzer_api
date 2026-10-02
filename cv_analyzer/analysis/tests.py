from rest_framework.test import APITestCase
from analysis.models import Analysis
from documents.models import CV, JobOffer
from django.urls import reverse
from users.models import CustomUser
from rest_framework import status
from unittest.mock import patch

class AnalysisAPITests(APITestCase):
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

        self.cv = CV.objects.create(owner=self.candidate, raw_text="test", status=CV.Status.PROCESSED)
        self.job_offer = JobOffer.objects.create(owner=self.recruiter, 
                                            title="Junior Python Developer",
                                            skills = "Python, Django, DRF, SQL, Git",
                                            raw_text = "We are looking for a motivated Junior Python Developer to build and maintain RESTful APIs using Django and Django REST Framework. You will write clean code, fix bugs, and collaborate with the team while gaining commercial experience through mentoring and code reviews. The ideal candidate has practical Python skills, basic knowledge of SQL and Git, and a strong desire to learn.")

        self.analysis = Analysis.objects.create(cv=self.cv, job_offer=self.job_offer)

        self.url_id = reverse("analysis_detail", kwargs={"pk": self.analysis.id})

        self.other_candidate = CustomUser.objects.create_user(
            username="john2",
            password="PAAAassword!2@",
            email="example@example2.com",
            phone_number="1234567872",
            role=CustomUser.Role.CANDIDATE
        )

        # Second analysis belonging to other_candidate
        other_cv = CV.objects.create(owner=self.other_candidate, raw_text="other", status=CV.Status.PROCESSED)
        self.other_analysis = Analysis.objects.create(cv=other_cv, job_offer=self.job_offer)

        self.url_list = reverse("analysis_list")

        # Completed analysis for candidate using separate CV
        cv_done = CV.objects.create(owner=self.candidate, raw_text="test done", status=CV.Status.PROCESSED)
        self.done_analysis = Analysis.objects.create(
            cv=cv_done,
            job_offer=self.job_offer,
            status=Analysis.Status.DONE,
            match_score=85.50,
            missing_skills="Docker, AWS"
        )
        self.url_done = reverse("analysis_detail", kwargs={"pk": self.done_analysis.id})

    def test_get_analysis_unauthenticated_returns_401(self):
        response = self.client.get(self.url_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_analysis_by_candidate_returns_200(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.get(self.url_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_analysis_by_recruiter_returns_200(self):
        self.client.force_authenticate(user=self.recruiter)
        response = self.client.get(self.url_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_analysis_by_stranger_returns_403(self):
        # User who is neither CV owner nor job offer owner should be denied
        self.client.force_authenticate(user=self.other_candidate)
        response = self.client.get(self.url_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_analysis_unauthenticated_returns_401(self):
        # No credentials — list endpoint should be rejected
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_analysis_candidate_sees_only_own(self):
        # Candidate should only see analyses linked to their own CV
        self.client.force_authenticate(user=self.candidate)
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Serializer returns 'CV' as the owner's username
        cv_owners = [item['CV'] for item in response.data]
        self.assertIn(self.candidate.username, cv_owners)
        self.assertNotIn(self.other_candidate.username, cv_owners)

    def test_analysis_returns_match_score_and_missing_skills(self):
        # Response should contain computed match score and missing skills
        self.client.force_authenticate(user=self.candidate)
        response = self.client.get(self.url_done, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['match_score']), 85.50)
        self.assertEqual(response.data['missing_skills'], "Docker, AWS")
        self.assertEqual(response.data['status'], Analysis.Status.DONE)

    def test_unique_constraint_on_cv_and_job_offer(self):
        # Creating a duplicate Analysis for the same CV and JobOffer should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Analysis.objects.create(cv=self.cv, job_offer=self.job_offer)

    @patch('documents.utils.get_ai_analysis', return_value=(90.0, "None"))
    def test_run_ai_analysis_idempotency_when_already_processing_or_done(self, mock_ai):
        # Task should abort early without invoking AI service if already processing or done
        from analysis.tasks import run_ai_analysis
        self.analysis.status = Analysis.Status.PROCESSING
        self.analysis.save()

        run_ai_analysis(self.analysis.id)

        # AI analysis function should NOT be called again
        mock_ai.assert_not_called()

